"use client";

import { InterviewHeaderProps } from "@/types/LiveInterviewTypes";
import { ArrowLeft } from "lucide-react";

export default function InterviewHeader({
    title,
    candidateName,
    status,
}: InterviewHeaderProps) {
    const statusLabel =
        status === "in-progress"
            ? "In Progress"
            : status === "paused"
                ? "Paused"
                : "Completed";

    const statusColor =
        status === "in-progress"
            ? "bg-emerald-500"
            : status === "paused"
                ? "bg-amber-500"
                : "bg-slate-400";

    const badgeBg =
        status === "in-progress"
            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
            : status === "paused"
                ? "bg-amber-50 text-amber-700 border-amber-200"
                : "bg-slate-50 text-slate-600 border-slate-200";

    return (
        <header className="flex items-center justify-between px-5 py-3 border-b border-slate-200/60 bg-white/80 backdrop-blur-md">
            <div className="flex items-center gap-4">
                <button
                    type="button"
                    className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-slate-100 transition-colors"
                    aria-label="Go back"
                >
                    <ArrowLeft className="w-4 h-4 text-slate-600" />
                </button>

                <div className="flex items-center gap-2.5">
                    <span className="relative flex h-2.5 w-2.5">
                        <span
                            className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${statusColor}`}
                        />
                        <span
                            className={`relative inline-flex h-2.5 w-2.5 rounded-full ${statusColor}`}
                        />
                    </span>
                    <h1 className="text-base font-semibold text-slate-900">
                        {title}
                    </h1>
                </div>

                <div className="h-5 w-px bg-slate-200" />

                <span className="text-sm font-medium text-slate-600">
                    {candidateName}
                </span>

                <span
                    className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badgeBg}`}
                >
                    {statusLabel}
                </span>
            </div>
        </header>
    );
}
