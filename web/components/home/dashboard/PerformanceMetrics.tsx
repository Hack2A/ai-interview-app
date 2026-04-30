"use client";

import { motion, Variants } from "framer-motion";
import MetricCard from "./MetricCard";

const METRICS = [
    {
        title: "Overall Score Trend",
        value: 87,
        trend: "+5% from last week",
        trendPositive: true,
        sparklineData: [52, 58, 55, 68, 72, 75, 80, 87],
    },
    {
        title: "Communication Clarity",
        value: 91,
        trend: "+3% from last week",
        trendPositive: true,
        sparklineData: [65, 68, 72, 78, 82, 85, 88, 91],
    },
    {
        title: "Technical Accuracy",
        value: 82,
        trend: "+2% from last week",
        trendPositive: true,
        sparklineData: [55, 60, 58, 65, 70, 74, 78, 82],
    },
];

const container: Variants = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: { staggerChildren: 0.1 },
    },
};

const item: Variants = {
    hidden: { opacity: 0, y: 16 },
    show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: "easeOut" } },
};

export default function PerformanceMetrics() {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Performance Metrics
            </h3>
            <motion.div
                className="grid grid-cols-3 gap-4"
                variants={container}
                initial="hidden"
                animate="show"
            >
                {METRICS.map((metric) => (
                    <motion.div key={metric.title} variants={item}>
                        <MetricCard
                            title={metric.title}
                            value={metric.value}
                            trend={metric.trend}
                            trendPositive={metric.trendPositive}
                            sparklineData={metric.sparklineData}
                        />
                    </motion.div>
                ))}
            </motion.div>
        </div>
    );
}
