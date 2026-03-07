import RegisterForm from "@/components/auth/regform";
import Link from "next/link";
import { Suspense } from "react";

export default function Register() {
    return (
        <div className="min-h-screen w-full flex bg-linear-to-br from-[#0F172A] via-[#1E293B] to-[#0F172A]">
            {/* Left Side - Branding */}
            <div className="hidden lg:flex lg:w-1/2 h-screen flex-col items-center justify-center relative overflow-hidden border-r border-[#7C3AED]/20">
                {/* Animated blobs */}
                <div className="absolute top-20 left-10 w-96 h-96 bg-[#5B21B6] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
                <div className="absolute bottom-20 right-10 w-96 h-96 bg-[#10B981] rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

                <div className="relative text-center space-y-6 px-8 z-10">
                    {/* Logo */}
                    <div className="flex justify-center mb-8">
                        <div className="w-20 h-20 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-2xl flex items-center justify-center shadow-2xl shadow-[#7C3AED]/50">
                            <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                            </svg>
                        </div>
                    </div>

                    <h1 className="text-5xl font-bold text-[#F1F5F9]">
                        Join Cryptrael Vault
                    </h1>
                    <p className="text-xl text-[#94A3B8] max-w-md mx-auto leading-relaxed">
                        Create your account and start securing your digital assets with enterprise-grade encryption.
                    </p>

                    {/* Features */}
                    <div className="mt-12 space-y-4 text-left max-w-md mx-auto">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#10B981]/20 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#94A3B8]">Free 14-day trial</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#10B981]/20 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#94A3B8]">No credit card required</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-[#10B981]/20 rounded-lg flex items-center justify-center">
                                <svg className="w-5 h-5 text-[#10B981]" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <span className="text-[#94A3B8]">Cancel anytime</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Right Side - Form */}
            <div className="w-full lg:w-1/2 h-screen flex items-center justify-center p-6">
                <Suspense fallback={
                    <div className="w-full max-w-md flex items-center justify-center">
                        <div className="text-[#94A3B8]">Loading...</div>
                    </div>
                }>
                    <RegisterForm />
                </Suspense>
            </div>
        </div>
    );
}