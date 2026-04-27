import apiClient from "./apiClient";
import type {
	CareerOptionsResponse,
	CareerActionRequest,
	CareerActionResponse,
} from "@/types/careerTypes";

// ═══════════════════════════════════════════════════════════════════════════════
//  Career Service — REST API
// ═══════════════════════════════════════════════════════════════════════════════

const CAREER_BASE = "career";

/**
 * GET /api/career/options/
 * Fetch all available career AI tools and their input schemas.
 */
export async function getCareerOptions(): Promise<CareerOptionsResponse> {
	const { data } = await apiClient.get<CareerOptionsResponse>(
		`${CAREER_BASE}/options/`,
	);
	return data;
}

/**
 * POST /api/career/action/
 * Execute a career AI action with the given form payload.
 *
 * @param payload - Must include `action` (the tool id) plus all required inputs.
 * @returns The raw JSON result from the ML task.
 *
 * @example
 * ```ts
 * const result = await executeCareerAction({
 *   action: "match_report",
 *   resume_text: "Experienced software engineer...",
 *   jd_text: "Looking for a backend dev..."
 * });
 * ```
 */
export async function executeCareerAction(
	payload: CareerActionRequest,
): Promise<CareerActionResponse> {
	const { data } = await apiClient.post<CareerActionResponse>(
		`${CAREER_BASE}/action/`,
		payload,
	);
	return data;
}
