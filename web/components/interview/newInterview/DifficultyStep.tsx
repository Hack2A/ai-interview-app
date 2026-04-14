import { FieldErrors, UseFormRegister } from "react-hook-form";
import { Difficulty, InterviewFormData } from "@/types/Interivewtypes";

type DifficultyStepProps = {
    difficulty: Difficulty;
    register: UseFormRegister<InterviewFormData>;
    errors: FieldErrors<InterviewFormData>;
};

const options = [
    { key: "easy", label: "Easy", hint: "Warm-up and basics" },
    { key: "medium", label: "Medium", hint: "Balanced depth" },
    { key: "hard", label: "Hard", hint: "Advanced challenge" },
    { key: "extreme", label: "Extreme", hint: "Expert-level gauntlet" },
] as const;

export default function DifficultyStep({ difficulty, register, errors }: DifficultyStepProps) {
    return (
        <section className="space-y-4">
            <div>
                <h2 className="text-2xl font-semibold text-slate-900">Difficulty Level</h2>
                <p className="text-sm text-slate-600">Select the level for this interview session.</p>
            </div>

            <div className="grid gap-3 sm:grid-cols-4">
                {options.map((option) => (
                    <label
                        key={option.key}
                        className={`cursor-pointer rounded-xl border p-4 ${difficulty === option.key ? "border-blue-500 bg-blue-50" : "border-slate-200"
                            }`}
                    >
                        <input
                            type="radio"
                            value={option.key}
                            className="hidden"
                            {...register("difficulty", { required: "Please select a difficulty" })}
                        />
                        <p className="font-semibold text-slate-900">{option.label}</p>
                        <p className="mt-1 text-sm text-slate-600">{option.hint}</p>
                    </label>
                ))}
            </div>
            {errors.difficulty && <p className="text-sm text-red-600">{errors.difficulty.message}</p>}
        </section>
    );
}
