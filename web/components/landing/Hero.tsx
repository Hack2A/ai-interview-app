"use client";

import { navigate } from "@/lib/navigation";
import { motion } from "framer-motion";

export default function Hero() {
    return (
        <section className="relative min-h-screen bg-linear-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A] overflow-hidden">

            <div className="relative max-w-7xl mx-auto px-6 pt-25 pb-24 lg:pb-32">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    {/* Left: Text Content */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                        className="space-y-8"
                    >
                        <div className="inline-flex items-center px-4 py-2 bg-[#7C3AED]/10 border border-[#7C3AED]/30 rounded-full backdrop-blur-sm">
                            <span className="text-[#10B981] text-sm font-medium">🔒 Enterprise-Grade Security</span>
                        </div>

                        <h1 className="text-5xl lg:text-7xl font-bold text-[#F1F5F9] leading-tight">
                            Unbreakable Digital Security.{" "}
                            <span className="bg-linear-to-r from-[#7C3AED] to-[#10B981] bg-clip-text text-transparent">
                                Immutable by Design.
                            </span>
                        </h1>

                        <p className="text-xl text-[#94A3B8] leading-relaxed max-w-xl">
                            Cryptrael Vault combines military-grade AES-256 encryption with blockchain-powered integrity verification.
                            Your data isn't just encrypted—it's cryptographically sealed and auditable forever.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-4">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] text-white font-semibold rounded-2xl shadow-lg shadow-[#7C3AED]/30 hover:shadow-[#7C3AED]/50 transition-all"
                                onClick={() => navigate("/register")}
                            >
                                Get Started
                            </motion.button>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-transparent border-2 border-[#7C3AED] text-[#F1F5F9] font-semibold rounded-2xl hover:bg-[#7C3AED]/10 transition-all"
                            >
                                View Architecture
                            </motion.button>
                        </div>

                        {/* Trust Indicators */}
                        <div className="flex items-center gap-8 pt-8">
                            <div>
                                <div className="text-3xl font-bold text-[#F1F5F9]">256-bit</div>
                                <div className="text-sm text-[#94A3B8]">AES Encryption</div>
                            </div>
                            <div className="w-px h-12 bg-[#94A3B8]/20"></div>
                            <div>
                                <div className="text-3xl font-bold text-[#F1F5F9]">99.99%</div>
                                <div className="text-sm text-[#94A3B8]">Uptime SLA</div>
                            </div>
                            <div className="w-px h-12 bg-[#94A3B8]/20"></div>
                            <div>
                                <div className="text-3xl font-bold text-[#F1F5F9]">SOC 2</div>
                                <div className="text-sm text-[#94A3B8]">Compliant</div>
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
                        <div className="relative w-full h-125 rounded-2xl bg-linear-to-br from-[#1E293B] to-[#0F172A] border border-[#7C3AED]/30 shadow-2xl shadow-[#7C3AED]/30 overflow-hidden">
                            {/* Animated background elements */}
                            <div className="absolute inset-0">
                                <div className="absolute top-20 left-20 w-32 h-32 bg-[#7C3AED] rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
                                <div className="absolute top-40 right-20 w-32 h-32 bg-[#10B981] rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
                                <div className="absolute bottom-20 left-40 w-32 h-32 bg-[#5B21B6] rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>
                            </div>

                            {/* Central vault icon */}
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
                                        className="w-64 h-64 text-[#7C3AED]"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={0.5}
                                            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 bg-[#7C3AED] blur-2xl opacity-20"></div>
                                </motion.div>
                            </div>

                            {/* Floating security badges */}
                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                                className="absolute top-10 right-10 px-4 py-2 bg-[#10B981]/20 border border-[#10B981]/50 rounded-lg backdrop-blur-sm"
                            >
                                <span className="text-[#10B981] text-sm font-semibold">✓ Encrypted</span>
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                                className="absolute bottom-10 left-10 px-4 py-2 bg-[#7C3AED]/20 border border-[#7C3AED]/50 rounded-lg backdrop-blur-sm"
                            >
                                <span className="text-[#7C3AED] text-sm font-semibold">⛓ Blockchain</span>
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 2 }}
                                className="absolute top-40 left-10 px-4 py-2 bg-[#F59E0B]/20 border border-[#F59E0B]/50 rounded-lg backdrop-blur-sm"
                            >
                                <span className="text-[#F59E0B] text-sm font-semibold">🔐 Secure</span>
                            </motion.div>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Bottom gradient fade */}
            <div className="absolute bottom-0 left-0 right-0 h-32 bg-linear-to-t from-[#0F172A] to-transparent"></div>
        </section>
    );
}
