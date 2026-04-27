"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import InterviewReport from "@/components/interview/InterviewReport";
import type { InterviewReportData } from "@/components/interview/InterviewReport";
import { reportService, InterviewSessionDetail } from "@/services/reportService";
import { ArrowLeft } from "lucide-react";

function ReportsContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const sessionId = searchParams.get("sessionId");

    const [reportData, setReportData] = useState<InterviewSessionDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!sessionId) {
            setIsLoading(false);
            return;
        }

        const fetchReport = async () => {
            try {
                const data = await reportService.getPastInterviewDetail(sessionId);
                setReportData(data);
            } catch (err) {
                console.error("Failed to fetch report detail:", err);
                setError("Failed to load interview report.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchReport();
    }, [sessionId]);

    if (isLoading) {
        return (
            <div className="flex h-[50vh] items-center justify-center">
                <div className="text-slate-500 animate-pulse">Loading report...</div>
            </div>
        );
    }

    if (!sessionId) {
        return (
            <div className="flex flex-col h-[50vh] items-center justify-center gap-4">
                <div className="text-slate-500">No session ID provided. Please select an interview from the dashboard.</div>
                <button
                    onClick={() => router.push("/")}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors"
                >
                    <ArrowLeft size={16} />
                    Back to Dashboard
                </button>
            </div>
        );
    }

    if (error || !reportData) {
        return (
            <div className="flex flex-col h-[50vh] items-center justify-center gap-4">
                <div className="text-red-500">{error || "No report data found."}</div>
                <button
                    onClick={() => router.push("/")}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors"
                >
                    <ArrowLeft size={16} />
                    Back to Dashboard
                </button>
            </div>
        );
    }

    const { evaluation_report, created_at, ended_at, difficulty } = reportData;

    // Map backend data to the format expected by the InterviewReport component
    const mappedReport: InterviewReportData = {
        score: evaluation_report?.score || reportData.ats_combined_score || 0,
        domain_rating: evaluation_report?.domain_rating || {},
        swot_analysis: evaluation_report?.swot_analysis || {},
        mistakes: evaluation_report?.mistakes || [],
        suggestions: evaluation_report?.suggestions || [],
        ai_insight: evaluation_report?.ai_insight || "",
    };

    const calculateDuration = (start: string, end: string) => {
        if (!start || !end) return "N/A";
        const diff = new Date(end).getTime() - new Date(start).getTime();
        return `${Math.round(diff / 60000)} minutes`;
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
    };

    return (
        <InterviewReport
            report={mappedReport}
            title={`${difficulty || "Mock"} Interview`}
            date={formatDate(created_at)}
            duration={calculateDuration(created_at, ended_at)}
            onFinish={() => router.push("/")}
            showHomeButton={true}
        />
    );
}

export default function ReportsPage() {
    return (
        <Suspense fallback={
            <div className="flex h-[50vh] items-center justify-center">
                <div className="text-slate-500 animate-pulse">Loading...</div>
            </div>
        }>
            <ReportsContent />
        </Suspense>
    );
}
