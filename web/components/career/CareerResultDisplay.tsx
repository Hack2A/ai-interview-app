"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Copy, Check } from "lucide-react";

interface CareerResultDisplayProps {
    result: Record<string, unknown>;
    accentColor: string;
}

/** Recursively render any JSON value as a polished card. */
function RenderValue({
    label,
    value,
    accentColor,
    depth = 0,
}: {
    label: string;
    value: unknown;
    accentColor: string;
    depth?: number;
}) {
    const [expanded, setExpanded] = useState(depth < 2);

    // Null / undefined
    if (value === null || value === undefined) {
        return (
            <div className="flex items-center gap-2 py-1">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide min-w-[120px]">
                    {formatLabel(label)}
                </span>
                <span className="text-sm text-gray-400 italic">—</span>
            </div>
        );
    }

    // Array
    if (Array.isArray(value)) {
        return (
            <div className="space-y-1">
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 uppercase tracking-wide hover:text-gray-800 transition-colors cursor-pointer"
                >
                    {expanded ? (
                        <ChevronDown size={14} />
                    ) : (
                        <ChevronRight size={14} />
                    )}
                    {formatLabel(label)}{" "}
                    <span className="text-gray-400 font-normal lowercase">
                        ({value.length} items)
                    </span>
                </button>
                {expanded && (
                    <div className="ml-4 space-y-1.5 border-l-2 pl-4" style={{ borderColor: accentColor + "30" }}>
                        {value.map((item, i) => {
                            if (typeof item === "object" && item !== null) {
                                return (
                                    <div
                                        key={i}
                                        className="bg-gray-50/80 rounded-lg p-3 border border-gray-100"
                                    >
                                        {Object.entries(
                                            item as Record<string, unknown>,
                                        ).map(([k, v]) => (
                                            <RenderValue
                                                key={k}
                                                label={k}
                                                value={v}
                                                accentColor={accentColor}
                                                depth={depth + 1}
                                            />
                                        ))}
                                    </div>
                                );
                            }
                            return (
                                <div
                                    key={i}
                                    className="flex items-center gap-2 py-0.5"
                                >
                                    <span
                                        className="w-1.5 h-1.5 rounded-full shrink-0"
                                        style={{ backgroundColor: accentColor }}
                                    />
                                    <span className="text-sm text-gray-700">
                                        {String(item)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        );
    }

    // Object (nested)
    if (typeof value === "object") {
        return (
            <div className="space-y-1">
                <button
                    onClick={() => setExpanded(!expanded)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 uppercase tracking-wide hover:text-gray-800 transition-colors cursor-pointer"
                >
                    {expanded ? (
                        <ChevronDown size={14} />
                    ) : (
                        <ChevronRight size={14} />
                    )}
                    {formatLabel(label)}
                </button>
                {expanded && (
                    <div className="ml-4 space-y-2 border-l-2 pl-4" style={{ borderColor: accentColor + "30" }}>
                        {Object.entries(value as Record<string, unknown>).map(
                            ([k, v]) => (
                                <RenderValue
                                    key={k}
                                    label={k}
                                    value={v}
                                    accentColor={accentColor}
                                    depth={depth + 1}
                                />
                            ),
                        )}
                    </div>
                )}
            </div>
        );
    }

    // Number — render as a badge if it looks like a score (0-100)
    if (typeof value === "number") {
        const isScore = value >= 0 && value <= 100 && label.toLowerCase().includes("score");
        return (
            <div className="flex items-center gap-3 py-1">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide min-w-[120px]">
                    {formatLabel(label)}
                </span>
                {isScore ? (
                    <div className="flex items-center gap-2">
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                                className="h-full rounded-full transition-all duration-700"
                                style={{
                                    width: `${value}%`,
                                    backgroundColor: accentColor,
                                }}
                            />
                        </div>
                        <span
                            className="text-sm font-bold"
                            style={{ color: accentColor }}
                        >
                            {value}%
                        </span>
                    </div>
                ) : (
                    <span className="text-sm font-medium text-gray-800">
                        {value}
                    </span>
                )}
            </div>
        );
    }

    // Boolean
    if (typeof value === "boolean") {
        return (
            <div className="flex items-center gap-3 py-1">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide min-w-[120px]">
                    {formatLabel(label)}
                </span>
                <span
                    className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        value
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                    }`}
                >
                    {value ? "Yes" : "No"}
                </span>
            </div>
        );
    }

    // String — long strings render as paragraphs
    const strVal = String(value);
    const isLong = strVal.length > 100;

    return (
        <div className={isLong ? "space-y-1 py-1" : "flex items-start gap-3 py-1"}>
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide min-w-[120px] shrink-0">
                {formatLabel(label)}
            </span>
            <span
                className={`text-sm text-gray-700 leading-relaxed ${
                    isLong ? "block whitespace-pre-wrap" : ""
                }`}
            >
                {strVal}
            </span>
        </div>
    );
}

/** Format snake_case labels to Title Case */
function formatLabel(s: string): string {
    return s
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function CareerResultDisplay({
    result,
    accentColor,
}: CareerResultDisplayProps) {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(result, null, 2));
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div
            className="rounded-2xl border bg-white overflow-hidden shadow-lg"
            style={{ borderColor: accentColor + "30" }}
        >
            {/* Header */}
            <div
                className="px-6 py-4 flex items-center justify-between"
                style={{
                    background: `linear-gradient(135deg, ${accentColor}08, ${accentColor}15)`,
                }}
            >
                <div className="flex items-center gap-2">
                    <div
                        className="w-2 h-2 rounded-full animate-pulse"
                        style={{ backgroundColor: accentColor }}
                    />
                    <h3 className="text-sm font-bold text-gray-800">
                        Analysis Result
                    </h3>
                </div>
                <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 
                        px-3 py-1.5 rounded-lg hover:bg-white/80 transition-all duration-200 cursor-pointer"
                >
                    {copied ? (
                        <>
                            <Check size={13} className="text-green-500" />
                            Copied!
                        </>
                    ) : (
                        <>
                            <Copy size={13} />
                            Copy JSON
                        </>
                    )}
                </button>
            </div>

            {/* Body */}
            <div className="px-6 py-5 space-y-3">
                {Object.entries(result).map(([key, value]) => (
                    <RenderValue
                        key={key}
                        label={key}
                        value={value}
                        accentColor={accentColor}
                    />
                ))}
            </div>
        </div>
    );
}
