export type ResumeMode = "new" | "existing";
export type InterviewType = "generic" | "curated";
export type Difficulty = "easy" | "medium" | "difficult";
export type DeviceStatus = "idle" | "checking" | "ready" | "blocked";

export type InterviewFormData = {
    resumeMode: ResumeMode;
    existingResumeId: string;
    newResume: FileList | null;
    interviewType: InterviewType;
    jobDescription: string;
    difficulty: Difficulty;
    aiProctoring: boolean;
    cameraChecked: boolean;
    microphoneChecked: boolean;
};

export type BackendInterviewPayload = {
    resumeMode: ResumeMode;
    existingResumeId: string | null;
    newResumeFileName: string | null;
    interviewType: InterviewType;
    jobDescription: string | null;
    difficulty: Difficulty;
    aiProctoring: boolean;
    cameraChecked: boolean;
    microphoneChecked: boolean;
};

export const STEP_TITLES = ["Resume", "Interview Type", "Difficulty", "Preview"] as const;

export function getDeviceStatusText(status: DeviceStatus, readyText: string) {
    if (status === "checking") {
        return "Checking...";
    }

    if (status === "ready") {
        return readyText;
    }

    if (status === "blocked") {
        return "Permission denied or device unavailable";
    }

    return "Not checked";
}
