"use client";

import { motion } from "framer-motion";
import { Check, AlertTriangle } from "lucide-react";

const SKILLS = {
    confidence: 90,
    pacing: 80,
    clarity: 85,
};

const STRENGTHS = [
    "Strong technical knowledge",
    "Clear articulation",
    "Effective pacing",
];

const FOCUS_AREAS = [
    "Improve confidence in delivery",
    "Enhance body language awareness",
];

/**
 * SVG Radar Chart Component
 * Draws a polygon-style radar for skill dimensions.
 */
function RadarChart({
    data,
}: {
    data: { label: string; value: number }[];
}) {
    const cx = 120;
    const cy = 110;
    const maxR = 80;
    const levels = 4;

    const angleSlice = (2 * Math.PI) / data.length;
    const startAngle = -Math.PI / 2;

    const gridPolygons = Array.from({ length: levels }, (_, level) => {
        const r = (maxR * (level + 1)) / levels;
        const points = data
            .map((_, i) => {
                const angle = startAngle + i * angleSlice;
                return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`;
            })
            .join(" ");
        return points;
    });

    const dataPoints = data.map((d, i) => {
        const r = (d.value / 100) * maxR;
        const angle = startAngle + i * angleSlice;
        return {
            x: cx + r * Math.cos(angle),
            y: cy + r * Math.sin(angle),
        };
    });
    const dataPolygon = dataPoints.map((p) => `${p.x},${p.y}`).join(" ");

    const labels = data.map((d, i) => {
        const r = maxR + 24;
        const angle = startAngle + i * angleSlice;
        return {
            x: cx + r * Math.cos(angle),
            y: cy + r * Math.sin(angle),
            label: d.label,
            value: d.value,
        };
    });

    return (
        <svg width="240" height="240" viewBox="0 0 240 240">
            {/* Grid */}
            {gridPolygons.map((points, i) => (
                <polygon
                    key={i}
                    points={points}
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="1"
                    opacity={0.6 + i * 0.1}
                />
            ))}

            {/* Axes */}
            {data.map((_, i) => {
                const angle = startAngle + i * angleSlice;
                return (
                    <line
                        key={i}
                        x1={cx}
                        y1={cy}
                        x2={cx + maxR * Math.cos(angle)}
                        y2={cy + maxR * Math.sin(angle)}
                        stroke="#e5e7eb"
                        strokeWidth="1"
                    />
                );
            })}

            {/* Data polygon */}
            <motion.polygon
                points={dataPolygon}
                fill="rgba(59, 130, 246, 0.12)"
                stroke="#3b82f6"
                strokeWidth="2"
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                style={{ transformOrigin: `${cx}px ${cy}px` }}
            />

            {/* Data points */}
            {dataPoints.map((p, i) => (
                <motion.circle
                    key={i}
                    cx={p.x}
                    cy={p.y}
                    r="4"
                    fill="#3b82f6"
                    stroke="white"
                    strokeWidth="2"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + i * 0.1, duration: 0.3 }}
                />
            ))}

            {/* Labels */}
            {labels.map((l, i) => (
                <g key={i}>
                    <text
                        x={l.x}
                        y={l.y - 6}
                        textAnchor="middle"
                        dominantBaseline="central"
                        className="text-xs font-semibold"
                        fill="#374151"
                    >
                        {l.label}
                    </text>
                    <text
                        x={l.x}
                        y={l.y + 10}
                        textAnchor="middle"
                        dominantBaseline="central"
                        className="text-xs font-bold"
                        fill="#3b82f6"
                    >
                        {l.value}%
                    </text>
                </g>
            ))}
        </svg>
    );
}

export default function SkillInsights() {
    const radarData = [
        { label: "Confidence", value: SKILLS.confidence },
        { label: "Pacing", value: SKILLS.pacing },
        { label: "Clarity", value: SKILLS.clarity },
    ];

    return (
        <motion.div
            className="grid grid-cols-3 gap-6 items-start"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
        >
            {/* Radar Chart */}
            <div className="flex flex-col items-center justify-center p-4">
                <RadarChart data={radarData} />
            </div>

            {/* Key Strengths */}
            <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h4 className="text-[0.95rem] font-semibold text-gray-800 mb-4 pb-3 border-b border-gray-100">
                    Key Strengths
                </h4>
                <div className="flex flex-col gap-3">
                    {STRENGTHS.map((strength, i) => (
                        <motion.div
                            key={i}
                            className="flex items-center gap-2.5 text-sm text-gray-700"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + i * 0.1 }}
                        >
                            <span className="w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center shrink-0">
                                <Check size={12} strokeWidth={3} />
                            </span>
                            {strength}
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Areas for Focus */}
            <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h4 className="text-[0.95rem] font-semibold text-gray-800 mb-4 pb-3 border-b border-gray-100">
                    Areas for Focus
                </h4>
                <div className="flex flex-col gap-3">
                    {FOCUS_AREAS.map((area, i) => (
                        <motion.div
                            key={i}
                            className="flex items-center gap-2.5 text-sm text-gray-700"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 + i * 0.1 }}
                        >
                            <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                                <AlertTriangle size={12} strokeWidth={3} />
                            </span>
                            {area}
                        </motion.div>
                    ))}
                </div>
            </div>
        </motion.div>
    );
}
