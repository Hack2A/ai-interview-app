"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useNavbar } from "../../NavbarContext";
import { useControlbar } from "@/hooks/controlbarHooks";
import InterviewHeader from "@/components/interview/liveInterview/InterviewHeader";
import VideoArea from "@/components/interview/liveInterview/VideoArea";
import ControlBar from "@/components/interview/liveInterview/ControlBar";
import TranscriptPanel from "@/components/interview/liveInterview/TranscriptPanel";
import SettingsModal from "@/components/interview/liveInterview/SettingsModal";
import DisconnectModal from "@/components/interview/liveInterview/DisconnectModal";
import { TranscriptEntry } from "@/types/LiveInterviewTypes";
import { useRealtimeStream } from "@/hooks/useRealtimeStream";

const MOCK_TRANSCRIPT: TranscriptEntry[] = [
	{
		id: "1",
		speaker: "Interviewer",
		text: "Welcome! Thanks for joining us today. Could you start by telling us a little about yourself?",
		timestamp: "00:00:12",
	},
	{
		id: "2",
		speaker: "You",
		text: "Sure! I'm a full-stack developer with 3 years of experience working primarily with React and Node.js.",
		timestamp: "00:00:28",
	},
	{
		id: "3",
		speaker: "Interviewer",
		text: "That's great. Can you walk us through a challenging project you've worked on recently?",
		timestamp: "00:00:45",
	},
	{
		id: "4",
		speaker: "You",
		text: "Absolutely. I recently led the migration of our legacy monolith to a microservices architecture using Docker and Kubernetes.",
		timestamp: "00:01:02",
	},
	{
		id: "5",
		speaker: "Interviewer",
		text: "Interesting! What were the biggest challenges you faced during that migration?",
		timestamp: "00:01:20",
	},
];

/* ─────────────────────────────────────────────────────────── */

export default function LiveInterview() {
	const { setShowNavbar } = useNavbar();
	const router = useRouter();

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

	const { startStreaming, stopStreaming, isStreaming } = useRealtimeStream(
		stream,
		{ autoStart: true },
	);

	// Hide navbar for full-screen interview experience
	useEffect(() => {
		setShowNavbar(false);
		return () => setShowNavbar(true);
	}, [setShowNavbar]);

	const handleDisconnectConfirm = () => {
		setIsDisconnectOpen(false);
		stopStreaming();
		router.push("/home");
	};

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

				{/* Right column: Transcript panel */}
				<TranscriptPanel entries={MOCK_TRANSCRIPT} />
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
