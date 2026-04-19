"use client";

import { Settings, User, Bell, Shield, Palette, Globe } from "lucide-react";
import { useState } from "react";

const SETTINGS_SECTIONS = [
    {
        id: "account",
        icon: User,
        label: "Account",
        settings: [
            { label: "Display Name", type: "text", value: "Username", placeholder: "Your display name" },
            { label: "Email", type: "text", value: "user@email.com", placeholder: "Your email address" },
            { label: "Bio", type: "textarea", value: "", placeholder: "Tell us about yourself" },
        ],
    },
    {
        id: "notifications",
        icon: Bell,
        label: "Notifications",
        settings: [
            { label: "Email Notifications", type: "toggle", value: true },
            { label: "Session Reminders", type: "toggle", value: true },
            { label: "Weekly Performance Summary", type: "toggle", value: false },
            { label: "New Feature Announcements", type: "toggle", value: true },
        ],
    },
    {
        id: "privacy",
        icon: Shield,
        label: "Privacy & Security",
        settings: [
            { label: "Two-factor Authentication", type: "toggle", value: false },
            { label: "Show Profile Publicly", type: "toggle", value: true },
            { label: "Allow Performance Data Collection", type: "toggle", value: true },
        ],
    },
    {
        id: "appearance",
        icon: Palette,
        label: "Appearance",
        settings: [
            { label: "Theme", type: "select", value: "light", options: ["Light", "Dark", "System"] },
            { label: "Compact Mode", type: "toggle", value: false },
        ],
    },
    {
        id: "language",
        icon: Globe,
        label: "Language & Region",
        settings: [
            { label: "Language", type: "select", value: "english", options: ["English", "Spanish", "French", "German", "Hindi"] },
            { label: "Timezone", type: "select", value: "ist", options: ["IST (UTC+5:30)", "EST (UTC-5)", "PST (UTC-8)", "GMT (UTC+0)"] },
        ],
    },
];

export default function SettingsPage() {
    const [activeSection, setActiveSection] = useState("account");

    const currentSection = SETTINGS_SECTIONS.find((s) => s.id === activeSection);

    return (
        <div className="w-[90%] max-w-5xl mx-auto px-6 py-10">
            {/* Header */}
            <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 bg-gray-100 rounded-xl flex items-center justify-center">
                    <Settings size={20} className="text-gray-600" />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
                    <p className="text-sm text-gray-400">Manage your account and preferences</p>
                </div>
            </div>

            <div className="flex gap-8">
                {/* Sidebar */}
                <div className="w-56 shrink-0">
                    <nav className="flex flex-col gap-1">
                        {SETTINGS_SECTIONS.map((section) => (
                            <button
                                key={section.id}
                                onClick={() => setActiveSection(section.id)}
                                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 cursor-pointer text-left
                                    ${activeSection === section.id
                                        ? "bg-blue-50 text-blue-600"
                                        : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"}`}
                            >
                                <section.icon size={16} />
                                {section.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content */}
                <div className="flex-1 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                    {currentSection && (
                        <div>
                            <h2 className="text-lg font-semibold text-gray-800 mb-6">{currentSection.label}</h2>
                            <div className="flex flex-col gap-6">
                                {currentSection.settings.map((setting, i) => (
                                    <div key={i} className="flex items-center justify-between py-1">
                                        <label className="text-sm font-medium text-gray-600">{setting.label}</label>
                                        {setting.type === "text" && (
                                            <input
                                                type="text"
                                                defaultValue={setting.value as string}
                                                placeholder={setting.placeholder}
                                                className="w-64 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-300 transition-all"
                                            />
                                        )}
                                        {setting.type === "textarea" && (
                                            <textarea
                                                defaultValue={setting.value as string}
                                                placeholder={setting.placeholder}
                                                rows={2}
                                                className="w-64 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-300 transition-all resize-none"
                                            />
                                        )}
                                        {setting.type === "toggle" && (
                                            <div className="w-10 h-5 bg-gray-200 rounded-full relative cursor-pointer">
                                                <div className={`absolute top-0.5 w-4 h-4 rounded-full transition-all shadow-sm ${(setting.value as boolean) ? "right-0.5 bg-blue-500" : "left-0.5 bg-white"}`} />
                                            </div>
                                        )}
                                        {setting.type === "select" && (
                                            <select className="w-64 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-300 transition-all bg-white cursor-pointer">
                                                {(setting.options as string[])?.map((opt) => (
                                                    <option key={opt} value={opt.toLowerCase()}>
                                                        {opt}
                                                    </option>
                                                ))}
                                            </select>
                                        )}
                                    </div>
                                ))}
                            </div>
                            <div className="mt-8 pt-6 border-t border-gray-100 flex justify-end">
                                <button className="px-6 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-sm shadow-blue-300/30 cursor-pointer">
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
