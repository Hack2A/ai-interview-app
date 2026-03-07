"use client";

import { motion } from "framer-motion";

const features = [
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
        ),
        title: "End-to-End AES-256 Encryption",
        description: "Military-grade encryption ensures your data is protected at rest and in transit. Zero-knowledge architecture means only you hold the keys to your vault."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
        ),
        title: "Blockchain-Based Integrity Verification",
        description: "Every file upload generates a cryptographic hash stored on an immutable blockchain ledger, providing tamper-proof verification and complete data provenance."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
        ),
        title: "Zero-Trust Access Control",
        description: "Granular permission management with multi-factor authentication, biometric verification, and role-based access policies. Trust nothing, verify everything."
    },
    {
        icon: (
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
        ),
        title: "Immutable Audit Trails",
        description: "Comprehensive logging of all access events with cryptographic timestamps. Meet compliance requirements with SOC 2, GDPR, and HIPAA-ready audit capabilities."
    }
];

export default function WhyChooseUs() {
    return (
        <section className="relative py-24 bg-[#0F172A]">
            <div className="max-w-7xl mx-auto px-6">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl lg:text-5xl font-bold text-[#F1F5F9] mb-4">
                        Why Choose Cryptrael Vault?
                    </h2>
                    <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
                        Enterprise-grade security built on cryptographic foundations and blockchain immutability
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
                            <div className="relative h-full p-8 bg-linear-to-br from-[#1E293B]/60 to-[#1E293B]/30 backdrop-blur-xl rounded-2xl border border-[#7C3AED]/20 hover:border-[#7C3AED]/50 transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-[#7C3AED]/10">
                                {/* Glow effect on hover */}
                                <div className="absolute inset-0 rounded-2xl bg-linear-to-br from-[#7C3AED]/0 to-[#10B981]/0 group-hover:from-[#7C3AED]/5 group-hover:to-[#10B981]/5 transition-all duration-300"></div>

                                <div className="relative z-10">
                                    {/* Icon */}
                                    <div className="inline-flex items-center justify-center w-16 h-16 mb-6 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-xl text-white shadow-lg shadow-[#7C3AED]/30 group-hover:shadow-[#7C3AED]/50 transition-all duration-300">
                                        {feature.icon}
                                    </div>

                                    {/* Content */}
                                    <h3 className="text-2xl font-bold text-[#F1F5F9] mb-4">
                                        {feature.title}
                                    </h3>
                                    <p className="text-[#94A3B8] leading-relaxed">
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
