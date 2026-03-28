import { ArrowLeft, ArrowRight } from "lucide-react";

type WizardActionsProps = {
	currentStep: number;
	isSubmitting: boolean;
	handleBack: () => void;
	handleNext: () => Promise<void>;
};

export default function WizardActions({
	currentStep,
	isSubmitting,
	handleBack,
	handleNext,
}: WizardActionsProps) {
	return (
		<div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-5">
			<button
				type="button"
				onClick={handleBack}
				disabled={currentStep === 1}
				className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
			>
				<ArrowLeft className="h-4 w-4" />
				Back
			</button>

			{currentStep < 4 ? (
				<button
					type="button"
					onClick={handleNext}
					className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
				>
					Continue
					<ArrowRight className="h-4 w-4" />
				</button>
			) : (
				<button
					type="submit"
					disabled={isSubmitting}
					className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-70"
				>
					{isSubmitting ? "Submitting..." : "Submit Interview Setup"}
				</button>
			)}
		</div>
	);
}
