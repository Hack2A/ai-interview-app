"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useNavbar } from "../../NavbarContext";
import { useControlbar } from "@/hooks/controlbarHooks";
import { useInterview } from "@/hooks/useInterview";
import { useRealtimeStream } from "@/hooks/useRealtimeStream";
import InterviewHeader from "@/components/interview/liveInterview/InterviewHeader";
import VideoArea from "@/components/interview/liveInterview/VideoArea";
import ControlBar from "@/components/interview/liveInterview/ControlBar";
import TranscriptPanel from "@/components/interview/liveInterview/TranscriptPanel";
import SettingsModal from "@/components/interview/liveInterview/SettingsModal";
import DisconnectModal from "@/components/interview/liveInterview/DisconnectModal";
import InterviewReport from "@/components/interview/InterviewReport";
import type { InterviewReportData } from "@/components/interview/InterviewReport";
import { Loader2, AlertCircle, ArrowLeft, CheckCircle2, Bug } from "lucide-react";

/* ─────────────────────────────────────────────────────────── */

export default function LiveInterview() {
	const { setShowNavbar } = useNavbar();
	const router = useRouter();
	const [showDebug, setShowDebug] = useState(false);

	// ── Camera / mic / controls (initialized first for selectedSpeaker) ──
	const {
		isMuted,
		isVideoOff,
		isSettingsOpen,
		isDisconnectOpen,
		stream,
		cameras,
		mics,
		speakers,
		selectedCamera,
		selectedMicrophone,
		selectedSpeaker,
		setIsSettingsOpen,
		setIsDisconnectOpen,
		setSelectedSpeaker,
		handleToggleMute,
		handleToggleVideo,
		handleCameraChange,
		handleMicChange,
		stopAllTracks,
	} = useControlbar();

	// ── Interview WebSocket lifecycle ────────────────────────────────
	const {
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
		sendAudio,
		endInterview,
		unlockAudio,
	} = useInterview(selectedSpeaker);

	// ── Audio streaming (sends mic chunks to WS) ────────────────────
	const isUserTurn = phase === "active" && !isAITyping && !isAISpeaking;
	const { stopStreaming, isStreaming, isSpeaking, manualSend } = useRealtimeStream(
		// Only start streaming audio once the interview is active
		phase === "active" ? stream : null,
		sendAudio,
		{ autoStart: true, enabled: isUserTurn },
	);

	// Unlock audio on first click/interaction (browser autoplay policy)
	useEffect(() => {
		if (audioUnlocked) return;
		const handler = () => unlockAudio();
		document.addEventListener("click", handler, { once: true });
		return () => document.removeEventListener("click", handler);
	}, [audioUnlocked, unlockAudio]);

	// Hide navbar for full-screen interview experience
	useEffect(() => {
		setShowNavbar(false);
		return () => setShowNavbar(true);
	}, [setShowNavbar]);

	// Release camera/mic hardware when interview ends
	useEffect(() => {
		if (phase === "ending" || phase === "completed" || phase === "error") {
			stopAllTracks();
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [phase]);

	// ── Disconnect handler ──────────────────────────────────────────
	const handleDisconnectConfirm = () => {
		setIsDisconnectOpen(false);
		stopStreaming();
		stopAllTracks();
		endInterview();
	};

	// Redirect home after report is viewed
	const handleFinish = () => {
		router.push("/home");
	};

	// ── Loading / Setting-up screen ─────────────────────────────────
	if (phase === "loading" || phase === "setting-up") {
		return (
			<div className="flex flex-col items-center justify-center h-screen bg-slate-50">
				<div className="flex flex-col items-center gap-6 max-w-md text-center px-6">
					{/* Animated spinner */}
					<div className="relative">
						<div className="absolute inset-0 rounded-full bg-blue-400/20 animate-ping" />
						<div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-blue-50 border-2 border-blue-200">
							<Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
						</div>
					</div>

					<div>
						<h1 className="text-2xl font-bold text-slate-900 mb-2">
							Starting your interview
						</h1>
						<p className="text-sm text-slate-500 leading-relaxed">
							{statusMessage}
						</p>
					</div>

					{/* Step indicators */}
					<div className="w-full space-y-2">
						{[
							{ label: "Connecting to server", done: phase !== "loading" },
							{ label: "Setting up AI engine", done: false },
							{ label: "Preparing questions", done: false },
						].map((step, i) => (
							<div
								key={i}
								className={`flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm transition-all ${step.done
									? "bg-emerald-50 text-emerald-700"
									: i === 0 && phase === "loading"
										? "bg-blue-50 text-blue-700"
										: phase === "setting-up" && i === 1
											? "bg-blue-50 text-blue-700"
											: "bg-slate-100 text-slate-400"
									}`}
							>
								{step.done ? (
									<CheckCircle2 className="w-4 h-4 text-emerald-500" />
								) : (
									<Loader2 className="w-4 h-4 animate-spin opacity-60" />
								)}
								<span className="font-medium">{step.label}</span>
							</div>
						))}
					</div>

					{/* ATS Result Summary */}
					{atsResult && (
						<div className="mt-4 w-full text-left rounded-xl border border-indigo-100 bg-indigo-50 p-4 shadow-sm animate-in fade-in slide-in-from-bottom-4">
							<h3 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
								<CheckCircle2 className="w-5 h-5" />
								Internal Resume Analysis
							</h3>

							<div className="grid grid-cols-2 gap-3 mb-4">
								<div className="bg-white rounded-lg p-3 border border-indigo-100 shadow-sm">
									<p className="text-xs text-slate-500 font-medium">Algorithmic Match</p>
									<p className="text-xl font-bold text-indigo-700">{(atsResult as any).algorithmic_score?.toFixed(1) || 0}%</p>
								</div>
								<div className="bg-white rounded-lg p-3 border border-indigo-100 shadow-sm">
									<p className="text-xs text-slate-500 font-medium">AI Assessment</p>
									<p className="text-xl font-bold text-indigo-700">{(atsResult as any).llm_score?.toFixed(1) || 0}%</p>
								</div>
							</div>

							{(atsResult as any).missing_skills?.length > 0 && (
								<div>
									<p className="text-xs font-semibold text-indigo-800 mb-1">Missing Skills Identified:</p>
									<div className="flex flex-wrap gap-1.5">
										{(atsResult as any).missing_skills.slice(0, 5).map((skill: string, i: number) => (
											<span key={i} className="px-2 py-1 bg-white border border-indigo-200 text-indigo-700 text-xs rounded-md">
												{skill}
											</span>
										))}
									</div>
								</div>
							)}
						</div>
					)}
				</div>
			</div>
		);
	}

	// ── Error screen ────────────────────────────────────────────────
	if (phase === "error") {
		return (
			<div className="flex flex-col items-center justify-center h-screen bg-slate-50">
				<div className="flex flex-col items-center gap-5 max-w-md text-center px-6">
					<div className="flex items-center justify-center w-16 h-16 rounded-full bg-red-50 border-2 border-red-200">
						<AlertCircle className="w-7 h-7 text-red-500" />
					</div>
					<div>
						<h1 className="text-2xl font-bold text-slate-900 mb-2">
							Something went wrong
						</h1>
						<p className="text-sm text-slate-600 leading-relaxed">
							{error || "An unexpected error occurred while setting up the interview."}
						</p>
					</div>
					<div className="flex gap-3">
						<button
							onClick={() => router.push("/interview/new")}
							className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
						>
							<ArrowLeft className="w-4 h-4" />
							Set Up Again
						</button>
						<button
							onClick={() => router.push("/home")}
							className="rounded-xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 transition-colors"
						>
							Go Home
						</button>
					</div>
				</div>
			</div>
		);
	}

	// ── Ending / Report screen ──────────────────────────────────────
	if (phase === "ending") {
		return (
			<div className="flex flex-col items-center justify-center h-screen bg-slate-50">
				<div className="flex flex-col items-center gap-5 max-w-md text-center px-6">
					<div className="relative">
						<div className="absolute inset-0 rounded-full bg-amber-400/20 animate-ping" />
						<div className="relative flex items-center justify-center w-20 h-20 rounded-full bg-amber-50 border-2 border-amber-200">
							<Loader2 className="w-8 h-8 text-amber-600 animate-spin" />
						</div>
					</div>
					<div>
						<h1 className="text-2xl font-bold text-slate-900 mb-2">
							Wrapping up…
						</h1>
						<p className="text-sm text-slate-500 leading-relaxed">
							{statusMessage}
						</p>
					</div>
				</div>
			</div>
		);
	}

	if (phase === "completed") {
		return report ? (
			<div className="min-h-screen bg-slate-50 overflow-y-auto">
				<InterviewReport
					report={report as unknown as InterviewReportData}
					title="Interview Report"
					showHomeButton
					onFinish={handleFinish}
					onRetry={() => router.push("/interview/new")}
				/>
			</div>
		) : (
			<div className="flex flex-col items-center justify-center h-screen bg-slate-50">
				<div className="flex flex-col items-center gap-5 max-w-md text-center px-6">
					<div className="flex items-center justify-center w-16 h-16 rounded-full bg-red-50 border-2 border-red-200">
						<AlertCircle className="w-7 h-7 text-red-500" />
					</div>
					<h1 className="text-2xl font-bold text-slate-900">Report Unavailable</h1>
					<p className="text-sm text-slate-500">Failed to load report data.</p>
					<button
						onClick={handleFinish}
						className="rounded-xl bg-slate-900 px-6 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 transition-colors"
					>
						Go Home
					</button>
				</div>
			</div>
		);
	}

	// ── Active interview UI ─────────────────────────────────────────
	return (
		<div className="flex flex-col h-screen bg-slate-50">
			{/* Header */}
			<InterviewHeader
				title="Interview"
				candidateName="Friendly Beaver"
				status="in-progress"
			/>

			{/* Main content area */}
			<div className="flex flex-1 min-h-0 gap-3 p-3">
				{/* Left column: Video + Controls */}
				<div className="flex flex-col flex-1 min-w-0 gap-0">
					<VideoArea
						stream={stream}
						isVideoOff={isVideoOff}
						isMuted={isMuted}
						userName="Akshat Pratyush"
						isAISpeaking={isAISpeaking}
						isUserSpeaking={isUserSpeaking || isSpeaking}
					/>
					<ControlBar
						isMuted={isMuted}
						isVideoOff={isVideoOff}
						isSpeaking={isSpeaking}
						isRecording={isStreaming}
						onToggleMute={handleToggleMute}
						onToggleVideo={handleToggleVideo}
						onOpenSettings={() => setIsSettingsOpen(true)}
						onDisconnect={() => setIsDisconnectOpen(true)}
						onFinishSpeaking={manualSend}
					/>
				</div>

				{/* Right column: Live transcript panel */}
				<TranscriptPanel
					entries={transcript}
					streamingText={streamingText}
					isAITyping={isAITyping}
					isAISpeaking={isAISpeaking}
					isUserSpeaking={isUserSpeaking || isSpeaking}
				/>
			</div>

			{/* ── Debug overlay (toggle with Bug icon) ── */}
			<button
				onClick={() => setShowDebug((v) => !v)}
				className="fixed bottom-4 left-4 z-50 flex items-center justify-center w-8 h-8 rounded-full bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
				title="Toggle debug overlay"
			>
				<Bug className="w-4 h-4" />
			</button>

			{showDebug && (
				<div className="fixed bottom-14 left-4 z-50 w-72 rounded-xl bg-slate-900/95 backdrop-blur-sm border border-slate-700 p-4 text-xs font-mono text-slate-300 space-y-1.5 shadow-2xl">
					<p className="text-slate-400 font-semibold text-[10px] uppercase tracking-wider mb-2">Debug Panel</p>
					<div className="flex justify-between">
						<span>WS connected</span>
						<span className={wsConnected ? "text-emerald-400" : "text-red-400"}>{wsConnected ? "✓ yes" : "✗ no"}</span>
					</div>
					<div className="flex justify-between">
						<span>Phase</span>
						<span className="text-amber-300">{phase}</span>
					</div>
					<div className="flex justify-between">
						<span>Mic streaming</span>
						<span className={isStreaming ? "text-emerald-400" : "text-slate-500"}>{isStreaming ? "✓ active" : "idle"}</span>
					</div>
					<div className="flex justify-between">
						<span>VAD speaking</span>
						<span className={isSpeaking ? "text-blue-400" : "text-slate-500"}>{isSpeaking ? "✓ yes" : "no"}</span>
					</div>
					<div className="flex justify-between">
						<span>Audio blobs sent</span>
						<span className="text-blue-300">{audioSentCount}</span>
					</div>
					<div className="flex justify-between">
						<span>AI typing</span>
						<span className={isAITyping ? "text-violet-400" : "text-slate-500"}>{isAITyping ? "✓ yes" : "no"}</span>
					</div>
					<div className="flex justify-between">
						<span>AI speaking</span>
						<span className={isAISpeaking ? "text-violet-400" : "text-slate-500"}>{isAISpeaking ? "✓ yes" : "no"}</span>
					</div>
					<div className="flex justify-between">
						<span>Stream source</span>
						<span className={stream ? "text-emerald-400" : "text-red-400"}>{stream ? `${stream.getTracks().length} track(s)` : "none"}</span>
					</div>
					<div className="flex justify-between">
						<span>Session ID</span>
						<span className="text-slate-400 truncate max-w-[120px]">{sessionId?.slice(0, 12) ?? "—"}</span>
					</div>
					<div className="flex justify-between">
						<span>Transcript entries</span>
						<span className="text-slate-300">{transcript.length}</span>
					</div>
					<p className="text-[9px] text-slate-500 mt-2">Open DevTools console for full logs</p>
				</div>
			)}

			{/* Settings modal */}
			<SettingsModal
				isOpen={isSettingsOpen}
				onClose={() => setIsSettingsOpen(false)}
				cameras={cameras}
				microphones={mics}
				speakers={speakers}
				selectedCamera={selectedCamera}
				selectedMicrophone={selectedMicrophone}
				selectedSpeaker={selectedSpeaker}
				onCameraChange={handleCameraChange}
				onMicrophoneChange={handleMicChange}
				onSpeakerChange={setSelectedSpeaker}
			/>

			{/* Disconnect confirmation */}
			<DisconnectModal
				isOpen={isDisconnectOpen}
				onCancel={() => setIsDisconnectOpen(false)}
				onConfirm={handleDisconnectConfirm}
			/>
		</div>
	);
}
