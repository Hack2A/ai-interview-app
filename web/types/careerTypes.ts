// ═══════════════════════════════════════════════════════════════════════════════
//  Career Service Types
// ═══════════════════════════════════════════════════════════════════════════════

/** A single input field descriptor from the career options schema. */
export interface CareerInput {
	name: string;
	label: string;
	type: "text" | "textarea";
	required: boolean;
	default?: string;
}

/** One career tool option returned from the backend. */
export interface CareerOption {
	id: string;
	title: string;
	description: string;
	inputs: CareerInput[];
}

/** Response shape from GET /api/career/options/ */
export interface CareerOptionsResponse {
	options: CareerOption[];
}

/** Payload sent to POST /api/career/action/ */
export interface CareerActionRequest {
	action: string;
	[key: string]: string; // dynamic keys from the form
}

/** Generic JSON response from POST /api/career/action/ */
export type CareerActionResponse = Record<string, unknown>;
