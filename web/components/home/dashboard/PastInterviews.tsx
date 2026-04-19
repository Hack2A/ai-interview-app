"use client";

import { motion, Variants } from "framer-motion";
import ScoreRing from "./ScoreRing";

const MOCK_INTERVIEWS = [
    {
        id: 1,
        title: "Product Manager Mock Interview",
        date: "Oct 24, 2023",
        duration: "45 min",
        score: 85,
    },
    {
        id: 2,
        title: "Software Engineer Technical Round",
        date: "Oct 18, 2023",
        duration: "60 min",
        score: 78,
    },
    {
        id: 3,
        title: "Behavioral Interview Practice",
        date: "Oct 10, 2023",
        duration: "30 min",
        score: 92,
    },
    {
        id: 4,
        title: "Sales Presentation Mock",
        date: "Oct 2, 2023",
        duration: "50 min",
        score: 88,
    },
];

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
    return (
        <motion.div
            className="grid grid-cols-2 gap-4"
            variants={container}
            initial="hidden"
            animate="show"
        >
            {MOCK_INTERVIEWS.map((interview) => (
                <motion.div
                    key={interview.id}
                    className="bg-white border border-gray-200 rounded-xl px-5 py-4 flex items-center justify-between gap-4 transition-all duration-300 hover:shadow-md hover:border-gray-300 hover:-translate-y-0.5 cursor-pointer"
                    variants={item}
                >
                    <div className="flex flex-col gap-1">
                        <span className="text-[0.95rem] font-semibold text-gray-800">
                            {interview.title}
                        </span>
                        <span className="text-xs text-gray-400">
                            Date: {interview.date}
                        </span>
                        <span className="text-xs text-gray-400">
                            Duration: {interview.duration}
                        </span>
                    </div>
                    <ScoreRing score={interview.score} />
                </motion.div>
            ))}
        </motion.div>
    );
}
