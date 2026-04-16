"use client";

import { navigate } from "@/lib/navigation";
import { motion } from "framer-motion";

export default function Hero() {
    return (
        <section className="relative min-h-screen bg-linear-to-br from-white via-blue-50/30 to-white overflow-hidden">

            <div className="relative max-w-7xl mx-auto px-6 pt-25 pb-24 lg:pb-32">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Left: Text Content */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="space-y-8"
                    >
                        <div className="inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-full">
                            <span className="text-[#2563EB] text-sm font-medium">🎯 AI-Powered Interview Mastery</span>
                        </div>

                        <h1 className="text-5xl lg:text-7xl font-bold text-[#1E293B] leading-tight">
                            Ace Your Interview.{" "}
                            <span className="bg-gradient-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
                                Powered by AI.
                            </span>
                        </h1>

                        <p className="text-xl text-[#475569] leading-relaxed max-w-xl">
                            IntrvAI helps you master interview skills with AI-powered practice sessions.
                            Upload your resume, get ATS scores, and practice with realistic AI interviews tailored to your needs.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-gradient-to-r from-[#3B82F6] to-[#2563EB] text-white font-semibold rounded-2xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 transition-all"
                                onClick={() => navigate("/register")}
                            >
                                Start Practicing
                            </motion.button>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-white border-2 border-[#2563EB] text-[#2563EB] font-semibold rounded-2xl hover:bg-blue-50 transition-all"
                                onClick={() => navigate("/features")}
                            >
                                View Features
                            </motion.button>
                        </div>

                        {/* Trust Indicators */}
                        <div className="flex items-center gap-8 pt-8">
                            <div>
                                <div className="text-3xl font-bold text-[#1E293B]">AI-Powered</div>
                                <div className="text-sm text-[#475569]">Interviews</div>
                            </div>
                            <div className="w-px h-12 bg-[#E2E8F0]"></div>
                            <div>
                                <div className="text-3xl font-bold text-[#1E293B]">ATS</div>
                                <div className="text-sm text-[#475569]">Score Checker</div>
                            </div>
                            <div className="w-px h-12 bg-[#E2E8F0]"></div>
                            <div>
                                <div className="text-3xl font-bold text-[#1E293B]">Multiple</div>
                                <div className="text-sm text-[#475569]">Interview Types</div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Right: Illustration */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1, delay: 0.2 }}
                        className="relative hidden lg:block"
                    >
                        <div className="relative w-full h-125 rounded-2xl bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-2xl shadow-blue-200/50 overflow-hidden">
                            {/* Animated background elements */}
                            <div className="absolute inset-0">
                                <div className="absolute top-20 left-20 w-32 h-32 bg-[#3B82F6] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
                                <div className="absolute top-40 right-20 w-32 h-32 bg-[#10B981] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
                                <div className="absolute bottom-20 left-40 w-32 h-32 bg-[#2563EB] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
                            </div>

                            {/* Central icon */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <motion.div
                                    animate={{
                                        rotate: [0, 5, -5, 0],
                                        scale: [1, 1.05, 1]
                                    }}
                                    transition={{
                                        duration: 6,
                                        repeat: Infinity,
                                        ease: "easeInOut"
                                    }}
                                    className="relative"
                                >
                                    <svg
                                        className="w-64 h-64 text-[#2563EB]"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={0.5}
                                            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 bg-[#2563EB] blur-2xl opacity-10"></div>
                                </motion.div>
                            </div>

                            {/* Floating badges */}
                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                                className="absolute top-10 right-10 px-4 py-2 bg-green-50 border border-green-200 rounded-lg shadow-sm"
                            >
                                <span className="text-[#10B981] text-sm font-semibold">🎯 AI Interviews</span>
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                                className="absolute bottom-10 left-10 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg shadow-sm"
                            >
                                <span className="text-[#2563EB] text-sm font-semibold">📊 ATS Score</span>
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                                className="absolute top-40 left-10 px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg shadow-sm"
                            >
                                <span className="text-[#F59E0B] text-sm font-semibold">📝 Summaries</span>
                            </motion.div>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Bottom gradient fade */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-white to-transparent"></div>
        </section>
    );
}
