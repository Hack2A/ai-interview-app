"use client";

import Link from "next/link";

export default function AuthNavbar() {
    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out bg-white/80 backdrop-blur-md border-b border-[#E2E8F0]`}
        >
            <div className="max-w-[90%] mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group outline-none focus:outline-none">
                        <div className="w-10 h-10 bg-linear-to-br from-[#3B82F6] to-[#2563EB] rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:shadow-blue-500/50 transition-all duration-300">
                            <svg
                                className="w-6 h-6 text-white"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                                />
                            </svg>
                        </div>
                        <span className="text-xl font-bold text-[#1E293B] group-hover:text-[#2563EB] transition-colors">
                            IntrvAI
                        </span>
                    </Link>
                </div>
            </div>
        </nav>
    );
}