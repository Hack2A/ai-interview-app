
export type TranscriptEntry = {
    id: string;
    speaker: string;
    text: string;
    timestamp: string;
};

export type InterviewStatus = "in-progress" | "paused" | "completed";

export type TranscriptTab = "transcript" | "scorecard" | "outputs" | "notes";

export type InterviewHeaderProps = {
    title: string;
    candidateName: string;
    status: InterviewStatus;
};

export interface VideoAreaProps {
    isVideoOff: boolean;
    isMuted: boolean;
    userName?: string;
    stream: MediaStream | null;
}

export type ControlBarProps = {
    isMuted: boolean;
    isVideoOff: boolean;
    isSpeaking?: boolean;
    isRecording?: boolean;
    onToggleMute: () => void;
    onToggleVideo: () => void;
    onOpenSettings: () => void;
    onDisconnect: () => void;
    onFinishSpeaking?: () => void;
};

export type SettingsModalProps = {
    isOpen: boolean;
    onClose: () => void;
    cameras: MediaDeviceInfo[];
    microphones: MediaDeviceInfo[];
    speakers: MediaDeviceInfo[];
    selectedCamera?: string;
    selectedMicrophone?: string;
    selectedSpeaker?: string;
    onCameraChange: (deviceId: string) => void;
    onMicrophoneChange: (deviceId: string) => void;
    onSpeakerChange: (deviceId: string) => void;
};

export type TranscriptPanelProps = {
    entries: TranscriptEntry[];
};
