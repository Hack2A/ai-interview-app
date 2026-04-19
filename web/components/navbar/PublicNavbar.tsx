"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

export default function PublicNavbar() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const scrollToSection = (sectionId: string) => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    return (
        <nav
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-in-out ${scrolled
                ? "bg-white/95 backdrop-blur-xl border-b border-[#E2E8F0] shadow-lg shadow-blue-100/50"
                : "bg-white border-b border-[#E2E8F0]"
                }`}
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

                    {/* Navigation Links */}
                    <ul className="hidden md:flex items-center gap-8">
                        <li>
                            <Link
                                href="/features"
                                className="text-[#475569] hover:text-[#2563EB] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#2563EB]"
                            >
                                Features
                            </Link>
                        </li>
                        <li>
                            <Link
                                href="/interviews"
                                className="text-[#475569] hover:text-[#2563EB] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#2563EB]"
                            >
                                Interviews
                            </Link>
                        </li>
                        <li>
                            <Link
                                href="/about"
                                className="text-[#475569] hover:text-[#2563EB] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#2563EB]"
                            >
                                About
                            </Link>
                        </li>
                    </ul>

                    {/* CTA Buttons */}
                    <div className="flex items-center gap-4">
                        <Link
                            href="/login"
                            className="hidden sm:block text-[#475569] hover:text-[#2563EB] transition-colors duration-200 font-medium outline-none focus:outline-none"
                        >
                            Log in
                        </Link>
                        <Link
                            href="/register"
                            className="px-6 py-2.5 bg-gradient-to-r from-[#3B82F6] to-[#2563EB] text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300 outline-none focus:outline-none focus:ring-2 focus:ring-blue-400/50"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}