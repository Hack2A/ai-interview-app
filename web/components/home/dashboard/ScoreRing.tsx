"use client";

import { useEffect, useState } from "react";

interface ScoreRingProps {
    score: number;
    maxScore?: number;
    size?: number;
    strokeWidth?: number;
    color?: string;
}

export default function ScoreRing({
    score,
    maxScore = 100,
    size = 56,
    strokeWidth = 4,
    color = "#3b82f6",
}: ScoreRingProps) {
    const [mounted, setMounted] = useState(false);

    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const progress = Math.min(score / maxScore, 1);
    const offset = circumference * (1 - progress);

    useEffect(() => {
        const timer = setTimeout(() => setMounted(true), 50);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
            <svg
                className="-rotate-90"
                width={size}
                height={size}
                viewBox={`0 0 ${size} ${size}`}
            >
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    strokeWidth={strokeWidth}
                    fill="none"
                    stroke="#e5e7eb"
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    strokeWidth={strokeWidth}
                    fill="none"
                    stroke={color}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={mounted ? offset : circumference}
                    className="transition-[stroke-dashoffset] duration-1000 ease-out"
                />
            </svg>
            <div className="absolute flex flex-col items-center justify-center leading-none">
                <span
                    className="font-bold text-gray-800"
                    style={{ fontSize: size * 0.28 }}
                >
                    {score}
                </span>
                <span className="text-gray-400 font-medium" style={{ fontSize: size * 0.16 }}>
                    /{maxScore}
                </span>
            </div>
        </div>
    );
}
