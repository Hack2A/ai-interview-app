"use client";

import {
    CircleUserRound, User, Settings, HelpCircle, FileText, LogOut, Bell,
    ChevronDown, Mic, BrainCircuit, FileSearch, BookOpen, Route, Users,
    Volume2, FileCode, Sparkles, FolderGit2, Github, Medal, ClipboardList,
    ScanEye, ShieldAlert
} from "lucide-react";
import Link from "next/link";
import { useState, useEffect, useRef } from "react";

const INTERVIEW_ITEMS = [
    { icon: Mic, label: "New Interview", href: "/interview/new", desc: "Start a new AI-powered mock interview" },
    { icon: FileText, label: "Past Interviews", href: "/home", desc: "Review your previous sessions" },
    { icon: ClipboardList, label: "My Reports", href: "/reports", desc: "Detailed performance reports" },
];

const CAREER_ITEMS = [
    { icon: FileSearch, label: "Match Report", href: "/career/match-report", desc: "Compare your profile to job postings" },
    { icon: FileCode, label: "Cover Letter Generator", href: "/career/cover-letter", desc: "AI-crafted cover letters" },
    { icon: BrainCircuit, label: "Skill Gap Analysis", href: "/career/skill-gap", desc: "Identify areas to improve" },
    { icon: Route, label: "Learning Roadmap Builder", href: "/career/roadmap", desc: "Personalized learning paths" },
    { icon: Users, label: "Recruiter Simulator", href: "/career/recruiter-sim", desc: "Practice with simulated recruiters" },
    { icon: Volume2, label: "Industry Tone Calibrator", href: "/career/tone-calibrator", desc: "Match your tone to the industry" },
    { icon: ScanEye, label: "Resume Parser", href: "/career/resume-parser", desc: "Parse and analyze your resume" },
    { icon: Sparkles, label: "Smart Resume Selector", href: "/career/smart-resume", desc: "Tailored LaTeX resume generation" },
    { icon: BookOpen, label: "Project Extraction", href: "/career/project-extract", desc: "Extract projects from raw text" },
    { icon: Github, label: "GitHub Repo Extraction", href: "/career/github-extract", desc: "Pull projects from GitHub repos" },
    { icon: Medal, label: "Project Ranking", href: "/career/project-ranking", desc: "Rank your projects against JDs" },
    { icon: FolderGit2, label: "JD Manager", href: "/career/jd-manager", desc: "Manage job descriptions" },
    { icon: ScanEye, label: "AI Tone Detector", href: "/career/tone-detector", desc: "Analyze tone in your writing" },
    { icon: ShieldAlert, label: "Bias & Redundancy Detector", href: "/career/bias-detector", desc: "Spot bias and redundancy" },
];

const PROFILE_ITEMS = [
    { icon: User, label: "Profile", href: "/profile" },
    { icon: Settings, label: "Settings", href: "/settings" },
    { icon: Bell, label: "Notifications", href: "/notifications" },
    { icon: HelpCircle, label: "Help & Support", href: "/support" },
];

export default function ProtectedNavbar() {
    const [scrolled, setScrolled] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
    const profileRef = useRef<HTMLDivElement>(null);
    const navRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
                setProfileOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <nav
            className={`transition-all duration-500 ease-in-out relative z-50 ${scrolled
                ? "bg-white/95 backdrop-blur-xl border-b border-[#E2E8F0] shadow-lg shadow-blue-100/50"
                : "bg-white border-b border-[#E2E8F0]"
                }`}
        >
            <div className="max-w-[90%] mx-auto px-6 py-4" ref={navRef}>
                <div className="flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/home" className="flex items-center gap-2 group outline-none focus:outline-none">
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

                    {/* Center Nav Items with Mega Dropdowns */}
                    <div className="flex items-center gap-1">
                        {/* Interview Dropdown */}
                        <div
                            className="relative"
                            onMouseEnter={() => setActiveDropdown("interview")}
                            onMouseLeave={() => setActiveDropdown(null)}
                        >
                            <button className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors duration-200 rounded-lg hover:bg-blue-50 cursor-pointer">
                                Interview
                                <ChevronDown size={14} className={`transition-transform duration-200 ${activeDropdown === "interview" ? "rotate-180" : ""}`} />
                            </button>

                            {activeDropdown === "interview" && (
                                <div className="absolute left-0 top-full pt-2 z-50">
                                    <div className="w-80 bg-white rounded-xl shadow-xl shadow-gray-200/80 border border-gray-100 py-2">
                                        <div className="px-4 py-2 border-b border-gray-100">
                                            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Interview Tools</p>
                                        </div>
                                        {INTERVIEW_ITEMS.map((menuItem) => (
                                            <Link
                                                key={menuItem.label}
                                                href={menuItem.href}
                                                className="flex items-start gap-3 px-4 py-3 hover:bg-blue-50 transition-colors duration-150 group"
                                            >
                                                <menuItem.icon size={18} strokeWidth={2} className="text-gray-400 group-hover:text-blue-500 mt-0.5 shrink-0 transition-colors" />
                                                <div>
                                                    <p className="text-sm font-medium text-gray-700 group-hover:text-blue-600 transition-colors">{menuItem.label}</p>
                                                    <p className="text-xs text-gray-400 mt-0.5">{menuItem.desc}</p>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Career Management Mega Dropdown */}
                        <div
                            className="relative"
                            onMouseEnter={() => setActiveDropdown("career")}
                            onMouseLeave={() => setActiveDropdown(null)}
                        >
                            <button className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-gray-600 hover:text-blue-600 transition-colors duration-200 rounded-lg hover:bg-blue-50 cursor-pointer">
                                Career Management
                                <ChevronDown size={14} className={`transition-transform duration-200 ${activeDropdown === "career" ? "rotate-180" : ""}`} />
                            </button>

                            {activeDropdown === "career" && (
                                <div className="absolute left-1/2 -translate-x-1/2 top-full pt-2 z-50">
                                <div className="w-[640px] bg-white rounded-xl shadow-xl shadow-gray-200/80 border border-gray-100 py-2">
                                    <div className="px-5 py-2 border-b border-gray-100">
                                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Career Management Tools</p>
                                    </div>
                                    <div className="grid grid-cols-2 p-2">
                                        {CAREER_ITEMS.map((menuItem) => (
                                            <Link
                                                key={menuItem.label}
                                                href={menuItem.href}
                                                className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-blue-50 transition-colors duration-150 group"
                                            >
                                                <menuItem.icon size={16} strokeWidth={2} className="text-gray-400 group-hover:text-blue-500 mt-0.5 shrink-0 transition-colors" />
                                                <div>
                                                    <p className="text-sm font-medium text-gray-700 group-hover:text-blue-600 transition-colors">{menuItem.label}</p>
                                                    <p className="text-[11px] text-gray-400 leading-tight mt-0.5">{menuItem.desc}</p>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right: Profile Button + Dropdown */}
                    <div className="relative" ref={profileRef}>
                        <button
                            onClick={() => setProfileOpen(!profileOpen)}
                            className="px-2.5 py-2.5 bg-linear-to-r from-[#3B82F6] to-[#2563EB] text-white font-semibold rounded-full shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300 outline-none focus:outline-none focus:ring-2 focus:ring-blue-400/50 flex items-center gap-1 cursor-pointer"
                        >
                            <CircleUserRound />
                        </button>

                        {profileOpen && (
                            <div className="absolute right-0 mt-3 w-56 bg-white rounded-xl shadow-xl shadow-gray-200/80 border border-gray-100 py-2 z-50">
                                <div className="px-4 py-3 border-b border-gray-100">
                                    <p className="text-sm font-semibold text-gray-800">Username</p>
                                    <p className="text-xs text-gray-400 mt-0.5">user@email.com</p>
                                </div>
                                <div className="py-1">
                                    {PROFILE_ITEMS.map((menuItem) => (
                                        <Link
                                            key={menuItem.label}
                                            href={menuItem.href}
                                            className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-600 hover:bg-blue-50 hover:text-blue-600 transition-colors duration-150"
                                            onClick={() => setProfileOpen(false)}
                                        >
                                            <menuItem.icon size={16} strokeWidth={2} />
                                            {menuItem.label}
                                        </Link>
                                    ))}
                                </div>
                                <div className="border-t border-gray-100 pt-1">
                                    <button
                                        className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors duration-150 w-full cursor-pointer"
                                        onClick={() => {
                                            setProfileOpen(false);
                                            // TODO: handle logout
                                        }}
                                    >
                                        <LogOut size={16} strokeWidth={2} />
                                        Sign Out
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}