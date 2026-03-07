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
                ? "bg-[#0F172A]/80 backdrop-blur-xl border-b border-[#7C3AED]/20 shadow-lg shadow-[#7C3AED]/5"
                : "bg-transparent border-b border-transparent"
                }`}
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

                    {/* Navigation Links */}
                    <ul className="hidden md:flex items-center gap-8">
                        <li>
                            <button
                                onClick={() => scrollToSection("features")}
                                className="text-[#94A3B8] hover:text-[#10B981] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#10B981] cursor-pointer"
                            >
                                Features
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => scrollToSection("security")}
                                className="text-[#94A3B8] hover:text-[#10B981] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#10B981] cursor-pointer"
                            >
                                Security
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => scrollToSection("pricing")}
                                className="text-[#94A3B8] hover:text-[#10B981] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#10B981] cursor-pointer"
                            >
                                Pricing
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={() => scrollToSection("docs")}
                                className="text-[#94A3B8] hover:text-[#10B981] transition-colors duration-200 font-medium outline-none focus:outline-none focus:text-[#10B981] cursor-pointer"
                            >
                                Docs
                            </button>
                        </li>
                    </ul>

                    {/* CTA Buttons */}
                    <div className="flex items-center gap-4">
                        <Link
                            href="/login"
                            className="hidden sm:block text-[#F1F5F9] hover:text-white transition-colors duration-200 font-medium outline-none focus:outline-none"
                        >
                            Log in
                        </Link>
                        <Link
                            href="/register"
                            className="px-6 py-2.5 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] text-white font-semibold rounded-xl shadow-lg shadow-[#7C3AED]/30 hover:shadow-[#7C3AED]/50 hover:scale-105 transition-all duration-300 outline-none focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/50"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}