"use client";

import { motion } from "framer-motion";

const insights = [
  {
    category: "Security",
    title: "Understanding Zero-Knowledge Encryption in Enterprise Vaults",
    description: "Deep dive into how zero-knowledge architecture ensures that even service providers cannot access your encrypted data.",
    date: "Feb 18, 2026",
    readTime: "8 min read"
  },
  {
    category: "Blockchain",
    title: "How Blockchain Audit Trails Revolutionize Compliance",
    description: "Explore how immutable blockchain ledgers provide tamper-proof audit trails that satisfy SOC 2 and HIPAA requirements.",
    date: "Feb 12, 2026",
    readTime: "6 min read"
  },
  {
    category: "Whitepaper",
    title: "Cryptrael Vault: Technical Architecture & Security Model",
    description: "Comprehensive whitepaper detailing our cryptographic protocols, threat model, and multi-layer security architecture.",
    date: "Feb 5, 2026",
    readTime: "15 min read"
  }
];

export default function InsightSection() {
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
            Security Insights
          </h2>
          <p className="text-xl text-[#94A3B8] max-w-2xl mx-auto">
            Stay informed with the latest in cryptographic security and blockchain technology
          </p>
        </motion.div>

        {/* Insights Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          {insights.map((insight, index) => (
            <motion.article
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="group cursor-pointer"
            >
              {/* Card */}
              <div className="relative h-full bg-linear-to-br from-[#1E293B]/60 to-[#1E293B]/30 backdrop-blur-xl rounded-2xl border border-[#7C3AED]/20 hover:border-[#7C3AED]/50 transition-all duration-300 overflow-hidden shadow-lg hover:shadow-2xl hover:shadow-[#7C3AED]/10">
                {/* Gradient overlay on hover */}
                <div className="absolute inset-0 bg-linear-to-br from-[#7C3AED]/0 to-[#10B981]/0 group-hover:from-[#7C3AED]/10 group-hover:to-[#10B981]/5 transition-all duration-500"></div>

                {/* Content */}
                <div className="relative p-8 space-y-4">
                  {/* Category Tag */}
                  <div className="inline-flex items-center px-3 py-1 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] rounded-full">
                    <span className="text-xs font-semibold text-white uppercase tracking-wider">
                      {insight.category}
                    </span>
                  </div>

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-[#F1F5F9] group-hover:text-[#10B981] transition-colors duration-300 leading-tight">
                    {insight.title}
                  </h3>

                  {/* Description */}
                  <p className="text-[#94A3B8] leading-relaxed">
                    {insight.description}
                  </p>

                  {/* Meta Info */}
                  <div className="flex items-center justify-between pt-4 border-t border-[#94A3B8]/20">
                    <span className="text-sm text-[#94A3B8]">{insight.date}</span>
                    <span className="text-sm text-[#94A3B8]">{insight.readTime}</span>
                  </div>

                  {/* Read More Button */}
                  <motion.button
                    whileHover={{ x: 5 }}
                    className="flex items-center gap-2 text-[#10B981] font-semibold group-hover:gap-4 transition-all duration-300"
                  >
                    Read More
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </motion.button>
                </div>

                {/* Decorative corner accent */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-linear-to-br from-[#7C3AED]/20 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
            </motion.article>
          ))}
        </div>

        {/* CTA Button */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mt-12 text-center"
        >
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 bg-transparent border-2 border-[#7C3AED] text-[#F1F5F9] font-semibold rounded-2xl hover:bg-[#7C3AED]/10 transition-all"
          >
            View All Articles
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
}