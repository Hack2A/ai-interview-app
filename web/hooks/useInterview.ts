"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
	InterviewWebSocket,
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
	isAISpeaking: boolean;       // true while AI audio is playing
	isUserSpeaking: boolean;     // true while STT is transcribing user audio
	error: string | null;
	report: Record<string, unknown> | null;
	atsResult: Record<string, unknown> | null;
	sessionId: string | null;
	wsConnected: boolean;         // live WS connection state for debug overlay
	audioSentCount: number;       // how many audio blobs sent (for debug overlay)
	audioUnlocked: boolean;       // whether audio playback has been unlocked
	sendAnswer: (text: string) => void;
	sendAudio: (data: Blob | ArrayBuffer) => void;
	endInterview: () => void;
	unlockAudio: () => void;      // call on user gesture to unlock autoplay
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

export function useInterview(speakerDeviceId?: string): UseInterviewReturn {
	const [phase, setPhase] = useState<InterviewPhase>("loading");
	const [statusMessage, setStatusMessage] = useState("Initializing…");
	const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
	const [streamingText, setStreamingText] = useState("");
	const [isAITyping, setIsAITyping] = useState(false);
	const [isAISpeaking, setIsAISpeaking] = useState(false);
	const [isUserSpeaking, setIsUserSpeaking] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [report, setReport] = useState<Record<string, unknown> | null>(null);
	const [atsResult, setAtsResult] = useState<Record<string, unknown> | null>(null);
	const [sessionId, setSessionId] = useState<string | null>(null);
	const [wsConnected, setWsConnected] = useState(false);
	const [audioSentCount, setAudioSentCount] = useState(0);

	const wsRef = useRef<InterviewWebSocket | null>(null);
	const startTimeRef = useRef<number>(Date.now());
	const streamBufferRef = useRef("");
	const audioQueueRef = useRef<HTMLAudioElement | null>(null);
	const [audioUnlocked, setAudioUnlocked] = useState(false);
	const speakerIdRef = useRef(speakerDeviceId);

	// Keep phase accessible in WS callbacks without stale closures
	const phaseRef = useRef<InterviewPhase>("loading");
	useEffect(() => {
		phaseRef.current = phase;
	}, [phase]);

	// Keep speaker device ref in sync
	useEffect(() => {
		speakerIdRef.current = speakerDeviceId;
	}, [speakerDeviceId]);

	// ── Audio unlock (call on any user gesture to satisfy autoplay policy) ──

	const unlockAudio = useCallback(() => {
		if (audioUnlocked) return;
		// Play a silent audio buffer to unlock the browser's autoplay gate
		try {
			const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
			const buffer = ctx.createBuffer(1, 1, 22050);
			const source = ctx.createBufferSource();
			source.buffer = buffer;
			source.connect(ctx.destination);
			source.start(0);
			ctx.close().catch(() => {});
			setAudioUnlocked(true);
			console.log("🔊 Audio playback unlocked via user gesture.");
		} catch {
			// Silently ignore — worst case audio.play() will try anyway
		}
	}, [audioUnlocked]);

	// ── Audio playback ─────────────────────────────────────────────────────

	const playAudioFromUrl = useCallback(async (audioUrl: string) => {
		if (!audioUrl) return;
		try {
			// Build the full URL — strip trailing /api/ to get the backend root
			const backendUrl =
				(process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/")
					.replace(/\/api\/?$/, "");

			// audioUrl may be absolute or relative (e.g. /media/audio/…)
			const fullUrl = audioUrl.startsWith("http") ? audioUrl : `${backendUrl}${audioUrl}`;
			console.log("🔊 Playing AI audio:", fullUrl);

			const audio = new Audio(fullUrl);
			audio.volume = 1.0;

			// Route to the selected speaker device if supported
			if (speakerIdRef.current && typeof (audio as any).setSinkId === "function") {
				try {
					await (audio as any).setSinkId(speakerIdRef.current);
					console.log("🔊 Audio routed to device:", speakerIdRef.current);
				} catch (err) {
					console.warn("🔊 setSinkId failed (will use default output):", err);
				}
			}

			audio.onplay = () => setIsAISpeaking(true);
			audio.onended = () => setIsAISpeaking(false);
			audio.onerror = (e) => {
				console.error("🔊 Audio play error:", e, fullUrl);
				setIsAISpeaking(false);
			};

			const doPlay = async (el: HTMLAudioElement) => {
				try {
					await el.play();
				} catch (err: any) {
					if (err?.name === "NotAllowedError") {
						console.warn(
							"🔊 Autoplay blocked — waiting for user interaction to resume audio.",
						);
						// Retry once on the next user click/tap
						const resumeOnGesture = () => {
							el.play().catch(console.error);
							setAudioUnlocked(true);
							document.removeEventListener("click", resumeOnGesture);
							document.removeEventListener("keydown", resumeOnGesture);
						};
						document.addEventListener("click", resumeOnGesture, { once: true });
						document.addEventListener("keydown", resumeOnGesture, { once: true });
					} else {
						console.error("🔊 Audio play failed:", err);
						setIsAISpeaking(false);
					}
				}
			};

			if (audioQueueRef.current && !audioQueueRef.current.ended) {
				// Queue after the current clip finishes
				audioQueueRef.current.onended = () => {
					audioQueueRef.current = audio;
					doPlay(audio);
				};
			} else {
				audioQueueRef.current = audio;
				doPlay(audio);
			}
		} catch (err) {
			console.warn("🔊 Audio playback setup failed:", err);
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
		setWsConnected(false);
		setAudioSentCount(0);

		const ws = new InterviewWebSocket({
			onConnected: (msg) => {
				if (disposed) return;
				setSessionId(msg.session_id);
				setPhase("setting-up");
				setWsConnected(true);
				setStatusMessage("Connected. Setting up your interview…");
				console.log("✅ WS connected, session:", msg.session_id);

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
				console.log("📡 WS status:", msg.message);
			},

			onATSResult: (msg) => {
				if (disposed) return;
				setStatusMessage("ATS analysis complete. Preparing questions…");
				setAtsResult(msg.data);
				console.log("📊 ATS Result:", msg.data);
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
				console.log("❓ Question received:", msg.text.substring(0, 80));

				if (msg.audio_url) {
					console.log("🔊 Question audio_url:", msg.audio_url);
					playAudioFromUrl(msg.audio_url);
				} else {
					console.warn("🔊 No audio_url in question message");
				}
			},

			onStreamStart: () => {
				setIsAITyping(true);
				setStreamingText("");
				streamBufferRef.current = "";
				console.log("🤖 AI stream started");
			},

			onStreamChunk: (chunk) => {
				streamBufferRef.current += chunk;
				setStreamingText(streamBufferRef.current);
			},

			onStreamEnd: (fullText, toxicity, audioUrl) => {
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
				console.log("🤖 AI stream end. audio_url:", audioUrl ?? "none");

				if (audioUrl) {
					playAudioFromUrl(audioUrl);
				} else {
					console.warn("🔊 No audio_url in stream_end — AI voice won't play");
				}
			},

			onResponse: () => {
				// Duplicate of stream_end — already handled there
			},

			onTranscription: (text) => {
				setIsUserSpeaking(false); // STT done
				const entry: TranscriptEntry = {
					id: nextId(),
					speaker: "You",
					text,
					timestamp: formatTimestamp(startTimeRef.current),
				};
				setTranscript((prev) => [...prev, entry]);
				console.log("📝 Transcription received:", text.substring(0, 80));
			},

			onReport: (msg: WSReportMessage) => {
				setReport(msg.data);
				setPhase("completed");
				setStatusMessage("Interview complete.");
			},

			onError: (message) => {
				if (disposed) return;
				console.error("❌ WS Error:", message);
				const current = phaseRef.current;
				if (current === "loading" || current === "setting-up") {
					setError(message);
					setPhase("error");
				}
			},

			onClose: (code) => {
				if (disposed) return;
				setWsConnected(false);
				console.log("🔌 WS closed, code:", code);
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

	// ── Public actions ───────────────────────────────────────────────

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
		if (!wsRef.current?.isConnected) {
			console.warn("⚠️ sendAudio: WS not connected, dropping audio blob");
			return;
		}
		// Show user is speaking while audio is in-flight
		setIsUserSpeaking(true);
		setAudioSentCount((n) => n + 1);
		const size = data instanceof Blob ? data.size : (data as ArrayBuffer).byteLength;
		console.log(`🎤 Sending audio blob #${audioSentCount + 1}: ${size} bytes`);
		wsRef.current.sendAudio(data);
	}, [audioSentCount]);

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
		isAISpeaking,
		isUserSpeaking,
		error,
		report,
		atsResult,
		sessionId,
		wsConnected,
		audioSentCount,
		audioUnlocked,
		sendAnswer,
		sendAudio,
		endInterview,
		unlockAudio,
	};
}
