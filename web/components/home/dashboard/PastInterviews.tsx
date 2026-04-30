"use client";

import { motion, Variants } from "framer-motion";
import ScoreRing from "./ScoreRing";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { reportService, InterviewSessionSummary } from "@/services/reportService";

const container: Variants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.07 },
    },
};

const item: Variants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" } },
};

export default function PastInterviews() {
    const router = useRouter();
    const [interviews, setInterviews] = useState<InterviewSessionSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchInterviews = async () => {
            try {
                const data = await reportService.getPastInterviews();
                setInterviews(data);
            } catch (error) {
                console.error("Failed to fetch past interviews:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchInterviews();
    }, []);

    const calculateDuration = (start: string, end: string) => {
        if (!start || !end) return "N/A";
        const startTime = new Date(start).getTime();
        const endTime = new Date(end).getTime();
        const diffMinutes = Math.round((endTime - startTime) / 60000);
        return `${diffMinutes} min`;
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-8 text-sm text-gray-500">
                Loading past interviews...
            </div>
        );
    }

    if (interviews.length === 0) {
        return (
            <div className="flex items-center justify-center py-8 text-sm text-gray-500">
                No past interviews found.
            </div>
        );
    }

    return (
        <motion.div
            className="grid grid-cols-2 gap-4"
            variants={container}
            initial="hidden"
            animate="show"
        >
            {interviews.map((interview) => (
                <motion.div
                    key={interview.id}
                    onClick={() => {
                        router.push(`/reports?sessionId=${interview.session_id}`);
                    }}
                    className="bg-white border border-gray-200 rounded-xl px-5 py-4 flex items-center justify-between gap-4 transition-all duration-300 hover:shadow-md hover:border-gray-300 hover:-translate-y-0.5 cursor-pointer"
                    variants={item}
                >
                    <div className="flex flex-col gap-1">
                        <span className="text-[0.95rem] font-semibold text-gray-800 capitalize">
                            {interview.difficulty || "Mock"} Interview
                        </span>
                        <span className="text-xs text-gray-400">
                            Date: {formatDate(interview.created_at)}
                        </span>
                        <span className="text-xs text-gray-400">
                            Duration: {calculateDuration(interview.created_at, interview.ended_at)}
                        </span>
                    </div>
                    <ScoreRing score={interview.evaluation_report?.score || interview.ats_combined_score || 0} />
                </motion.div>
            ))}
        </motion.div>
    );
}
