"use client";

import { motion } from "framer-motion";

const testimonials = [
    {
        name: "Sarah Chen",
        role: "Chief Security Officer, TechCorp",
        avatar: "SC",
        review: "Cryptrael Vault transformed how we handle sensitive client data. The blockchain audit trail gives us complete confidence in our compliance reporting.",
        rating: 5
    },
    {
        name: "Marcus Rodriguez",
        role: "CTO, FinanceHub",
        avatar: "MR",
        review: "We evaluated 12 different solutions. Cryptrael's zero-knowledge architecture and immutable verification won us over. It's security done right.",
        rating: 5
    },
    {
        name: "Emily Nakamura",
        role: "Head of Infrastructure, MediSync",
        avatar: "EN",
        review: "HIPAA compliance was a nightmare until Cryptrael Vault. The automated audit logs and encryption verification saved us countless hours.",
        rating: 5
    }
];

export default function Testimonials() {
    return (
        <section className="relative py-24 bg-linear-to-b from-[#0F172A] to-[#1E293B] overflow-hidden">
            {/* Background Blurred Shapes */}
            <div className="absolute top-10 right-10 w-72 h-72 bg-[#7C3AED] rounded-full mix-blend-multiply filter blur-3xl opacity-10"></div>
            <div className="absolute bottom-10 left-10 w-72 h-72 bg-[#10B981] rounded-full mix-blend-multiply filter blur-3xl opacity-10"></div>

            <div className="relative max-w-7xl mx-auto px-6">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-4xl lg:text-5xl font-bold text-[#F1F5F9] mb-4">
                        Trusted by Security Leaders
                    </h2>
                    <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
                        Organizations worldwide rely on Cryptrael Vault for their most sensitive data
                    </p>
                </motion.div>

                {/* Testimonials Grid */}
                <div className="grid md:grid-cols-3 gap-8">
                    {testimonials.map((testimonial, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.6, delay: index * 0.1 }}
                            whileHover={{ y: -8, scale: 1.02 }}
                            className="group relative"
                        >
                            {/* Card */}
                            <div className="relative h-full p-8 bg-linear-to-br from-[#1E293B]/80 to-[#1E293B]/40 backdrop-blur-xl rounded-2xl border border-[#7C3AED]/20 hover:border-[#10B981]/50 transition-all duration-300 shadow-xl hover:shadow-2xl hover:shadow-[#10B981]/10">
                                {/* Glowing border effect */}
                                <div className="absolute inset-0 rounded-2xl bg-linear-to-br from-[#7C3AED]/0 via-[#10B981]/0 to-[#7C3AED]/0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl"></div>

                                <div className="relative z-10">
                                    {/* Stars */}
                                    <div className="flex gap-1 mb-6">
                                        {[...Array(testimonial.rating)].map((_, i) => (
                                            <svg
                                                key={i}
                                                className="w-5 h-5 text-[#10B981]"
                                                fill="currentColor"
                                                viewBox="0 0 20 20"
                                            >
                                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                            </svg>
                                        ))}
                                    </div>

                                    {/* Review */}
                                    <p className="text-[#F1F5F9] text-lg leading-relaxed mb-6">
                                        "{testimonial.review}"
                                    </p>

                                    {/* Author */}
                                    <div className="flex items-center gap-4 pt-4 border-t border-[#94A3B8]/20">
                                        {/* Avatar */}
                                        <div className="w-12 h-12 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-full flex items-center justify-center font-bold text-white shadow-lg">
                                            {testimonial.avatar}
                                        </div>

                                        <div>
                                            <div className="font-semibold text-[#F1F5F9]">
                                                {testimonial.name}
                                            </div>
                                            <div className="text-sm text-[#94A3B8]">
                                                {testimonial.role}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Trust Badges */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                    className="mt-16 flex flex-wrap justify-center items-center gap-8 text-[#94A3B8]"
                >
                    <div className="flex items-center gap-2">
                        <svg className="w-6 h-6 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">SOC 2 Type II</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <svg className="w-6 h-6 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">GDPR Compliant</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <svg className="w-6 h-6 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">HIPAA Ready</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <svg className="w-6 h-6 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span className="font-medium">ISO 27001</span>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
