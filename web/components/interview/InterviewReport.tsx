"use client";

import { useState } from "react";
import {
    FileText,
    Download,
    RotateCcw,
    Code2,
    MessageSquare,
    Users,
    Clock,
    TrendingUp,
    CheckCircle2,
    AlertTriangle,
    Sparkles,
    ThumbsUp,
    ThumbsDown,
    BookOpen,
    ChevronRight,
    Eye,
    Home,
} from "lucide-react";

/* ─── Types ──────────────────────────────────────────────────────── */

export interface InterviewReportData {
    /** Overall score out of 100 */
    score: number;
    /** Domain-level ratings, e.g. { HR: 20, Technical: 40, Communication: 72 } */
    domain_rating: Record<string, number>;
    /** SWOT-style analysis */
    swot_analysis?: {
        strengths?: string[];
        weaknesses?: string[];
    };
    /** Key mistakes made */
    mistakes?: string[];
    /** Improvement suggestions */
    suggestions?: string[];
    /** Optional AI-generated insight quote */
    ai_insight?: string;
}

export interface InterviewReportProps {
    /** The report data returned from the backend */
    report: InterviewReportData;
    /** Title shown at the top (e.g. "Software Engineer Interview") */
    title?: string;
    /** Date string (e.g. "October 24, 2023") */
    date?: string;
    /** Duration string (e.g. "45 minutes") */
    duration?: string;
    /** Called when user clicks "Go Home" / finishes viewing */
    onFinish?: () => void;
    /** Called when user clicks "Retry Session" */
    onRetry?: () => void;
    /** If true, shows "Go Home" button (live interview context) */
    showHomeButton?: boolean;
}

/* ─── Circular Progress Component ────────────────────────────────── */

function ScoreGauge({ score, size = 120 }: { score: number; size?: number }) {
    const strokeWidth = 8;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const progress = (score / 100) * circumference;
    const dashOffset = circumference - progress;

    const getColor = () => {
        if (score >= 70) return "#10b981";
        if (score >= 50) return "#f59e0b";
        return "#ef4444";
    };

    return (
        <div className="relative" style={{ width: size, height: size }}>
            <svg width={size} height={size} className="transform -rotate-90">
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke="#f1f5f9"
                    strokeWidth={strokeWidth}
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={getColor()}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={dashOffset}
                    style={{
                        transition: "stroke-dashoffset 1.2s ease-out",
                    }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-black text-slate-900">
                    {score}
                </span>
                <span className="text-[10px] text-slate-400 font-medium">
                    out of 100
                </span>
            </div>
        </div>
    );
}

/* ─── Mini Bar Chart ─────────────────────────────────────────────── */

function BarChart({ data }: { data: number[] }) {
    const max = Math.max(...data, 50);
    return (
        <div className="flex items-end gap-1.5 h-16">
            {data.map((val, i) => (
                <div
                    key={i}
                    className="flex-1 rounded-t-sm transition-all duration-700 ease-out"
                    style={{
                        height: `${(val / max) * 100}%`,
                        background:
                            i === data.length - 1
                                ? "linear-gradient(to top, #3b82f6, #60a5fa)"
                                : "#cbd5e1",
                        minWidth: 12,
                    }}
                />
            ))}
        </div>
    );
}

/* ─── Category Score Card ────────────────────────────────────────── */

const DOMAIN_CONFIG: Record<
    string,
    { icon: React.ElementType; color: string; bgColor: string; subtitle: string }
> = {
    technical: {
        icon: Code2,
        color: "#3b82f6",
        bgColor: "#eff6ff",
        subtitle: "DSA & System Design",
    },
    communication: {
        icon: MessageSquare,
        color: "#8b5cf6",
        bgColor: "#f5f3ff",
        subtitle: "Clarity & Structure",
    },
    hr: {
        icon: Users,
        color: "#ef4444",
        bgColor: "#fef2f2",
        subtitle: "Culture & Values",
    },
};

const DEFAULT_DOMAIN_CONFIG = {
    icon: FileText,
    color: "#6366f1",
    bgColor: "#eef2ff",
    subtitle: "Assessment",
};

function CategoryCard({
    name,
    score,
}: {
    name: string;
    score: number;
}) {
    const config =
        DOMAIN_CONFIG[name.toLowerCase()] || DEFAULT_DOMAIN_CONFIG;
    const Icon = config.icon;

    return (
        <div className="bg-white rounded-xl border border-slate-100 p-4 flex items-center gap-3.5 shadow-sm hover:shadow-md transition-shadow">
            <div
                className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: config.bgColor }}
            >
                <Icon size={18} style={{ color: config.color }} />
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-bold text-slate-800">
                        {name}
                    </h3>
                    <span
                        className="text-lg font-black"
                        style={{ color: config.color }}
                    >
                        {score}%
                    </span>
                </div>
                <p className="text-[11px] text-slate-400 font-medium">
                    {config.subtitle}
                </p>
            </div>
        </div>
    );
}

/* ─── Score Label Helper ─────────────────────────────────────────── */

function getScoreLabel(score: number) {
    if (score >= 80) return "Excellent";
    if (score >= 70) return "Great";
    if (score >= 60) return "Good";
    if (score >= 50) return "Average";
    return "Needs Focus";
}

/* ─── Main Component ─────────────────────────────────────────────── */

export default function InterviewReport({
    report,
    title = "Interview Report",
    date,
    duration,
    onFinish,
    onRetry,
    showHomeButton = false,
}: InterviewReportProps) {
    const [feedbackGiven, setFeedbackGiven] = useState<
        "up" | "down" | null
    >(null);

    const score = report.score ?? 0;
    const domainRating = report.domain_rating ?? {};
    const strengths = report.swot_analysis?.strengths ?? [];
    const weaknesses = report.swot_analysis?.weaknesses ?? [];
    const mistakes = report.mistakes ?? [];
    const suggestions = report.suggestions ?? [];
    const aiInsight = report.ai_insight || null;

    const label = getScoreLabel(score);

    // Build score progression placeholder from domain values
    const domainScores = Object.values(domainRating);
    const scoreProgression =
        domainScores.length >= 2
            ? domainScores
            : [score * 0.7, score * 0.8, score * 0.85, score * 0.9, score];

    return (
        <div className="w-full max-w-[1100px] mx-auto px-4 sm:px-6 py-8 pb-16">
            {/* ── Header ─────────────────────────────────────────── */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
                <div>
                    <h1 className="text-2xl font-black text-slate-900">
                        {title}
                    </h1>
                    {(date || duration) && (
                        <p className="text-sm text-slate-400 mt-1">
                            {date && `Conducted on ${date}`}
                            {date && duration && " • "}
                            {duration}
                        </p>
                    )}
                </div>
                <div className="flex gap-2.5 flex-shrink-0">
                    <button className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 bg-white text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-all cursor-pointer shadow-sm">
                        <Download size={14} />
                        Export PDF
                    </button>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-sm font-semibold text-white hover:bg-blue-700 transition-all cursor-pointer shadow-sm"
                        >
                            <RotateCcw size={14} />
                            Retry Session
                        </button>
                    )}
                    {showHomeButton && onFinish && (
                        <button
                            onClick={onFinish}
                            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 text-sm font-semibold text-white hover:bg-slate-800 transition-all cursor-pointer shadow-sm"
                        >
                            <Home size={14} />
                            Go Home
                        </button>
                    )}
                </div>
            </div>

            {/* ── Top Row: Score + Categories + Chart ─────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-6">
                {/* Overall Score */}
                <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-100 p-5 shadow-sm flex flex-col items-center justify-center text-center">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">
                        Overall Performance
                    </p>
                    <ScoreGauge score={score} />
                    <span
                        className="mt-3 inline-block px-3 py-1 rounded-full text-xs font-bold"
                        style={{
                            background:
                                score >= 70
                                    ? "#d1fae5"
                                    : score >= 50
                                      ? "#fef3c7"
                                      : "#fee2e2",
                            color:
                                score >= 70
                                    ? "#065f46"
                                    : score >= 50
                                      ? "#92400e"
                                      : "#991b1b",
                        }}
                    >
                        ↗ {label}
                    </span>
                </div>

                {/* Categories + Chart + Stats */}
                <div className="lg:col-span-9 space-y-4">
                    {/* Category Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {Object.entries(domainRating).map(
                            ([domain, domScore]) => (
                                <CategoryCard
                                    key={domain}
                                    name={domain}
                                    score={domScore}
                                />
                            ),
                        )}
                    </div>

                    {/* Chart Row */}
                    <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                        <div className="sm:col-span-5 bg-white rounded-xl border border-slate-100 p-4 shadow-sm">
                            <p className="text-xs font-bold text-slate-500 mb-1">
                                Score Breakdown
                            </p>
                            <p className="text-[10px] text-slate-300 mb-3">
                                By domain
                            </p>
                            <BarChart data={scoreProgression} />
                        </div>

                        <div className="sm:col-span-7 grid grid-cols-2 gap-3">
                            <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm flex items-start gap-3">
                                <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <TrendingUp
                                        size={14}
                                        className="text-blue-500"
                                    />
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-slate-700">
                                        Score
                                    </p>
                                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                                        {score}/100 overall rating
                                    </p>
                                </div>
                            </div>
                            <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-sm flex items-start gap-3">
                                <div className="w-8 h-8 rounded-lg bg-amber-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <Clock
                                        size={14}
                                        className="text-amber-500"
                                    />
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-slate-700">
                                        Domains
                                    </p>
                                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                                        {Object.keys(domainRating).length} areas
                                        evaluated
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Bottom Row: Analysis + AI Insights ─────────────── */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-6">
                {/* Detailed Analysis */}
                <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
                    <h2 className="text-base font-black text-slate-900 flex items-center gap-2 mb-5">
                        <FileText size={16} className="text-slate-500" />
                        Detailed Analysis
                    </h2>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                        {/* Strengths */}
                        <div>
                            <h3 className="flex items-center gap-2 text-sm font-bold text-emerald-700 mb-3">
                                <CheckCircle2
                                    size={14}
                                    className="text-emerald-500"
                                />
                                Key Strengths
                            </h3>
                            <ul className="space-y-2.5">
                                {(strengths.length > 0
                                    ? strengths
                                    : ["N/A"]
                                ).map((s, i) => (
                                    <li
                                        key={i}
                                        className="flex items-start gap-2 text-sm text-slate-600 leading-relaxed"
                                    >
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
                                        {s}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Weaknesses / Improvements */}
                        <div>
                            <h3 className="flex items-center gap-2 text-sm font-bold text-red-600 mb-3">
                                <AlertTriangle
                                    size={14}
                                    className="text-red-400"
                                />
                                Areas for Improvement
                            </h3>
                            <ul className="space-y-2.5">
                                {(weaknesses.length > 0
                                    ? weaknesses
                                    : ["N/A"]
                                ).map((s, i) => (
                                    <li
                                        key={i}
                                        className="flex items-start gap-2 text-sm text-slate-600 leading-relaxed"
                                    >
                                        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-red-400 flex-shrink-0" />
                                        {s}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>

                {/* AI Insights + Resources */}
                <div className="lg:col-span-5 space-y-4">
                    {/* AI Insight Quote */}
                    {aiInsight && (
                        <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-100 p-5 shadow-sm">
                            <h3 className="flex items-center gap-2 text-xs font-black text-amber-700 uppercase tracking-wider mb-3">
                                <Sparkles
                                    size={13}
                                    className="text-amber-500"
                                />
                                AI Insights
                            </h3>
                            <p className="text-sm text-slate-700 leading-relaxed italic">
                                {aiInsight}
                            </p>
                            <div className="flex items-center justify-between mt-4">
                                <span className="text-[10px] text-slate-400 font-medium">
                                    Was this helpful?
                                </span>
                                <div className="flex gap-1.5">
                                    <button
                                        onClick={() =>
                                            setFeedbackGiven("up")
                                        }
                                        className={`p-1.5 rounded-lg transition-all cursor-pointer ${
                                            feedbackGiven === "up"
                                                ? "bg-emerald-100 text-emerald-600"
                                                : "bg-white/60 text-slate-400 hover:bg-white hover:text-emerald-500"
                                        }`}
                                    >
                                        <ThumbsUp size={13} />
                                    </button>
                                    <button
                                        onClick={() =>
                                            setFeedbackGiven("down")
                                        }
                                        className={`p-1.5 rounded-lg transition-all cursor-pointer ${
                                            feedbackGiven === "down"
                                                ? "bg-red-100 text-red-600"
                                                : "bg-white/60 text-slate-400 hover:bg-white hover:text-red-500"
                                        }`}
                                    >
                                        <ThumbsDown size={13} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Actionable Feedback */}
                    {(mistakes.length > 0 || suggestions.length > 0) && (
                        <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                                Actionable Feedback
                            </h3>

                            {mistakes.length > 0 && (
                                <div className="mb-4">
                                    <p className="text-xs font-semibold text-amber-600 mb-2">
                                        Key Mistakes
                                    </p>
                                    <ul className="space-y-1.5">
                                        {mistakes.map((m, i) => (
                                            <li
                                                key={i}
                                                className="flex items-start gap-2 text-sm text-slate-600"
                                            >
                                                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                                                {m}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {suggestions.length > 0 && (
                                <div>
                                    <p className="text-xs font-semibold text-blue-600 mb-2">
                                        Improvement Suggestions
                                    </p>
                                    <ul className="space-y-1.5">
                                        {suggestions.map((s, i) => (
                                            <li
                                                key={i}
                                                className="flex items-start gap-2 text-sm text-slate-600"
                                            >
                                                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                                                {s}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Recommended Resources */}
                    <div className="bg-white rounded-2xl border border-slate-100 p-5 shadow-sm">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                            Recommended Resources
                        </h3>
                        <div className="space-y-3">
                            {[
                                {
                                    title: "Mastering System Design",
                                    meta: "20 hrs • Intermediate",
                                    color: "#1e3a5f",
                                },
                                {
                                    title: "Behavioral Interviewing",
                                    meta: "11 hrs • Beginner",
                                    color: "#2d4a3e",
                                },
                            ].map((res, i) => (
                                <div
                                    key={i}
                                    className="flex items-center gap-3 p-2 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer group"
                                >
                                    <div
                                        className="w-11 h-14 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm"
                                        style={{
                                            background: `linear-gradient(135deg, ${res.color}, ${res.color}cc)`,
                                        }}
                                    >
                                        <BookOpen
                                            size={16}
                                            className="text-white/80"
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
                                            {res.title}
                                        </p>
                                        <p className="text-[11px] text-slate-400">
                                            {res.meta}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* ── Actionable Next Steps ──────────────────────────── */}
            <div className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
                <h2 className="text-base font-black text-slate-900 mb-4">
                    Actionable Next Steps
                </h2>
                <div className="space-y-3">
                    {[
                        {
                            title: "Review: Big O Notation & Space Complexity",
                            description:
                                "Focus on array-based analysis and recursive calls.",
                            icon: BookOpen,
                        },
                        {
                            title: "Practice: STAR Method Workshop",
                            description:
                                "Refine behavioral responses for culture-fit questions.",
                            icon: Eye,
                        },
                    ].map((step, i) => (
                        <div
                            key={i}
                            className="flex items-center gap-4 p-4 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all cursor-pointer group"
                        >
                            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center flex-shrink-0 group-hover:bg-blue-100 transition-colors">
                                <step.icon
                                    size={18}
                                    className="text-blue-600"
                                />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-bold text-slate-800">
                                    {step.title}
                                </p>
                                <p className="text-xs text-slate-400 mt-0.5">
                                    {step.description}
                                </p>
                            </div>
                            <ChevronRight
                                size={16}
                                className="text-slate-300 group-hover:text-blue-500 transition-colors flex-shrink-0"
                            />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
