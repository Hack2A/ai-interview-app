"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import DashboardTabs, { Tab } from "./DashboardTabs";
import PastInterviews from "./PastInterviews";
import PerformanceMetrics from "./PerformanceMetrics";
import SkillInsights from "./SkillInsights";

const TABS: Tab[] = [
    { id: "past-interviews", label: "Past Interviews" },
    { id: "performance-metrics", label: "Performance Metrics", badge: "Active" },
    { id: "skill-insights", label: "Skill Insights" },
];

const tabContent: Record<string, React.ReactNode> = {
    "past-interviews": <PastInterviews />,
    "performance-metrics": <PerformanceMetrics />,
    "skill-insights": <SkillInsights />,
};

export default function DashboardSection() {
    const [activeTab, setActiveTab] = useState("past-interviews");

    return (
        <section className="w-[90%] mx-auto px-20 pb-10">
            {/* Gradient Divider */}
            <div className="h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent" />

            {/* Dashboard Card */}
            <div className="mt-6 bg-white rounded-2xl shadow-sm border border-black/[0.04] px-10 py-8"
                 style={{ boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)" }}>
                <DashboardTabs
                    tabs={TABS}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                />

                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        transition={{ duration: 0.25, ease: "easeInOut" }}
                    >
                        {tabContent[activeTab]}
                    </motion.div>
                </AnimatePresence>
            </div>
        </section>
    );
}
