export type MediaDeviceOption = {
    deviceId: string;
    label: string;
    kind: "audioinput" | "audiooutput" | "videoinput";
};

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

export type VideoAreaProps = {
    isVideoOff: boolean;
    isMuted: boolean;
    userName?: string;
};

export type ControlBarProps = {
    isMuted: boolean;
    isVideoOff: boolean;
    onToggleMute: () => void;
    onToggleVideo: () => void;
    onOpenSettings: () => void;
    onDisconnect: () => void;
};

export type SettingsModalProps = {
    isOpen: boolean;
    onClose: () => void;
    cameras: MediaDeviceOption[];
    microphones: MediaDeviceOption[];
    speakers: MediaDeviceOption[];
    selectedCamera: string;
    selectedMicrophone: string;
    selectedSpeaker: string;
    onCameraChange: (deviceId: string) => void;
    onMicrophoneChange: (deviceId: string) => void;
    onSpeakerChange: (deviceId: string) => void;
};

export type TranscriptPanelProps = {
    entries: TranscriptEntry[];
    activeTab: TranscriptTab;
    onTabChange: (tab: TranscriptTab) => void;
};
