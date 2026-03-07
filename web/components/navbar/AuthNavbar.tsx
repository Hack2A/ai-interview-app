"use client";

import Link from "next/link";

export default function AuthNavbar() {
    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out bg-transparent border-b border-transparent`}
        >
            <div className="max-w-[90%] mx-auto px-6 py-4">
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group outline-none focus:outline-none">
                        <div className="w-10 h-10 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-xl flex items-center justify-center shadow-lg shadow-[#7C3AED]/30 group-hover:shadow-[#7C3AED]/50 transition-all duration-300">
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
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                                />
                            </svg>
                        </div>
                        <span className="text-xl font-bold text-[#F1F5F9] group-hover:text-white transition-colors">
                            Cryptrael Vault
                        </span>
                    </Link>
                </div>
            </div>
        </nav>
    );
}