"use client";

import { useEffect, useRef, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { useNavbar } from "../../NavbarContext";
import DifficultyStep from "@/components/interview/newInterview/DifficultyStep";
import InterviewTypeStep from "@/components/interview/newInterview/InterviewTypeStep";
import PreviewStep from "@/components/interview/newInterview/PreviewStep";
import ResumeStep from "@/components/interview/newInterview/ResumeStep";
import StepIndicator from "@/components/interview/newInterview/StepIndicator";
import WizardActions from "@/components/interview/newInterview/WizardActions";
import { BackendInterviewPayload, DeviceStatus, InterviewFormData } from "@/types/Interivewtypes";

export default function NewInterview() {
    const [currentStep, setCurrentStep] = useState(1);
    const [cameraStatus, setCameraStatus] = useState<DeviceStatus>("idle");
    const [microphoneStatus, setMicrophoneStatus] = useState<DeviceStatus>("idle");
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const cameraStreamRef = useRef<MediaStream | null>(null);
    const microphoneStreamRef = useRef<MediaStream | null>(null);

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

    useEffect(() => {
        return () => {
            cameraStreamRef.current?.getTracks().forEach((track) => track.stop());
            microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());
        };
    }, []);

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

    const handleCameraCheck = async () => {
        if (!navigator.mediaDevices?.getUserMedia) {
            setCameraStatus("blocked");
            setValue("cameraChecked", false);
            return;
        }

        setCameraStatus("checking");

        try {
            cameraStreamRef.current?.getTracks().forEach((track) => track.stop());
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            cameraStreamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            setCameraStatus("ready");
            setValue("cameraChecked", true, { shouldDirty: true });
        } catch {
            setCameraStatus("blocked");
            setValue("cameraChecked", false, { shouldDirty: true });
        }
    };

    const handleMicrophoneCheck = async () => {
        if (!navigator.mediaDevices?.getUserMedia) {
            setMicrophoneStatus("blocked");
            setValue("microphoneChecked", false);
            return;
        }

        setMicrophoneStatus("checking");

        try {
            microphoneStreamRef.current?.getTracks().forEach((track) => track.stop());
            const stream = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
            microphoneStreamRef.current = stream;
            setMicrophoneStatus("ready");
            setValue("microphoneChecked", true, { shouldDirty: true });
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

    const onSubmit = (data: InterviewFormData) => {
        const payload = buildPayload(data);
        console.log("Interview setup payload", payload);
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
                        />
                    )}

                    <WizardActions
                        currentStep={currentStep}
                        isSubmitting={isSubmitting}
                        handleBack={handleBack}
                        handleNext={handleNext}
                    />
                </form>
            </div>
        </div>
    );
}