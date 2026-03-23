import { FieldErrors, UseFormRegister } from "react-hook-form";
import { InterviewFormData, ResumeMode } from "@/types/Interivewtypes";

type ResumeStepProps = {
    resumeMode: ResumeMode;
    register: UseFormRegister<InterviewFormData>;
    errors: FieldErrors<InterviewFormData>;
};

export default function ResumeStep({ resumeMode, register, errors }: ResumeStepProps) {
    return (
        <section className="space-y-4">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Resume Source</h2>
                <p className="text-sm text-slate-600">
                    Choose whether to use an already uploaded resume or upload a new one for this interview.
                </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
                <label
                    className={`cursor-pointer rounded-xl border p-4 ${resumeMode === "existing" ? "border-blue-500 bg-blue-50" : "border-slate-200"
                        }`}
                >
                    <input
                        type="radio"
                        value="existing"
                        className="hidden"
                        {...register("resumeMode", { required: "Please choose one option" })}
                    />
                    <p className="font-semibold text-slate-900">Use existing resume</p>
                    <p className="mt-1 text-sm text-slate-600">Pick a resume already available in your account.</p>
                </label>

                <label
                    className={`cursor-pointer rounded-xl border p-4 ${resumeMode === "new" ? "border-blue-500 bg-blue-50" : "border-slate-200"
                        }`}
                >
                    <input
                        type="radio"
                        value="new"
                        className="hidden"
                        {...register("resumeMode", { required: "Please choose one option" })}
                    />
                    <p className="font-semibold text-slate-900">Upload new resume</p>
                    <p className="mt-1 text-sm text-slate-600">Attach a resume file dedicated to this interview.</p>
                </label>
            </div>

            {resumeMode === "existing" && (
                <div>
                    <label className="mb-2 block text-sm font-semibold text-slate-700">Existing Resume ID / Name</label>
                    <input
                        type="text"
                        placeholder="Example: resume_2026_software_engineer"
                        className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400"
                        {...register("existingResumeId", {
                            validate: (value) => {
                                if (resumeMode !== "existing") {
                                    return true;
                                }

                                return value.trim().length > 0 || "Please provide an existing resume reference";
                            },
                        })}
                    />
                    {errors.existingResumeId && (
                        <p className="mt-1 text-sm text-red-600">{errors.existingResumeId.message}</p>
                    )}
                </div>
            )}

            {resumeMode === "new" && (
                <div>
                    <label className="mb-2 block text-sm font-semibold text-slate-700">Upload Resume</label>
                    <input
                        type="file"
                        accept=".pdf,.doc,.docx"
                        className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-700 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-100 file:px-3 file:py-2 file:font-semibold file:text-blue-700"
                        {...register("newResume", {
                            validate: (value) => {
                                if (resumeMode !== "new") {
                                    return true;
                                }

                                return (value?.length ?? 0) > 0 || "Please upload a resume file";
                            },
                        })}
                    />
                    {errors.newResume && <p className="mt-1 text-sm text-red-600">{errors.newResume.message as string}</p>}
                </div>
            )}
        </section>
    );
}
