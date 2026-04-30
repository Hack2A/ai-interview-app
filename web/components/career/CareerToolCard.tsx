"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { ArrowRight } from "lucide-react";

interface CareerToolCardProps {
    icon: LucideIcon;
    title: string;
    description: string;
    href: string;
    gradient: { from: string; to: string };
}

export default function CareerToolCard({
    icon: Icon,
    title,
    description,
    href,
    gradient,
}: CareerToolCardProps) {
    return (
        <Link href={href} className="group block outline-none focus:outline-none">
            <div
                className="relative overflow-hidden rounded-2xl border border-gray-100 bg-white 
                    p-6 transition-all duration-300
                    hover:shadow-xl hover:-translate-y-1 hover:border-transparent"
                style={{
                    // @ts-ignore
                    "--card-accent": gradient.from,
                } as React.CSSProperties}
            >
                {/* Gradient glow on hover */}
                <div
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{
                        background: `linear-gradient(135deg, ${gradient.from}06, ${gradient.to}10)`,
                    }}
                />

                {/* Icon badge */}
                <div
                    className="relative w-12 h-12 rounded-xl flex items-center justify-center mb-4
                        shadow-lg transition-transform duration-300 group-hover:scale-110"
                    style={{
                        background: `linear-gradient(135deg, ${gradient.from}, ${gradient.to})`,
                        boxShadow: `0 6px 20px ${gradient.from}30`,
                    }}
                >
                    <Icon size={22} strokeWidth={2} className="text-white" />
                </div>

                {/* Text */}
                <h3 className="relative text-base font-bold text-gray-800 mb-1.5 group-hover:text-gray-900 transition-colors">
                    {title}
                </h3>
                <p className="relative text-sm text-gray-500 leading-relaxed mb-4">
                    {description}
                </p>

                {/* CTA */}
                <div
                    className="relative flex items-center gap-1.5 text-sm font-semibold transition-all duration-300
                        group-hover:gap-2.5"
                    style={{ color: gradient.from }}
                >
                    Open Tool
                    <ArrowRight
                        size={14}
                        className="transition-transform duration-300 group-hover:translate-x-1"
                    />
                </div>
            </div>
        </Link>
    );
}
