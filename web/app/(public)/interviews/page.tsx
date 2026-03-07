import PublicNavbar from "@/components/navbar/PublicNavbar";
import Footer from "@/components/landing/footer";

export default function Interviews() {
    const interviewTypes = [
        {
            title: "Technical Interviews",
            description: "Practice coding challenges, algorithms, data structures, and system design questions.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
            ),
            color: "from-blue-500 to-blue-600",
            bgColor: "from-blue-50 to-blue-100"
        },
        {
            title: "HR Interviews",
            description: "Master behavioral questions, company culture fit, and professional communication.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            ),
            color: "from-purple-500 to-purple-600",
            bgColor: "from-purple-50 to-purple-100"
        },
        {
            title: "Behavioral Interviews",
            description: "Prepare for STAR method questions, leadership scenarios, and teamwork examples.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
            ),
            color: "from-green-500 to-green-600",
            bgColor: "from-green-50 to-green-100"
        },
        {
            title: "JavaScript Interviews",
            description: "Focus on JavaScript fundamentals, ES6+, async programming, and framework questions.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            ),
            color: "from-yellow-500 to-yellow-600",
            bgColor: "from-yellow-50 to-yellow-100"
        },
        {
            title: "Skill-Based Interviews",
            description: "Tailored interviews based on specific skills like React, Node.js, Python, or Cloud.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            ),
            color: "from-indigo-500 to-indigo-600",
            bgColor: "from-indigo-50 to-indigo-100"
        },
        {
            title: "Custom Curated Interviews",
            description: "Get personalized interview experiences curated specifically for your target role and company.",
            icon: (
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
            ),
            color: "from-pink-500 to-pink-600",
            bgColor: "from-pink-50 to-pink-100"
        }
    ];

    return (
        <>
            <PublicNavbar />
            <main className="min-h-screen bg-gradient-to-br from-white via-blue-50/30 to-white pt-24">
                {/* Hero Section */}
                <section className="max-w-7xl mx-auto px-6 py-20">
                    <div className="text-center mb-16">
                        <h1 className="text-5xl lg:text-6xl font-bold text-[#1E293B] mb-6">
                            Interview Types for{" "}
                            <span className="bg-gradient-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
                                Every Scenario
                            </span>
                        </h1>
                        <p className="text-xl text-[#475569] max-w-3xl mx-auto">
                            Practice with AI-powered interviews designed for different roles, skills, and career paths
                        </p>
                    </div>

                    {/* Interview Types Grid */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
                        {interviewTypes.map((type, index) => (
                            <div
                                key={index}
                                className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300"
                            >
                                <div className={`w-16 h-16 bg-gradient-to-br ${type.bgColor} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                                    <div className={`text-transparent bg-gradient-to-r ${type.color} bg-clip-text`}>
                                        {type.icon}
                                    </div>
                                </div>
                                <h3 className="text-2xl font-bold text-[#1E293B] mb-3">{type.title}</h3>
                                <p className="text-[#475569] leading-relaxed">
                                    {type.description}
                                </p>
                            </div>
                        ))}
                    </div>

                    {/* Interview Modes Section */}
                    <div className="mb-20">
                        <h2 className="text-4xl font-bold text-[#1E293B] text-center mb-6">
                            Choose Your Interview Mode
                        </h2>
                        <p className="text-lg text-[#475569] text-center mb-12 max-w-2xl mx-auto">
                            Practice in the format that works best for you
                        </p>

                        <div className="grid md:grid-cols-2 gap-8">
                            {/* Audio Only Mode */}
                            <div className="p-10 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl border border-blue-100">
                                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-100">
                                    <svg className="w-8 h-8 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                    </svg>
                                </div>
                                <h3 className="text-2xl font-bold text-[#1E293B] mb-4">Audio Only</h3>
                                <p className="text-[#475569] mb-6">
                                    Focus on your communication skills without camera pressure. Perfect for phone interview practice.
                                </p>
                                <ul className="space-y-3">
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#2563EB] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Less pressure, more focus</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#2563EB] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Ideal for phone interviews</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#2563EB] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Practice anywhere, anytime</span>
                                    </li>
                                </ul>
                            </div>

                            {/* Video Mode */}
                            <div className="p-10 bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl border border-purple-100">
                                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-100">
                                    <svg className="w-8 h-8 text-[#9333EA]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <h3 className="text-2xl font-bold text-[#1E293B] mb-4">Video Interview</h3>
                                <p className="text-[#475569] mb-6">
                                    Get the full interview experience with video. Practice body language and visual presentation.
                                </p>
                                <ul className="space-y-3">
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#9333EA] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Realistic interview simulation</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#9333EA] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Body language feedback</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <svg className="w-5 h-5 text-[#9333EA] mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        <span className="text-[#475569]">Build confidence on camera</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    {/* CTA Section */}
                    <div className="text-center py-16 px-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl border border-blue-100">
                        <h2 className="text-3xl lg:text-4xl font-bold text-[#1E293B] mb-4">
                            Start Your Interview Practice Today
                        </h2>
                        <p className="text-lg text-[#475569] mb-8 max-w-2xl mx-auto">
                            Choose from multiple interview types and modes to prepare for your dream job
                        </p>
                        <a
                            href="/register"
                            className="inline-block px-8 py-4 bg-gradient-to-r from-[#3B82F6] to-[#2563EB] text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300"
                        >
                            Begin Practice Now
                        </a>
                    </div>
                </section>
            </main>
            <Footer />
        </>
    );
}
