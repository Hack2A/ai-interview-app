"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
	InterviewWebSocket,
	textToSpeech,
} from "@/services/interviewService";
import type {
	WSSetupMessage,
	WSReportMessage,
	SessionDifficulty,
	InterviewMode,
	InterviewTypeOption,
} from "@/types/interviewServiceTypes";
import type { TranscriptEntry } from "@/types/LiveInterviewTypes";

// ── Types ────────────────────────────────────────────────────────────────────

export type InterviewPhase =
	| "loading"      // reading config, connecting WS
	| "setting-up"   // WS connected, setup in progress (ATS, loading docs…)
	| "active"       // interview is live (first question received)
	| "ending"       // user clicked disconnect, generating report
	| "completed"    // report received
	| "error";       // something went wrong

export interface InterviewConfig {
	resumeBase64?: string;        // base64 PDF
	jdText?: string;              // plain text JD
	difficulty: SessionDifficulty;
	mode: InterviewMode;
	interviewType: InterviewTypeOption;
	proctoring: boolean;
}

export interface UseInterviewReturn {
	phase: InterviewPhase;
	statusMessage: string;
	transcript: TranscriptEntry[];
	streamingText: string;
	isAITyping: boolean;
	error: string | null;
	report: Record<string, unknown> | null;
	sessionId: string | null;
	sendAnswer: (text: string) => void;
	sendAudio: (data: Blob | ArrayBuffer) => void;
	endInterview: () => void;
}

// ── Constants ────────────────────────────────────────────────────────────────

const SESSION_STORAGE_KEY = "interview_config";

/** Save interview config to sessionStorage (called from /interview/new). */
export function saveInterviewConfig(config: InterviewConfig) {
	sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(config));
}

/** Read interview config from sessionStorage (does NOT remove it). */
function loadInterviewConfig(): InterviewConfig | null {
	const raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
	if (!raw) return null;
	try {
		return JSON.parse(raw) as InterviewConfig;
	} catch {
		return null;
	}
}

// ── Helpers ──────────────────────────────────────────────────────────────────

let transcriptCounter = 0;
function nextId(): string {
	return String(++transcriptCounter);
}

function formatTimestamp(startTime: number): string {
	const elapsed = Math.floor((Date.now() - startTime) / 1000);
	const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
	const ss = String(elapsed % 60).padStart(2, "0");
	return `${mm}:${ss}`;
}

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useInterview(): UseInterviewReturn {
	const [phase, setPhase] = useState<InterviewPhase>("loading");
	const [statusMessage, setStatusMessage] = useState("Initializing…");
	const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
	const [streamingText, setStreamingText] = useState("");
	const [isAITyping, setIsAITyping] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [report, setReport] = useState<Record<string, unknown> | null>(null);
	const [sessionId, setSessionId] = useState<string | null>(null);

	const wsRef = useRef<InterviewWebSocket | null>(null);
	const startTimeRef = useRef<number>(Date.now());
	const streamBufferRef = useRef("");
	const audioQueueRef = useRef<HTMLAudioElement | null>(null);

	// Keep phase accessible in WS callbacks without stale closures
	const phaseRef = useRef<InterviewPhase>("loading");
	useEffect(() => {
		phaseRef.current = phase;
	}, [phase]);

	// ── TTS playback ─────────────────────────────────────────────────────

	const playTTS = useCallback(async (text: string) => {
		try {
			const audioBlob = await textToSpeech({ text });
			const url = URL.createObjectURL(audioBlob);
			const audio = new Audio(url);

			if (audioQueueRef.current && !audioQueueRef.current.ended) {
				audioQueueRef.current.onended = () => {
					audio.play().catch(() => {});
				};
			} else {
				audio.play().catch(() => {});
			}
			audioQueueRef.current = audio;

			audio.onended = () => {
				URL.revokeObjectURL(url);
			};
		} catch (err) {
			console.warn("TTS playback failed:", err);
		}
	}, []);

	// ── Initialize WS on mount ───────────────────────────────────────────

	useEffect(() => {
		// `disposed` is set to true when cleanup runs (React Strict Mode or real unmount).
		// It prevents stale WS callbacks from mutating state after cleanup.
		let disposed = false;

		const config = loadInterviewConfig();
		if (!config) {
			if (!disposed) {
				setError("No interview configuration found. Please go back and set up your interview.");
				setPhase("error");
			}
			return;
		}

		startTimeRef.current = Date.now();
		transcriptCounter = 0;

		// Reset state for fresh connection (needed on Strict Mode remount)
		setPhase("loading");
		setError(null);
		setStatusMessage("Initializing…");

		const ws = new InterviewWebSocket({
			onConnected: (msg) => {
				if (disposed) return;
				setSessionId(msg.session_id);
				setPhase("setting-up");
				setStatusMessage("Connected. Setting up your interview…");

				const setup: Omit<WSSetupMessage, "type"> = {
					difficulty: config.difficulty,
					mode: config.mode,
					interview_type: config.interviewType,
					proctoring: config.proctoring,
				};

				if (config.resumeBase64) {
					setup.resume_pdf = config.resumeBase64;
				}
				if (config.jdText) {
					setup.jd = config.jdText;
				}

				ws.sendSetup(setup);
			},

			onStatus: (msg) => {
				if (disposed) return;
				setStatusMessage(msg.message);
			},

			onATSResult: (msg) => {
				if (disposed) return;
				setStatusMessage("ATS analysis complete. Preparing questions…");
				console.log("ATS Result:", msg.data);
			},

			onQuestion: (msg) => {
				if (disposed) return;
				setPhase("active");
				setStatusMessage("");

				// Safe to clear session config now that setup succeeded
				sessionStorage.removeItem(SESSION_STORAGE_KEY);

				const entry: TranscriptEntry = {
					id: nextId(),
					speaker: "Interviewer",
					text: msg.text,
					timestamp: formatTimestamp(startTimeRef.current),
				};
				setTranscript((prev) => [...prev, entry]);
				playTTS(msg.text);
			},

			onStreamStart: () => {
				setIsAITyping(true);
				setStreamingText("");
				streamBufferRef.current = "";
			},

			onStreamChunk: (chunk) => {
				streamBufferRef.current += chunk;
				setStreamingText(streamBufferRef.current);
			},

			onStreamEnd: (fullText) => {
				setIsAITyping(false);
				setStreamingText("");
				streamBufferRef.current = "";

				const entry: TranscriptEntry = {
					id: nextId(),
					speaker: "Interviewer",
					text: fullText,
					timestamp: formatTimestamp(startTimeRef.current),
				};
				setTranscript((prev) => [...prev, entry]);
				playTTS(fullText);
			},

			onResponse: () => {
				// Duplicate of stream_end — already handled there
			},

			onTranscription: (text) => {
				const entry: TranscriptEntry = {
					id: nextId(),
					speaker: "You",
					text,
					timestamp: formatTimestamp(startTimeRef.current),
				};
				setTranscript((prev) => [...prev, entry]);
			},

			onReport: (msg: WSReportMessage) => {
				setReport(msg.data);
				setPhase("completed");
				setStatusMessage("Interview complete.");
			},

			onError: (message) => {
				if (disposed) return;
				console.error("WS Error:", message);
				const current = phaseRef.current;
				if (current === "loading" || current === "setting-up") {
					setError(message);
					setPhase("error");
				}
			},

			onClose: (code) => {
				if (disposed) return;
				const current = phaseRef.current;
				// Ignore close during completed/error/ending/loading (Strict Mode cleanup)
				if (
					code !== 1000 &&
					current !== "completed" &&
					current !== "error" &&
					current !== "ending" &&
					current !== "loading"
				) {
					setError(`Connection lost (code: ${code}). Please try again.`);
					setPhase("error");
				}
			},
		});

		wsRef.current = ws;
		ws.connect();

		return () => {
			disposed = true;
			ws.disconnect();
			wsRef.current = null;
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	// ── Public actions ───────────────────────────────────────────────────

	const sendAnswer = useCallback((text: string) => {
		if (!wsRef.current?.isConnected) return;

		const entry: TranscriptEntry = {
			id: nextId(),
			speaker: "You",
			text,
			timestamp: formatTimestamp(startTimeRef.current),
		};
		setTranscript((prev) => [...prev, entry]);

		wsRef.current.sendAnswer(text);
	}, []);

	const sendAudio = useCallback((data: Blob | ArrayBuffer) => {
		if (!wsRef.current?.isConnected) return;
		wsRef.current.sendAudio(data);
	}, []);

	const endInterview = useCallback(() => {
		if (!wsRef.current?.isConnected) return;
		setPhase("ending");
		setStatusMessage("Generating evaluation report… (this may take up to 2 minutes)");
		wsRef.current.sendEnd();
	}, []);

	return {
		phase,
		statusMessage,
		transcript,
		streamingText,
		isAITyping,
		error,
		report,
		sessionId,
		sendAnswer,
		sendAudio,
		endInterview,
	};
}
