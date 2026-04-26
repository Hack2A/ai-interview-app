"use client";

import InterviewReport from "@/components/interview/InterviewReport";
import type { InterviewReportData } from "@/components/interview/InterviewReport";

/* ─── Mock Data (will be replaced by API call later) ─────────────── */

const MOCK_REPORT: InterviewReportData = {
    score: 40,
    domain_rating: {
        Technical: 45,
        Communication: 72,
        HR: 28,
    },
    swot_analysis: {
        strengths: [
            "Strong articulation of React component lifecycles and hook optimization patterns.",
            "Demonstrated professional empathy when discussing conflict resolution scenarios.",
            "Excellent eye contact and presence through the virtual interface.",
        ],
        weaknesses: [
            "Struggled to calculate the Big O complexity of the nested loop solution proposed.",
            'Missing "Company Values" alignment—did not reference core mission during "Why us?"',
            'Over-reliance on "filler words" (um, like) during complex technical explanations.',
        ],
    },
    mistakes: [
        "Struggled to calculate the Big O complexity of the nested loop solution proposed.",
        'Missing "Company Values" alignment—did not reference core mission during "Why us?"',
        'Over-reliance on "filler words" (um, like) during complex technical explanations.',
    ],
    suggestions: [
        "Practice Big O notation with array-based analysis and recursive calls.",
        "Refine behavioral responses using the STAR Method for culture-fit questions.",
    ],
    ai_insight:
        '"You have the technical foundation, but your delivery lacks confidence when tackling unknown problems. Try practicing the "Think Aloud" technique to show your process even if the answer isn\'t perfect."',
};

/* ─── Page ───────────────────────────────────────────────────────── */

export default function ReportsPage() {
    return (
        <InterviewReport
            report={MOCK_REPORT}
            title="Software Engineer Interview"
            date="October 24, 2023"
            duration="45 minutes"
            onRetry={() => {}}
        />
    );
}
