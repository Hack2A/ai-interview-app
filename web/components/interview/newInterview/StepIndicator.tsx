import { STEP_TITLES } from "@/types/Interivewtypes";

type StepIndicatorProps = {
    currentStep: number;
};

export default function StepIndicator({ currentStep }: StepIndicatorProps) {
    return (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {STEP_TITLES.map((title, index) => {
                const stepNumber = index + 1;
                const isActive = currentStep === stepNumber;
                const isDone = currentStep > stepNumber;

                return (
                    <div
                        key={title}
                        className={`rounded-xl border px-3 py-2 text-sm ${isActive
                            ? "border-blue-500 bg-blue-50 text-blue-700"
                            : isDone
                                ? "border-green-200 bg-green-50 text-green-700"
                                : "border-slate-200 bg-white text-slate-500"
                            }`}
                    >
                        <p className="text-xs font-semibold uppercase tracking-wide">Step {stepNumber}</p>
                        <p className="font-semibold">{title}</p>
                    </div>
                );
            })}
        </div>
    );
}
