import RegisterForm from "@/components/auth/regform";
import Link from "next/link";
import { Suspense } from "react";

export default function Register() {
    return (
        <div className="min-h-screen w-full flex bg-gradient-to-br from-white via-blue-50/30 to-white">
            {/* Left Side - Branding */}
            <div className="hidden lg:flex lg:w-1/2 h-screen flex-col items-center justify-center relative overflow-hidden border-r border-[#E2E8F0]">
                {/* Animated blobs */}
                <div className="absolute top-20 left-10 w-96 h-96 bg-[#3B82F6]/10 rounded-full filter blur-3xl animate-blob"></div>
                <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#2563EB]/10 rounded-full filter blur-3xl animate-blob animation-delay-2000"></div>

                <div className="relative text-center space-y-6 px-8 z-10">
                    {/* Logo */}
                    <div className="flex justify-center mb-8">
                        <div className="w-20 h-20 bg-gradient-to-br from-[#3B82F6] to-[#2563EB] rounded-2xl flex items-center justify-center shadow-2xl shadow-blue-500/50">
                            <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                        </div>
                    </div>

                    <h1 className="text-5xl font-bold text-[#1E293B]">
                        Join IntrvAI
                    </h1>
                    <p className="text-xl text-[#475569] max-w-md mx-auto leading-relaxed">
                        Create your account and start your journey to interview success with AI-powered preparation.
                    </p>

                    {/* Features */}
                    <div className="mt-12 space-y-4 text-left max-w-md mx-auto">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#2563EB]/10 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#2563EB]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#475569]">Free practice interviews</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#2563EB]/10 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#2563EB]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#475569]">Instant ATS scoring</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#2563EB]/10 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#2563EB]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#475569]">Detailed analytics</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 h-screen flex items-center justify-center p-6">
                <Suspense fallback={
                    <div className="w-full max-w-md flex items-center justify-center">
                        <div className="text-[#475569]">Loading...</div>
                    </div>
                }>
                    <RegisterForm />
                </Suspense>
            </div>
        </div>
    );
}