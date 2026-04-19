"use client";

import { motion } from "framer-motion";

const features = [
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
        ),
        title: "Resume Upload & ATS Score",
        description: "Upload your resume and get instant ATS (Applicant Tracking System) score analysis. Identify areas for improvement and optimize your resume to pass through automated screening systems."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
        ),
        title: "Diverse Interview Types",
        description: "Practice with technical, HR, behavioral, JavaScript-based, and skill-specific interviews. Choose from pre-built options or get a curated interview experience tailored to your specific needs and target role."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
        ),
        title: "Flexible Interview Modes",
        description: "Choose your comfort level: practice with audio-only interviews or enable video sharing for a more realistic experience. AI conducts intelligent, context-aware interviews that adapt to your responses."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
        ),
        title: "Detailed Interview Analytics",
        description: "Get comprehensive post-interview summaries with performance insights. Download detailed reports, review transcripts anytime, and track your progress across multiple practice sessions to improve continuously."
    }
];

export default function WhyChooseUs() {
    return (
        <section className="relative py-24 bg-white">
            <div className="max-w-7xl mx-auto px-6">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl lg:text-5xl font-bold text-[#1E293B] mb-4">
                        Why Choose IntrvAI?
                    </h2>
                    <p className="text-xl text-[#475569] max-w-2xl mx-auto">
                        AI-powered interview preparation with comprehensive features to help you ace your next interview
                    </p>
                </motion.div>

                {/* Feature Grid */}
                <div className="grid md:grid-cols-2 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.6, delay: index * 0.1 }}
                            whileHover={{ y: -8, transition: { duration: 0.3 } }}
                            className="group relative"
                        >
                            {/* Card */}
                            <div className="relative h-full p-8 bg-white border border-[#E2E8F0] hover:border-blue-200 rounded-2xl hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                                {/* Glow effect on hover */}
                                <div className="absolute inset-0 rounded-2xl bg-linear-to-br from-blue-50/0 to-indigo-50/0 group-hover:from-blue-50/50 group-hover:to-indigo-50/50 transition-all duration-300"></div>

                                <div className="relative z-10">
                                    {/* Icon */}
                                    <div className="inline-flex items-center justify-center w-16 h-16 mb-6 bg-linear-to-br from-[#3B82F6] to-[#2563EB] rounded-xl text-white shadow-lg shadow-blue-500/30 group-hover:shadow-blue-500/50 transition-all duration-300">
                                        {feature.icon}
                                    </div>

                                    {/* Content */}
                                    <h3 className="text-2xl font-bold text-[#1E293B] mb-4">
                                        {feature.title}
                                    </h3>
                                    <p className="text-[#475569] leading-relaxed">
                                        {feature.description}
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
