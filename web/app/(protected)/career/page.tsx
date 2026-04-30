"use client";

import { Sparkles } from "lucide-react";
import CareerToolCard from "@/components/career/CareerToolCard";
import {
    CAREER_OPTIONS,
    CAREER_ICONS,
    CAREER_GRADIENTS,
    toSlug,
} from "@/lib/careerConfig";

export default function CareerHubPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                {/* Background decorations */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-blue-100/40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
                    <div className="absolute bottom-0 left-0 w-72 h-72 bg-purple-100/30 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
                </div>

                <div className="relative max-w-6xl mx-auto px-6 pt-16 pb-10">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                            <Sparkles size={20} className="text-white" />
                        </div>
                        <span className="text-xs font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full">
                            AI-Powered
                        </span>
                    </div>
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-3 tracking-tight">
                        Career Management
                    </h1>
                    <p className="text-lg text-gray-500 max-w-2xl leading-relaxed">
                        Leverage AI to match resumes, generate cover letters,
                        identify skill gaps, and accelerate your career growth.
                    </p>
                </div>
            </div>

            {/* Tools Grid */}
            <div className="max-w-6xl mx-auto px-6 pb-20">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                    {CAREER_OPTIONS.map((option) => (
                        <CareerToolCard
                            key={option.id}
                            icon={CAREER_ICONS[option.id]}
                            title={option.title}
                            description={option.description}
                            href={`/career/${toSlug(option.id)}`}
                            gradient={CAREER_GRADIENTS[option.id]}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
