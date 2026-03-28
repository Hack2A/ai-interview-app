"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useNavbar } from "../../NavbarContext";
import InterviewHeader from "@/components/interview/liveInterview/InterviewHeader";
import VideoArea from "@/components/interview/liveInterview/VideoArea";
import ControlBar from "@/components/interview/liveInterview/ControlBar";
import TranscriptPanel from "@/components/interview/liveInterview/TranscriptPanel";
import SettingsModal from "@/components/interview/liveInterview/SettingsModal";
import DisconnectModal from "@/components/interview/liveInterview/DisconnectModal";
import {
    MediaDeviceOption,
    TranscriptEntry,
} from "@/types/LiveInterviewTypes";

/* ── Mock data (replace with real service integration later) ── */

const MOCK_CAMERAS: MediaDeviceOption[] = [
    { deviceId: "cam-1", label: "FaceTime HD Camera", kind: "videoinput" },
    { deviceId: "cam-2", label: "USB Webcam", kind: "videoinput" },
];

const MOCK_MICS: MediaDeviceOption[] = [
    { deviceId: "mic-1", label: "Built-in Microphone", kind: "audioinput" },
    { deviceId: "mic-2", label: "AirPods Pro", kind: "audioinput" },
];

const MOCK_SPEAKERS: MediaDeviceOption[] = [
    { deviceId: "spk-1", label: "Built-in Speakers", kind: "audiooutput" },
    { deviceId: "spk-2", label: "AirPods Pro", kind: "audiooutput" },
];

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

    // UI state
    const [isMuted, setIsMuted] = useState(false);
    const [isVideoOff, setIsVideoOff] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isDisconnectOpen, setIsDisconnectOpen] = useState(false);

    // Device selections
    const [selectedCamera, setSelectedCamera] = useState(
        MOCK_CAMERAS[0].deviceId
    );
    const [selectedMicrophone, setSelectedMicrophone] = useState(
        MOCK_MICS[0].deviceId
    );
    const [selectedSpeaker, setSelectedSpeaker] = useState(
        MOCK_SPEAKERS[0].deviceId
    );

    // Hide navbar for full-screen interview experience
    useEffect(() => {
        setShowNavbar(false);
        return () => setShowNavbar(true);
    }, [setShowNavbar]);

    const handleDisconnectConfirm = () => {
        setIsDisconnectOpen(false);
        router.push("/home");
    };

    return (
        <div className="flex flex-col h-screen bg-slate-50">
            {/* Header */}
            <InterviewHeader
                title="Interview"
                candidateName="Jane Cooper"
                status="in-progress"
            />

            {/* Main content area */}
            <div className="flex flex-1 min-h-0 gap-3 p-3">
                {/* Left column: Video + Controls */}
                <div className="flex flex-col flex-1 min-w-0 gap-0">
                    <VideoArea
                        isVideoOff={isVideoOff}
                        isMuted={isMuted}
                        userName="Alex"
                    />
                    <ControlBar
                        isMuted={isMuted}
                        isVideoOff={isVideoOff}
                        onToggleMute={() => setIsMuted((prev) => !prev)}
                        onToggleVideo={() => setIsVideoOff((prev) => !prev)}
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
                cameras={MOCK_CAMERAS}
                microphones={MOCK_MICS}
                speakers={MOCK_SPEAKERS}
                selectedCamera={selectedCamera}
                selectedMicrophone={selectedMicrophone}
                selectedSpeaker={selectedSpeaker}
                onCameraChange={setSelectedCamera}
                onMicrophoneChange={setSelectedMicrophone}
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