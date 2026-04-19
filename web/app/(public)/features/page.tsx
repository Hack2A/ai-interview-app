import PublicNavbar from "@/components/navbar/PublicNavbar";
import Footer from "@/components/landing/footer";

export default function Features() {
    return (
        <>
            <PublicNavbar />
            <main className="min-h-screen bg-linear-to-br from-white via-blue-50/30 to-white pt-24">
                {/* Hero Section */}
                <section className="max-w-7xl mx-auto px-6 py-20">
                    <div className="text-center mb-16">
                        <h1 className="text-5xl lg:text-6xl font-bold text-[#1E293B] mb-6">
                            Powerful Features to{" "}
                            <span className="bg-linear-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
                                Ace Your Interview
                            </span>
                        </h1>
                        <p className="text-xl text-[#475569] max-w-3xl mx-auto">
                            Everything you need to prepare, practice, and succeed in your next interview
                        </p>
                    </div>

                    {/* Feature Grid */}
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
                        {/* Resume Analysis */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Resume Upload & Analysis</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Upload your resume and get instant analysis. Our AI identifies strengths, weaknesses, and optimization opportunities.
                            </p>
                        </div>

                        {/* ATS Score */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">ATS Score Checker</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Check how well your resume performs against Applicant Tracking Systems used by companies worldwide.
                            </p>
                        </div>

                        {/* AI Interviews */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">AI-Powered Interviews</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Practice with intelligent AI that adapts to your responses and provides realistic interview scenarios.
                            </p>
                        </div>

                        {/* Multiple Interview Types */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Diverse Interview Types</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Technical, HR, behavioral, JavaScript, skill-based, and custom-curated interviews tailored to your needs.
                            </p>
                        </div>

                        {/* Audio/Video Modes */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Flexible Interview Modes</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Choose between audio-only or video-enabled interviews based on your comfort level and practice needs.
                            </p>
                        </div>

                        {/* Detailed Analytics */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Comprehensive Analytics</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Get detailed performance summaries, downloadable reports, and revisit transcripts to track your improvement.
                            </p>
                        </div>

                        {/* Real-time Feedback */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Instant Feedback</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Receive immediate feedback on your answers, communication style, and areas for improvement after each session.
                            </p>
                        </div>

                        {/* Progress Tracking */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Progress Tracking</h3>
                            <p className="text-[#475569] leading-relaxed">
                                Monitor your improvement over time with detailed metrics and performance trends across multiple sessions.
                            </p>
                        </div>

                        {/* Personalized Learning */}
                        <div className="group p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all duration-300">
                            <div className="w-14 h-14 bg-linear-to-br from-blue-50 to-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <svg className="w-7 h-7 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold text-[#1E293B] mb-3">Personalized Learning Path</h3>
                            <p className="text-[#475569] leading-relaxed">
                                AI adapts to your skill level and creates a customized learning path to address your specific weaknesses.
                            </p>
                        </div>
                    </div>

                    {/* CTA Section */}
                    <div className="text-center py-16 px-8 bg-linear-to-r from-blue-50 to-indigo-50 rounded-3xl border border-blue-100">
                        <h2 className="text-3xl lg:text-4xl font-bold text-[#1E293B] mb-4">
                            Ready to Start Practicing?
                        </h2>
                        <p className="text-lg text-[#475569] mb-8 max-w-2xl mx-auto">
                            Join thousands of professionals who have improved their interview skills with IntrvAI
                        </p>
                        <a
                            href="/register"
                            className="inline-block px-8 py-4 bg-linear-to-r from-[#3B82F6] to-[#2563EB] text-white font-semibold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300"
                        >
                            Get Started for Free
                        </a>
                    </div>
                </section>
            </main>
            <Footer />
        </>
    );
}
