import { FieldErrors, UseFormRegister } from "react-hook-form";
import { InterviewFormData, InterviewType } from "@/types/Interivewtypes";

type InterviewTypeStepProps = {
    interviewType: InterviewType;
    register: UseFormRegister<InterviewFormData>;
    errors: FieldErrors<InterviewFormData>;
};

export default function InterviewTypeStep({ interviewType, register, errors }: InterviewTypeStepProps) {
    return (
        <section className="space-y-4">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Interview Mode</h2>
                <p className="text-sm text-slate-600">
                    Use a job description for curated interview questions or keep it generic for a normal interview.
                </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
                <label
                    className={`cursor-pointer rounded-xl border p-4 ${interviewType === "generic" ? "border-blue-500 bg-blue-50" : "border-slate-200"
                        }`}
                >
                    <input
                        type="radio"
                        value="generic"
                        className="hidden"
                        {...register("interviewType", { required: "Please choose one mode" })}
                    />
                    <p className="font-semibold text-slate-900">Normal interview</p>
                    <p className="mt-1 text-sm text-slate-600">No JD required, generic question set.</p>
                </label>

                <label
                    className={`cursor-pointer rounded-xl border p-4 ${interviewType === "curated" ? "border-blue-500 bg-blue-50" : "border-slate-200"
                        }`}
                >
                    <input
                        type="radio"
                        value="curated"
                        className="hidden"
                        {...register("interviewType", { required: "Please choose one mode" })}
                    />
                    <p className="font-semibold text-slate-900">Curated interview</p>
                    <p className="mt-1 text-sm text-slate-600">Provide JD to tailor questions to the role.</p>
                </label>
            </div>

            {interviewType === "curated" && (
                <div>
                    <label className="mb-2 block text-sm font-semibold text-slate-700">Job Description</label>
                    <textarea
                        rows={8}
                        placeholder="Paste the job description here..."
                        className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400"
                        {...register("jobDescription", {
                            validate: (value) => {
                                if (interviewType !== "curated") {
                                    return true;
                                }

                                return value.trim().length > 0 || "Job description is required for curated interviews";
                            },
                        })}
                    />
                    {errors.jobDescription && <p className="mt-1 text-sm text-red-600">{errors.jobDescription.message}</p>}
                </div>
            )}
        </section>
    );
}
