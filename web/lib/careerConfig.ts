import {
	FileSearch,
	FileCode,
	BrainCircuit,
	Route,
	Users,
	FolderGit2,
	Volume2,
} from "lucide-react";
import type { CareerOption } from "@/types/careerTypes";
import type { LucideIcon } from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════════
//  Career Options — Static Config (matches backend schema)
// ═══════════════════════════════════════════════════════════════════════════════

/** Full list of career options, used as the client-side source of truth. */
export const CAREER_OPTIONS: CareerOption[] = [
	{
		id: "match_report",
		title: "Match Report",
		description:
			"Compares your resume against a job description to give you a match score.",
		inputs: [
			{
				name: "resume_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
			{
				name: "jd_text",
				label: "Job Description",
				type: "textarea",
				required: true,
			},
		],
	},
	{
		id: "cover_letter",
		title: "Cover Letter",
		description:
			"Generates a customized cover letter based on your resume and the JD.",
		inputs: [
			{
				name: "resume_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
			{
				name: "jd_text",
				label: "Job Description",
				type: "textarea",
				required: true,
			},
			{
				name: "tone",
				label: "Tone",
				type: "text",
				required: false,
				default: "professional",
			},
		],
	},
	{
		id: "skill_gap",
		title: "Skill Gap Analysis",
		description: "Identifies missing skills between you and the job.",
		inputs: [
			{
				name: "resume_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
			{
				name: "jd_text",
				label: "Job Description",
				type: "textarea",
				required: true,
			},
		],
	},
	{
		id: "roadmap",
		title: "Learning Roadmap",
		description:
			"Generates a step-by-step learning roadmap for a specific topic.",
		inputs: [
			{
				name: "topic",
				label: "Topic",
				type: "text",
				required: true,
			},
			{
				name: "context",
				label: "Context/Current Level",
				type: "textarea",
				required: false,
			},
		],
	},
	{
		id: "recruiter_sim",
		title: "Recruiter Simulator",
		description: "Simulates a recruiter's evaluation of your profile.",
		inputs: [
			{
				name: "resume_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
			{
				name: "jd_text",
				label: "Job Description",
				type: "textarea",
				required: true,
			},
		],
	},
	{
		id: "extract_projects",
		title: "Extract Projects",
		description: "Extracts project details from a raw resume.",
		inputs: [
			{
				name: "raw_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
		],
	},
	{
		id: "industry_calibrate",
		title: "Industry Calibrate",
		description: "Calibrates resume phrasing for different industries.",
		inputs: [
			{
				name: "resume_text",
				label: "Resume Text",
				type: "textarea",
				required: true,
			},
			{
				name: "mode",
				label: "Industry Mode",
				type: "text",
				required: false,
				default: "startup",
			},
		],
	},
];

/** Icon mapping for each career tool — keyed by option id. */
export const CAREER_ICONS: Record<string, LucideIcon> = {
	match_report: FileSearch,
	cover_letter: FileCode,
	skill_gap: BrainCircuit,
	roadmap: Route,
	recruiter_sim: Users,
	extract_projects: FolderGit2,
	industry_calibrate: Volume2,
};

/** Gradient color mapping for career tool cards. */
export const CAREER_GRADIENTS: Record<string, { from: string; to: string }> = {
	match_report: { from: "#3B82F6", to: "#2563EB" },
	cover_letter: { from: "#8B5CF6", to: "#6D28D9" },
	skill_gap: { from: "#F59E0B", to: "#D97706" },
	roadmap: { from: "#10B981", to: "#059669" },
	recruiter_sim: { from: "#EC4899", to: "#DB2777" },
	extract_projects: { from: "#6366F1", to: "#4F46E5" },
	industry_calibrate: { from: "#14B8A6", to: "#0D9488" },
};

/** Lookup a career option by its slug (URL-safe id with hyphens). */
export function getCareerOptionBySlug(
	slug: string,
): CareerOption | undefined {
	// Convert URL slug (e.g. "match-report") to option id (e.g. "match_report")
	const id = slug.replace(/-/g, "_");
	return CAREER_OPTIONS.find((opt) => opt.id === id);
}

/** Convert an option id to a URL slug. */
export function toSlug(id: string): string {
	return id.replace(/_/g, "-");
}
