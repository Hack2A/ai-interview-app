"use client";

import { useEffect } from "react";
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
import { Loader2, AlertCircle, ArrowLeft, CheckCircle2 } from "lucide-react";

/* ─────────────────────────────────────────────────────────── */

export default function LiveInterview() {
	const { setShowNavbar } = useNavbar();
	const router = useRouter();

	// ── Interview WebSocket lifecycle ────────────────────────────────
	const {
		phase,
		statusMessage,
		transcript,
		streamingText,
		isAITyping,
		error,
		report,
		sendAudio,
		endInterview,
	} = useInterview();

	// ── Camera / mic / controls ─────────────────────────────────────
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
	} = useControlbar();

	// ── Audio streaming (sends mic chunks to WS) ────────────────────
	const { stopStreaming } = useRealtimeStream(
		// Only start streaming audio once the interview is active
		phase === "active" ? stream : null,
		sendAudio,
		{ autoStart: true },
	);

	// Hide navbar for full-screen interview experience
	useEffect(() => {
		setShowNavbar(false);
		return () => setShowNavbar(true);
	}, [setShowNavbar]);

	// ── Disconnect handler ──────────────────────────────────────────
	const handleDisconnectConfirm = () => {
		setIsDisconnectOpen(false);
		stopStreaming();
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
								className={`flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm transition-all ${
									step.done
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
		return (
			<div className="flex flex-col items-center justify-center h-screen bg-slate-50">
				<div className="flex flex-col items-center gap-5 max-w-lg text-center px-6">
					<div className="flex items-center justify-center w-16 h-16 rounded-full bg-emerald-50 border-2 border-emerald-200">
						<CheckCircle2 className="w-7 h-7 text-emerald-500" />
					</div>
					<div>
						<h1 className="text-2xl font-bold text-slate-900 mb-2">
							Interview Complete!
						</h1>
						<p className="text-sm text-slate-500 leading-relaxed mb-4">
							Your evaluation report has been generated.
						</p>
					</div>

					{report && (
						<div className="w-full rounded-xl border border-slate-200 bg-white p-5 text-left max-h-80 overflow-y-auto">
							<pre className="text-xs text-slate-700 whitespace-pre-wrap font-mono">
								{JSON.stringify(report, null, 2)}
							</pre>
						</div>
					)}

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
					/>
					<ControlBar
						isMuted={isMuted}
						isVideoOff={isVideoOff}
						onToggleMute={handleToggleMute}
						onToggleVideo={handleToggleVideo}
						onOpenSettings={() => setIsSettingsOpen(true)}
						onDisconnect={() => setIsDisconnectOpen(true)}
					/>
				</div>

				{/* Right column: Live transcript panel */}
				<TranscriptPanel
					entries={transcript}
					streamingText={streamingText}
					isAITyping={isAITyping}
				/>
			</div>

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
