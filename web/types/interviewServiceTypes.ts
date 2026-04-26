// ── Shared Enums / Literals ──────────────────────────────────────────────────

export type SessionDifficulty = "Easy" | "Medium" | "Hard" | "Extreme";
export type SessionStatus = "active" | "completed" | "cancelled";
export type MessageRole = "user" | "ai" | "system";
export type InterviewMode = "generic" | "curated";
export type InterviewTypeOption =
	| "technical"
	| "behavioral"
	| "hr"
	| "combined";

// ── REST API — Request Types ─────────────────────────────────────────────────

/** POST /api/interview/ats/analyze/ — multipart/form-data */
export interface ATSAnalyzeRequest {
	resume: File;
	jd: File;
}

/** POST /api/interview/session/start/ — JSON body */
export interface StartSessionRequest {
	difficulty?: SessionDifficulty;
	enable_proctoring?: boolean;
	resume_text?: string;
	jd_text?: string;
}

/** POST /api/interview/chat/ — multipart/form-data (if audio) or JSON */
export interface ChatRequest {
	message?: string;
	audio?: File;
}

/** POST /api/interview/tts/ — JSON body */
export interface TTSRequest {
	text: string;
}

// ── REST API — Response Types ────────────────────────────────────────────────

export interface HealthCheckResponse {
	[key: string]: unknown; // orchestrator health payload
}

export interface ATSAnalyzeResponse {
	[key: string]: unknown; // ATS scoring result from the ML engine
	error?: string;
}

export interface StartSessionResponse {
	session_id: string;
	difficulty: SessionDifficulty;
	enable_proctoring: boolean;
	opening_message: string;
}

export interface ChatMessageResponse {
	id: number;
	role: MessageRole;
	content: string;
	created_at: string;
}

export interface SessionInfoResponse {
	id: number;
	session_id: string;
	difficulty: SessionDifficulty;
	status: SessionStatus;
	enable_proctoring: boolean;
	ats_algorithmic_score: number | null;
	ats_llm_score: number | null;
	ats_combined_score: number | null;
	evaluation_report: Record<string, unknown> | null;
	created_at: string;
	ended_at: string | null;
	messages: ChatMessageResponse[];
}

export interface ChatResponse {
	user_text: string;
	ai_response: string;
	toxicity: unknown;
	transcription?: string;
}

export interface EndSessionResponse {
	session_id: string;
	status: "completed";
	evaluation_report: Record<string, unknown> | null;
	proctoring_summary?: Record<string, unknown>;
}

// ── WebSocket — Message Types ────────────────────────────────────────────────

/** Messages the CLIENT sends to the WebSocket */
export type WSClientMessage = WSSetupMessage | WSAnswerMessage | WSEndMessage;

export interface WSSetupMessage {
	type: "setup";
	resume?: string;
	jd?: string;
	resume_pdf?: string; // base64-encoded PDF
	jd_pdf?: string; // base64-encoded PDF
	difficulty?: SessionDifficulty;
	mode?: InterviewMode;
	interview_type?: InterviewTypeOption;
	proctoring?: boolean;
}

export interface WSAnswerMessage {
	type: "answer";
	text: string;
}

export interface WSEndMessage {
	type: "end";
}

/** Messages the SERVER sends over WebSocket */
export type WSServerMessage =
	| WSConnectedMessage
	| WSStatusMessage
	| WSATSResultMessage
	| WSStartMessage
	| WSQuestionMessage
	| WSStreamStartMessage
	| WSStreamChunkMessage
	| WSStreamEndMessage
	| WSResponseMessage
	| WSTranscriptMessage
	| WSTranscriptionMessage
	| WSReportMessage
	| WSErrorMessage;

export interface WSConnectedMessage {
	type: "connected";
	session_id: string;
	message: string;
}

export interface WSStatusMessage {
	type: "status";
	message: string;
}

export interface WSATSResultMessage {
	type: "ats_result";
	data: Record<string, unknown>;
}

export interface WSStartMessage {
	type: "start";
	text: string;
	audio_url?: string;
}

export interface WSQuestionMessage {
	type: "question";
	text: string;
	audio_url?: string;
}

export interface WSStreamStartMessage {
	type: "stream_start";
}

export interface WSStreamChunkMessage {
	type: "stream_chunk";
	text: string;
}

export interface WSStreamEndMessage {
	type: "stream_end";
	text: string;
	toxicity?: unknown;
	audio_url?: string;
}

export interface WSResponseMessage {
	type: "response";
	text: string;
}

export interface WSTranscriptMessage {
	type: "transcript";
	text: string;
}

export interface WSTranscriptionMessage {
	type: "transcription";
	text: string;
}

export interface WSReportMessage {
	type: "report";
	data: Record<string, unknown>;
	session_id: string;
	proctoring?: Record<string, unknown>;
}

export interface WSErrorMessage {
	type: "error";
	message: string;
}

// ── WebSocket Event Callback Map ─────────────────────────────────────────────

export interface InterviewWSCallbacks {
	onConnected?: (msg: WSConnectedMessage) => void;
	onStatus?: (msg: WSStatusMessage) => void;
	onATSResult?: (msg: WSATSResultMessage) => void;
	onQuestion?: (msg: WSStartMessage | WSQuestionMessage) => void;
	onStreamStart?: () => void;
	onStreamChunk?: (chunk: string) => void;
	onStreamEnd?: (fullText: string, toxicity?: unknown, audioUrl?: string) => void;
	onResponse?: (text: string) => void;
	onTranscription?: (text: string) => void;
	onReport?: (msg: WSReportMessage) => void;
	onError?: (message: string) => void;
	onClose?: (code: number) => void;
}
