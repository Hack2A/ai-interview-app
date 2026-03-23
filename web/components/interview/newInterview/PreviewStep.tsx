import { RefObject } from "react";
import { UseFormRegister } from "react-hook-form";
import { Camera, Mic, ShieldCheck } from "lucide-react";
import { DeviceStatus, Difficulty, InterviewFormData, InterviewType, ResumeMode, getDeviceStatusText } from "@/types/Interivewtypes";

type PreviewStepProps = {
    register: UseFormRegister<InterviewFormData>;
    cameraStatus: DeviceStatus;
    microphoneStatus: DeviceStatus;
    videoRef: RefObject<HTMLVideoElement | null>;
    handleCameraCheck: () => Promise<void>;
    handleMicrophoneCheck: () => Promise<void>;
    resumeMode: ResumeMode;
    interviewType: InterviewType;
    difficulty: Difficulty;
    aiProctoring: boolean;
};

export default function PreviewStep({
    register,
    cameraStatus,
    microphoneStatus,
    videoRef,
    handleCameraCheck,
    handleMicrophoneCheck,
    resumeMode,
    interviewType,
    difficulty,
    aiProctoring,
}: PreviewStepProps) {
    return (
        <section className="space-y-5">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Preview & Proctoring</h2>
                <p className="text-sm text-slate-600">
                    Toggle AI proctoring, then verify your camera and microphone before submitting.
                </p>
            </div>

            <div className="rounded-xl border border-slate-200 p-4">
                <label className="flex cursor-pointer items-center justify-between">
                    <div className="flex items-center gap-3">
                        <ShieldCheck className="h-5 w-5 text-slate-700" />
                        <div>
                            <p className="font-semibold text-slate-900">Enable AI Proctoring</p>
                            <p className="text-sm text-slate-600">Monitor interview integrity with AI checks.</p>
                        </div>
                    </div>
                    <input type="checkbox" className="h-5 w-5 accent-blue-600" {...register("aiProctoring")} />
                </label>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
                <div className="rounded-xl border border-slate-200 p-4">
                    <div className="mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2 text-slate-900">
                            <Camera className="h-5 w-5" />
                            <p className="font-semibold">Camera Check</p>
                        </div>
                        <span className="text-xs font-semibold text-slate-500">{getDeviceStatusText(cameraStatus, "Ready")}</span>
                    </div>

                    <video
                        ref={videoRef}
                        autoPlay
                        muted
                        playsInline
                        className="h-44 w-full rounded-lg bg-slate-100 object-cover"
                    />

                    <button
                        type="button"
                        onClick={handleCameraCheck}
                        className="mt-3 w-full rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                    >
                        Check Camera
                    </button>
                </div>

                <div className="rounded-xl border border-slate-200 p-4">
                    <div className="mb-3 flex items-center justify-between">
                        <div className="flex items-center gap-2 text-slate-900">
                            <Mic className="h-5 w-5" />
                            <p className="font-semibold">Microphone Check</p>
                        </div>
                        <span className="text-xs font-semibold text-slate-500">
                            {getDeviceStatusText(microphoneStatus, "Ready")}
                        </span>
                    </div>

                    <div className="flex h-44 items-center justify-center rounded-lg bg-slate-100 p-4 text-center text-sm text-slate-600">
                        Run microphone check and allow permission in browser prompt.
                    </div>

                    <button
                        type="button"
                        onClick={handleMicrophoneCheck}
                        className="mt-3 w-full rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                    >
                        Check Microphone
                    </button>
                </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                <p className="font-semibold text-slate-900">Current Selection Summary</p>
                <ul className="mt-2 space-y-1">
                    <li>Resume mode: {resumeMode}</li>
                    <li>Interview type: {interviewType}</li>
                    <li>Difficulty: {difficulty}</li>
                    <li>AI Proctoring: {aiProctoring ? "Enabled" : "Disabled"}</li>
                </ul>
            </div>
        </section>
    );
}
