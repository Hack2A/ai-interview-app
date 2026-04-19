import PublicNavbar from "@/components/navbar/PublicNavbar";
import Footer from "@/components/landing/footer";

export default function About() {
    return (
        <>
            <PublicNavbar />
            <main className="min-h-screen bg-gradient-to-br from-white via-blue-50/30 to-white pt-24">
                {/* Hero Section */}
                <section className="max-w-7xl mx-auto px-6 py-20">
                    <div className="text-center mb-16">
                        <h1 className="text-5xl lg:text-6xl font-bold text-[#1E293B] mb-6">
                            About{" "}
                            <span className="bg-gradient-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
                                IntrvAI
                            </span>
                        </h1>
                        <p className="text-xl text-[#475569] max-w-3xl mx-auto">
                            Empowering job seekers with AI-driven interview preparation to land their dream careers
                        </p>
                    </div>

                    {/* Mission Section */}
                    <div className="mb-20">
                        <div className="grid md:grid-cols-2 gap-12 items-center">
                            <div>
                                <h2 className="text-4xl font-bold text-[#1E293B] mb-6">Our Mission</h2>
                                <p className="text-lg text-[#475569] mb-4 leading-relaxed">
                                    At IntrvAI, we believe that everyone deserves a fair shot at their dream job. The interview process can be daunting, but with the right preparation and practice, anyone can excel.
                                </p>
                                <p className="text-lg text-[#475569] leading-relaxed">
                                    We've built an AI-powered platform that simulates realistic interview scenarios, provides instant feedback, and helps you continuously improve until you're ready to ace any interview with confidence.
                                </p>
                            </div>
                            <div className="relative">
                                <div className="aspect-square bg-gradient-to-br from-blue-100 to-indigo-100 rounded-3xl flex items-center justify-center p-12 border border-blue-200">
                                    <svg className="w-full h-full text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={0.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* What We Offer */}
                    <div className="mb-20">
                        <h2 className="text-4xl font-bold text-[#1E293B] text-center mb-12">What We Offer</h2>
                        <div className="grid md:grid-cols-3 gap-8">
                            <div className="text-center p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all">
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                    <svg className="w-8 h-8 text-[#2563EB]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-bold text-[#1E293B] mb-3">AI-Powered Intelligence</h3>
                                <p className="text-[#475569]">
                                    Our advanced AI adapts to your skill level and provides personalized interview experiences
                                </p>
                            </div>
                            <div className="text-center p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all">
                                <div className="w-16 h-16 bg-gradient-to-br from-green-50 to-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                    <svg className="w-8 h-8 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-bold text-[#1E293B] mb-3">Comprehensive Feedback</h3>
                                <p className="text-[#475569]">
                                    Get detailed insights on your performance, communication style, and areas for improvement
                                </p>
                            </div>
                            <div className="text-center p-8 bg-white rounded-2xl border border-[#E2E8F0] hover:border-blue-200 hover:shadow-xl hover:shadow-blue-100/50 transition-all">
                                <div className="w-16 h-16 bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                    <svg className="w-8 h-8 text-[#9333EA]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <h3 className="text-xl font-bold text-[#1E293B] mb-3">Rapid Improvement</h3>
                                <p className="text-[#475569]">
                                    Track your progress over time and see measurable improvements in your interview skills
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* How It Works */}
                    <div className="mb-20">
                        <h2 className="text-4xl font-bold text-[#1E293B] text-center mb-12">How It Works</h2>
                        <div className="space-y-8">
                            <div className="flex gap-8 items-start">
                                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30">
                                    1
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-[#1E293B] mb-3">Upload Your Resume</h3>
                                    <p className="text-[#475569] text-lg">
                                        Start by uploading your resume to get an instant ATS score and personalized recommendations for improvement.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-8 items-start">
                                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30">
                                    2
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-[#1E293B] mb-3">Choose Interview Type</h3>
                                    <p className="text-[#475569] text-lg">
                                        Select from technical, HR, behavioral, or skill-based interviews tailored to your target role and industry.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-8 items-start">
                                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30">
                                    3
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-[#1E293B] mb-3">Practice with AI</h3>
                                    <p className="text-[#475569] text-lg">
                                        Engage in realistic interview sessions with our AI interviewer that adapts to your responses in real-time.
                                    </p>
                                </div>
                            </div>
                            <div className="flex gap-8 items-start">
                                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30">
                                    4
                                </div>
                                <div>
                                    <h3 className="text-2xl font-bold text-[#1E293B] mb-3">Get Detailed Feedback</h3>
                                    <p className="text-[#475569] text-lg">
                                        Review comprehensive summaries, download reports, and revisit transcripts to continuously improve your skills.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Stats Section */}
                    <div className="mb-20 py-16 px-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl border border-blue-100">
                        <div className="grid md:grid-cols-3 gap-12 text-center">
                            <div>
                                <div className="text-5xl font-bold text-[#2563EB] mb-2">10,000+</div>
                                <div className="text-[#475569] text-lg">Active Users</div>
                            </div>
                            <div>
                                <div className="text-5xl font-bold text-[#2563EB] mb-2">50,000+</div>
                                <div className="text-[#475569] text-lg">Interviews Conducted</div>
                            </div>
                            <div>
                                <div className="text-5xl font-bold text-[#2563EB] mb-2">85%</div>
                                <div className="text-[#475569] text-lg">Success Rate</div>
                            </div>
                        </div>
                    </div>

                    {/* CTA Section */}
                    <div className="text-center py-16 px-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl text-white">
                        <h2 className="text-3xl lg:text-4xl font-bold mb-4">
                            Ready to Transform Your Interview Skills?
                        </h2>
                        <p className="text-lg mb-8 max-w-2xl mx-auto opacity-90">
                            Join thousands of successful candidates who have used IntrvAI to land their dream jobs
                        </p>
                        <a
                            href="/register"
                            className="inline-block px-8 py-4 bg-white text-[#2563EB] font-semibold rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
                        >
                            Get Started Now
                        </a>
                    </div>
                </section>
            </main>
            <Footer />
        </>
    );
}
