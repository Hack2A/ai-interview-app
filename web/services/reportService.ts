import apiClient from "./apiClient";

export interface InterviewSessionSummary {
    id: number;
    session_id: string;
    difficulty: string;
    status: string;
    ats_combined_score?: number | null;
    evaluation_report?: any;
    created_at: string;
    ended_at: string;
}

export interface ChatMessage {
    id: number;
    role: "user" | "ai" | "system";
    content: string;
    created_at: string;
}

export interface InterviewSessionDetail extends InterviewSessionSummary {
    enable_proctoring: boolean;
    ats_algorithmic_score: number;
    ats_llm_score: number;
    evaluation_report: any; // JSON object containing detailed feedback
    messages: ChatMessage[];
}

export const reportService = {
    /**
     * Retrieves a list of all past interview summaries for the authenticated user.
     * Returned in reverse chronological order.
     */
    getPastInterviews: async (): Promise<InterviewSessionSummary[]> => {
        const response = await apiClient.get('/interview/past/');
        return response.data;
    },

    /**
     * Retrieves a specific interview session including its evaluation report and chat history.
     * @param sessionId The unique session identifier
     */
    getPastInterviewDetail: async (sessionId: string): Promise<InterviewSessionDetail> => {
        const response = await apiClient.get(`/interview/past/${sessionId}/`);
        return response.data;
    }
};
