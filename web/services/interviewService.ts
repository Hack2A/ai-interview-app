import apiClient from "./apiClient";
import type {
	ATSAnalyzeRequest,
	ATSAnalyzeResponse,
	ChatRequest,
	ChatResponse,
	ChatMessageResponse,
	EndSessionResponse,
	HealthCheckResponse,
	InterviewWSCallbacks,
	SessionInfoResponse,
	StartSessionRequest,
	StartSessionResponse,
	TTSRequest,
	WSClientMessage,
	WSServerMessage,
	WSSetupMessage,
} from "@/types/interviewServiceTypes";

// ═══════════════════════════════════════════════════════════════════════════════
//  REST API
// ═══════════════════════════════════════════════════════════════════════════════

const INTERVIEW_BASE = "interview";

/**
 * GET /api/interview/health/
 * Check whether the ML orchestrator is running.
 */
export async function healthCheck(): Promise<HealthCheckResponse> {
	const { data } = await apiClient.get<HealthCheckResponse>(
		`${INTERVIEW_BASE}/health/`,
	);
	return data;
}

/**
 * POST /api/interview/ats/analyze/
 * Upload resume + JD PDFs for ATS analysis.
 * Requires authentication.
 */
export async function analyzeATS(
	payload: ATSAnalyzeRequest,
): Promise<ATSAnalyzeResponse> {
	const formData = new FormData();
	formData.append("resume", payload.resume);
	formData.append("jd", payload.jd);

	const { data } = await apiClient.post<ATSAnalyzeResponse>(
		`${INTERVIEW_BASE}/ats/analyze/`,
		formData,
		{ headers: { "Content-Type": "multipart/form-data" } },
	);
	return data;
}

/**
 * POST /api/interview/session/start/
 * Start a new interview session.
 * Returns the session ID + opening AI message.
 */
export async function startSession(
	payload: StartSessionRequest = {},
): Promise<StartSessionResponse> {
	const { data } = await apiClient.post<StartSessionResponse>(
		`${INTERVIEW_BASE}/session/start/`,
		payload,
	);
	return data;
}

/**
 * GET /api/interview/session/info/
 * Get the currently active session info (including all messages).
 */
export async function getSessionInfo(): Promise<SessionInfoResponse> {
	const { data } = await apiClient.get<SessionInfoResponse>(
		`${INTERVIEW_BASE}/session/info/`,
	);
	return data;
}

/**
 * POST /api/interview/session/end/
 * End the active session and generate an evaluation report.
 */
export async function endSession(): Promise<EndSessionResponse> {
	const { data } = await apiClient.post<EndSessionResponse>(
		`${INTERVIEW_BASE}/session/end/`,
	);
	return data;
}

/**
 * POST /api/interview/chat/
 * Send a text message (or audio file) to the AI interviewer.
 */
export async function sendChatMessage(
	payload: ChatRequest,
): Promise<ChatResponse> {
	// Use FormData if audio is provided, else plain JSON
	if (payload.audio) {
		const formData = new FormData();
		if (payload.message) formData.append("message", payload.message);
		formData.append("audio", payload.audio);

		const { data } = await apiClient.post<ChatResponse>(
			`${INTERVIEW_BASE}/chat/`,
			formData,
			{ headers: { "Content-Type": "multipart/form-data" } },
		);
		return data;
	}

	const { data } = await apiClient.post<ChatResponse>(
		`${INTERVIEW_BASE}/chat/`,
		{ message: payload.message },
	);
	return data;
}

/**
 * GET /api/interview/chat/history/
 * Get all messages from the active session.
 */
export async function getChatHistory(): Promise<ChatMessageResponse[]> {
	const { data } = await apiClient.get<ChatMessageResponse[]>(
		`${INTERVIEW_BASE}/chat/history/`,
	);
	return data;
}

/**
 * POST /api/interview/tts/
 * Convert text to speech, returns a WAV audio Blob.
 */
export async function textToSpeech(payload: TTSRequest): Promise<Blob> {
	const { data } = await apiClient.post(`${INTERVIEW_BASE}/tts/`, payload, {
		responseType: "blob",
	});
	return data;
}

// ═══════════════════════════════════════════════════════════════════════════════
//  WEBSOCKET — Real-time Interview
// ═══════════════════════════════════════════════════════════════════════════════

const WS_URL =
	process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/interview/";

/**
 * Managed WebSocket connection for the real-time interview pipeline.
 *
 * Usage:
 * ```ts
 * const ws = new InterviewWebSocket({
 *   onConnected: (msg) => console.log("Connected:", msg.session_id),
 *   onStreamChunk: (chunk) => appendToUI(chunk),
 *   onReport: (msg) => showReport(msg.data),
 *   onError: (err) => toast.error(err),
 * });
 *
 * ws.connect();
 * ws.sendSetup({ resume: "...", jd: "...", difficulty: "Medium" });
 * ws.sendAnswer("My answer to the question...");
 * ws.sendEnd();
 * ws.disconnect();
 * ```
 */
export class InterviewWebSocket {
	private ws: WebSocket | null = null;
	private callbacks: InterviewWSCallbacks;
	private url: string;

	constructor(callbacks: InterviewWSCallbacks, url: string = WS_URL) {
		this.callbacks = callbacks;
		this.url = url;
	}

	/** Open the WebSocket connection with optional auth token. */
	connect(token?: string) {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			console.warn("InterviewWebSocket: already connected");
			return;
		}

		// Append token as query param for Django Channels JWT middleware
		let wsUrl = this.url;
		const authToken = token || InterviewWebSocket.getTokenFromCookie();
		if (authToken) {
			const separator = wsUrl.includes("?") ? "&" : "?";
			wsUrl = `${wsUrl}${separator}token=${authToken}`;
		}

		this.ws = new WebSocket(wsUrl);

		this.ws.onopen = () => {
			console.log("🟢 Interview WS connected");
		};

		this.ws.onmessage = (event: MessageEvent) => {
			try {
				const msg: WSServerMessage = JSON.parse(event.data);
				this._dispatch(msg);
			} catch {
				console.error("Failed to parse WS message:", event.data);
			}
		};

		this.ws.onerror = (err) => {
			console.error("🔴 Interview WS error:", err);
			this.callbacks.onError?.("WebSocket connection error");
		};

		this.ws.onclose = (event) => {
			console.log(`🔌 Interview WS closed (code=${event.code})`);
			this.callbacks.onClose?.(event.code);
			this.ws = null;
		};
	}

	/** Extract JWT token from the 'token' cookie. */
	static getTokenFromCookie(): string | null {
		if (typeof document === "undefined") return null;
		const match = document.cookie
			.split("; ")
			.find((row) => row.startsWith("token="));
		return match?.split("=")[1] ?? null;
	}

	/** Gracefully close the WebSocket. */
	disconnect() {
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
	}

	/** Returns true when the WS is connected and open. */
	get isConnected(): boolean {
		return this.ws?.readyState === WebSocket.OPEN;
	}

	// ── Send helpers ─────────────────────────────────────────────────────────

	/** Send setup message to start the interview pipeline. */
	sendSetup(setup: Omit<WSSetupMessage, "type">) {
		this._send({ type: "setup", ...setup });
	}

	/** Send a text answer to the AI interviewer. */
	sendAnswer(text: string) {
		this._send({ type: "answer", text });
	}

	/** Send raw audio bytes (binary frame) for STT → answer pipeline. */
	sendAudio(audioData: Blob | ArrayBuffer) {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
			console.error("Cannot send audio: WS not connected");
			return;
		}
		this.ws.send(audioData);
	}

	/** End the interview and request the evaluation report. */
	sendEnd() {
		this._send({ type: "end" });
	}

	// ── Internals ────────────────────────────────────────────────────────────

	private _send(msg: WSClientMessage) {
		if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
			console.error("Cannot send: WS not connected");
			return;
		}
		this.ws.send(JSON.stringify(msg));
	}

	private _dispatch(msg: WSServerMessage) {
		switch (msg.type) {
			case "connected":
				this.callbacks.onConnected?.(msg);
				break;
			case "status":
				this.callbacks.onStatus?.(msg);
				break;
			case "ats_result":
				this.callbacks.onATSResult?.(msg);
				break;
			case "start":
			case "question":
				this.callbacks.onQuestion?.(msg);
				break;
			case "stream_start":
				this.callbacks.onStreamStart?.();
				break;
			case "stream_chunk":
				this.callbacks.onStreamChunk?.(msg.text);
				break;
			case "stream_end":
				this.callbacks.onStreamEnd?.(msg.text, msg.toxicity, msg.audio_url);
				break;
			case "response":
				this.callbacks.onResponse?.(msg.text);
				break;
			case "transcription":
				this.callbacks.onTranscription?.(msg.text);
				break;
			case "report":
				this.callbacks.onReport?.(msg);
				break;
			case "error":
				this.callbacks.onError?.(msg.message);
				break;
			default:
				console.warn(
					"Unknown WS message type:",
					(msg as { type: string }).type,
				);
		}
	}
}
