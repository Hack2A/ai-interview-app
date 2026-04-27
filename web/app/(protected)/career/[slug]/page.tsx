"use client";

import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

import CareerToolForm from "@/components/career/CareerToolForm";
import CareerResultDisplay from "@/components/career/CareerResultDisplay";
import { executeCareerAction } from "@/services/careerService";
import {
    getCareerOptionBySlug,
    CAREER_ICONS,
    CAREER_GRADIENTS,
} from "@/lib/careerConfig";

export default function CareerToolPage() {
    const params = useParams();
    const router = useRouter();
    const slug = params.slug as string;

    const option = getCareerOptionBySlug(slug);

    const [result, setResult] = useState<Record<string, unknown> | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    if (!option) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50/30 px-6">
                <div className="text-center">
                    <div className="text-6xl mb-4">🔍</div>
                    <h1 className="text-2xl font-bold text-gray-800 mb-2">
                        Tool Not Found
                    </h1>
                    <p className="text-gray-500 mb-6">
                        The career tool &quot;{slug}&quot; doesn&apos;t exist.
                    </p>
                    <Link
                        href="/career"
                        className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl font-medium text-sm
                            hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/25"
                    >
                        <ArrowLeft size={16} />
                        Back to Career Hub
                    </Link>
                </div>
            </div>
        );
    }

    const Icon = CAREER_ICONS[option.id];
    const gradient = CAREER_GRADIENTS[option.id];
    const accentColor = gradient.from;

    const handleSubmit = async (formData: Record<string, string>) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const payload = {
                action: option.id,
                ...formData,
            };
            const data = await executeCareerAction(payload);
            setResult(data);
        } catch (err: unknown) {
            if (err && typeof err === "object" && "response" in err) {
                const axiosErr = err as {
                    response?: { status: number; data?: { error?: string; detail?: string } };
                };
                if (axiosErr.response?.status === 400) {
                    setError(
                        axiosErr.response.data?.error ||
                            axiosErr.response.data?.detail ||
                            "Invalid request. Please check your inputs.",
                    );
                } else if (axiosErr.response?.status === 503) {
                    setError(
                        "The AI engine is temporarily unavailable. Please try again later.",
                    );
                } else {
                    setError("An unexpected error occurred. Please try again.");
                }
            } else {
                setError("Network error. Please check your connection.");
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
            {/* Header */}
            <div className="relative overflow-hidden">
                {/* Background glow */}
                <div className="absolute inset-0 pointer-events-none">
                    <div
                        className="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 opacity-20"
                        style={{ backgroundColor: accentColor }}
                    />
                </div>

                <div className="relative max-w-3xl mx-auto px-6 pt-10 pb-8">
                    {/* Breadcrumb */}
                    <Link
                        href="/career"
                        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 
                            transition-colors mb-6 group"
                    >
                        <ArrowLeft
                            size={14}
                            className="transition-transform group-hover:-translate-x-0.5"
                        />
                        Career Hub
                    </Link>

                    <div className="flex items-center gap-4">
                        {/* Icon */}
                        <div
                            className="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg shrink-0"
                            style={{
                                background: `linear-gradient(135deg, ${gradient.from}, ${gradient.to})`,
                                boxShadow: `0 8px 24px ${gradient.from}30`,
                            }}
                        >
                            <Icon
                                size={26}
                                strokeWidth={2}
                                className="text-white"
                            />
                        </div>
                        <div>
                            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
                                {option.title}
                            </h1>
                            <p className="text-sm text-gray-500 mt-0.5">
                                {option.description}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="max-w-3xl mx-auto px-6 pb-20 space-y-8">
                {/* Form Card */}
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 lg:p-8">
                    <h2 className="text-sm font-bold text-gray-600 uppercase tracking-wider mb-5">
                        Input
                    </h2>
                    <CareerToolForm
                        inputs={option.inputs}
                        onSubmit={handleSubmit}
                        isLoading={isLoading}
                        accentColor={accentColor}
                    />
                </div>

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex items-start gap-3">
                        <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center shrink-0 mt-0.5">
                            <span className="text-red-500 text-lg">!</span>
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-red-700 mb-0.5">
                                Error
                            </p>
                            <p className="text-sm text-red-600">{error}</p>
                        </div>
                    </div>
                )}

                {/* Result */}
                {result && (
                    <div className="animate-fade-in">
                        <h2 className="text-sm font-bold text-gray-600 uppercase tracking-wider mb-4">
                            Output
                        </h2>
                        <CareerResultDisplay
                            result={result}
                            accentColor={accentColor}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}
