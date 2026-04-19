"use client";

import { motion } from "framer-motion";

export interface Tab {
    id: string;
    label: string;
    badge?: string;
}

interface DashboardTabsProps {
    tabs: Tab[];
    activeTab: string;
    onTabChange: (tabId: string) => void;
}

export default function DashboardTabs({
    tabs,
    activeTab,
    onTabChange,
}: DashboardTabsProps) {
    return (
        <div className="flex gap-1 border-b border-gray-200 mb-8 relative">
            {tabs.map((tab) => {
                const isActive = tab.id === activeTab;
                return (
                    <button
                        key={tab.id}
                        className={`px-5 py-3 text-sm font-medium relative flex items-center gap-2 cursor-pointer bg-transparent border-none transition-colors duration-200
                            ${isActive ? "text-gray-800 font-semibold" : "text-gray-400 hover:text-gray-500"}`}
                        onClick={() => onTabChange(tab.id)}
                    >
                        {tab.label}
                        {tab.badge && (
                            <span className="text-[0.65rem] font-semibold px-1.5 py-0.5 rounded bg-blue-100 text-blue-600 tracking-wide">
                                {tab.badge}
                            </span>
                        )}
                        {isActive && (
                            <motion.div
                                className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-blue-500 rounded-t-sm"
                                layoutId="tab-indicator"
                                transition={{
                                    type: "spring",
                                    stiffness: 500,
                                    damping: 35,
                                }}
                            />
                        )}
                    </button>
                );
            })}
        </div>
    );
}
