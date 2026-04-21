"use client";

import { useEffect, useRef, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { useRouter } from "next/navigation";
import { useNavbar } from "../../NavbarContext";
import DifficultyStep from "@/components/interview/newInterview/DifficultyStep";
import InterviewTypeStep from "@/components/interview/newInterview/InterviewTypeStep";
import PreviewStep from "@/components/interview/newInterview/PreviewStep";
import ResumeStep from "@/components/interview/newInterview/ResumeStep";
import StepIndicator from "@/components/interview/newInterview/StepIndicator";
import WizardActions from "@/components/interview/newInterview/WizardActions";
import { BackendInterviewPayload, DeviceStatus, InterviewFormData } from "@/types/Interivewtypes";
import { saveInterviewConfig } from "@/hooks/useInterview";
import type { SessionDifficulty } from "@/types/interviewServiceTypes";

export default function NewInterview() {
    const router = useRouter();
    const [currentStep, setCurrentStep] = useState(1);
    const [cameraStatus, setCameraStatus] = useState<DeviceStatus>("idle");
    const [microphoneStatus, setMicrophoneStatus] = useState<DeviceStatus>("idle");
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const cameraStreamRef = useRef<MediaStream | null>(null);
    const microphoneStreamRef = useRef<MediaStream | null>(null);

    // Device lists and selections
    const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([]);
    const [availableMics, setAvailableMics] = useState<MediaDeviceInfo[]>([]);
    const [availableSpeakers, setAvailableSpeakers] = useState<MediaDeviceInfo[]>([]);
    const [selectedCameraId, setSelectedCameraId] = useState<string>("");
    const [selectedMicId, setSelectedMicId] = useState<string>("");
    const [selectedSpeakerId, setSelectedSpeakerId] = useState<string>("");

    const {
        control,
        register,
        trigger,
        setValue,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<InterviewFormData>({
        mode: "onTouched",
        defaultValues: {
            resumeMode: "existing",
            existingResumeId: "",
            newResume: null,
            interviewType: "generic",
            jobDescription: "",
            difficulty: "easy",
            aiProctoring: true,
            cameraChecked: false,
            microphoneChecked: false,
        },
    });

    const resumeMode = useWatch({ control, name: "resumeMode" }) ?? "existing";
    const interviewType = useWatch({ control, name: "interviewType" }) ?? "generic";
    const difficulty = useWatch({ control, name: "difficulty" }) ?? "easy";
    const aiProctoring = useWatch({ control, name: "aiProctoring" }) ?? true;
    const cameraChecked = useWatch({ control, name: "cameraChecked" }) ?? false;
    const microphoneChecked = useWatch({ control, name: "microphoneChecked" }) ?? false;
    const { setShowNavbar } = useNavbar();

    useEffect(() => {
        setShowNavbar(false);
        return () => setShowNavbar(true);
    }, [setShowNavbar]);

    useEffect(() => {
        if (resumeMode === "new") {
            setValue("existingResumeId", "", { shouldValidate: true });
            return;
        }

        setValue("newResume", null, { shouldValidate: true });
    }, [resumeMode, setValue]);

    useEffect(() => {
        if (interviewType === "generic") {
            setValue("jobDescription", "", { shouldValidate: true });
        }
    }, [interviewType, setValue]);

    // Stop streams on unmount
    useEffect(() => {
        return () => {
            cameraStreamRef.current?.getTracks().forEach((track) => track.stop());
            microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());
        };
    }, []);

    /** Enumerate all media devices and update the state lists. */
    const refreshDevices = async () => {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter((d) => d.kind === "videoinput");
            const mics = devices.filter((d) => d.kind === "audioinput");
            const speakers = devices.filter((d) => d.kind === "audiooutput");
            setAvailableCameras(cameras);
            setAvailableMics(mics);
            setAvailableSpeakers(speakers);

            // Set defaults only when they haven't been chosen yet
            setSelectedCameraId((prev) => prev || cameras[0]?.deviceId || "");
            setSelectedMicId((prev) => prev || mics[0]?.deviceId || "");
            setSelectedSpeakerId((prev) => prev || speakers[0]?.deviceId || "");
        } catch (err) {
            console.warn("Could not enumerate devices:", err);
        }
    };

    const validateCurrentStep = async () => {
        if (currentStep === 1) {
            if (resumeMode === "existing") {
                return trigger(["resumeMode", "existingResumeId"]);
            }

            return trigger(["resumeMode", "newResume"]);
        }

        if (currentStep === 2) {
            if (interviewType === "curated") {
                return trigger(["interviewType", "jobDescription"]);
            }

            return trigger(["interviewType"]);
        }

        if (currentStep === 3) {
            return trigger(["difficulty"]);
        }

        return true;
    };

    const handleNext = async () => {
        const isValid = await validateCurrentStep();
        if (!isValid) {
            return;
        }

        setCurrentStep((prev) => Math.min(prev + 1, 4));
    };

    const handleBack = () => {
        setCurrentStep((prev) => Math.max(prev - 1, 1));
    };

    const handleCameraCheck = async (deviceId?: string) => {
        if (!navigator.mediaDevices?.getUserMedia) {
            setCameraStatus("blocked");
            setValue("cameraChecked", false);
            return;
        }

        setCameraStatus("checking");

        try {
            cameraStreamRef.current?.getTracks().forEach((track) => track.stop());

            const videoConstraint = deviceId ? { deviceId: { exact: deviceId } } : true;
            const stream = await navigator.mediaDevices.getUserMedia({ video: videoConstraint, audio: false });
            cameraStreamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            setCameraStatus("ready");
            setValue("cameraChecked", true, { shouldDirty: true });

            // Enumerate devices now that we have permission
            await refreshDevices();
        } catch {
            setCameraStatus("blocked");
            setValue("cameraChecked", false, { shouldDirty: true });
        }
    };

    const handleMicrophoneCheck = async (deviceId?: string) => {
        if (!navigator.mediaDevices?.getUserMedia) {
            setMicrophoneStatus("blocked");
            setValue("microphoneChecked", false);
            return;
        }

        setMicrophoneStatus("checking");

        try {
            microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());

            const audioConstraint = deviceId ? { deviceId: { exact: deviceId } } : true;
            const stream = await navigator.mediaDevices.getUserMedia({ video: false, audio: audioConstraint });
            microphoneStreamRef.current = stream;
            setMicrophoneStatus("ready");
            setValue("microphoneChecked", true, { shouldDirty: true });

            // Enumerate devices now that we have permission
            await refreshDevices();
        } catch {
            setMicrophoneStatus("blocked");
            setValue("microphoneChecked", false, { shouldDirty: true });
        }
    };

    const buildPayload = (data: InterviewFormData): BackendInterviewPayload => {
        return {
            resumeMode: data.resumeMode,
            existingResumeId: data.resumeMode === "existing" ? data.existingResumeId : null,
            newResumeFileName: data.resumeMode === "new" ? data.newResume?.[0]?.name ?? null : null,
            interviewType: data.interviewType,
            jobDescription: data.interviewType === "curated" ? data.jobDescription.trim() : null,
            difficulty: data.difficulty,
            aiProctoring: data.aiProctoring,
            cameraChecked: data.cameraChecked,
            microphoneChecked: data.microphoneChecked,
        };
    };

    /** Convert a File to a base64 string (without the data:… prefix). */
    const fileToBase64 = (file: File): Promise<string> =>
        new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const result = reader.result as string;
                // Strip the "data:application/pdf;base64," prefix
                const base64 = result.split(",")[1] || result;
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });

    /** Map form difficulty values to backend SessionDifficulty. */
    const mapDifficulty = (d: string): SessionDifficulty => {
        const map: Record<string, SessionDifficulty> = {
            easy: "Easy",
            medium: "Medium",
            hard: "Hard",
            extreme: "Extreme",
        };
        return map[d] ?? "Medium";
    };

    const onSubmit = async (data: InterviewFormData) => {
        const payload = buildPayload(data);
        console.log("Interview setup payload", payload);

        // Read resume as base64 PDF if a new file was uploaded
        let resumeBase64: string | undefined;
        if (data.resumeMode === "new" && data.newResume?.[0]) {
            resumeBase64 = await fileToBase64(data.newResume[0]);
        }

        // Save config for the live interview page to pick up
        saveInterviewConfig({
            resumeBase64,
            jdText: data.interviewType === "curated" ? data.jobDescription.trim() : undefined,
            difficulty: mapDifficulty(data.difficulty),
            mode: data.interviewType === "curated" ? "curated" : "generic",
            interviewType: "technical",
            proctoring: data.aiProctoring,
        });

        // Stop preview streams before navigating (live page acquires its own)
        cameraStreamRef.current?.getTracks().forEach((t) => t.stop());
        microphoneStreamRef.current?.getTracks().forEach((t) => t.stop());

        // Redirect to the live interview page
        router.push("/interview/live");
    };

    return (
        <div className="min-h-screen w-full bg-linear-to-br from-slate-50 via-white to-blue-50 px-4 py-8 sm:px-6 lg:px-10">
            <div className="mx-auto w-full max-w-5xl">
                <div className="mb-6 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
                    <p className="text-sm font-semibold text-slate-500">New Interview Setup</p>
                    <h1 className="text-3xl font-bold text-slate-900">Configure your interview</h1>
                    <p className="mt-1 text-sm text-slate-600">
                        Complete each step to build the final interview payload for backend submission.
                    </p>
                </div>

                <StepIndicator currentStep={currentStep} />

                <form
                    onSubmit={handleSubmit(onSubmit)}
                    className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                    {currentStep === 1 && <ResumeStep resumeMode={resumeMode} register={register} errors={errors} />}

                    {currentStep === 2 && (
                        <InterviewTypeStep interviewType={interviewType} register={register} errors={errors} />
                    )}

                    {currentStep === 3 && <DifficultyStep difficulty={difficulty} register={register} errors={errors} />}

                    {currentStep === 4 && (
                        <PreviewStep
                            register={register}
                            cameraStatus={cameraStatus}
                            microphoneStatus={microphoneStatus}
                            videoRef={videoRef}
                            handleCameraCheck={handleCameraCheck}
                            handleMicrophoneCheck={handleMicrophoneCheck}
                            resumeMode={resumeMode}
                            interviewType={interviewType}
                            difficulty={difficulty}
                            aiProctoring={aiProctoring}
                            availableCameras={availableCameras}
                            availableMics={availableMics}
                            availableSpeakers={availableSpeakers}
                            selectedCameraId={selectedCameraId}
                            selectedMicId={selectedMicId}
                            selectedSpeakerId={selectedSpeakerId}
                            onCameraChange={setSelectedCameraId}
                            onMicChange={setSelectedMicId}
                            onSpeakerChange={setSelectedSpeakerId}
                            micStream={microphoneStreamRef.current}
                        />
                    )}

                    <WizardActions
                        currentStep={currentStep}
                        isSubmitting={isSubmitting}
                        handleBack={handleBack}
                        handleNext={handleNext}
                        canSubmit={cameraChecked && microphoneChecked}
                    />
                </form>
            </div>
        </div>
    );
}