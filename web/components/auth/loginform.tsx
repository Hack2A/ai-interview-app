"use client";

import { navigate } from "@/lib/navigation";
import { authService } from "@/services/authService";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import GoogleAuth from "./GoogleAuth";
import OTPInput from "./OTPInput";

type LoginFormData = {
    email: string;
    password: string;
};

export default function LoginForm() {
    const searchParams = useSearchParams();
    const redirect = searchParams.get('redirect') || '/home';

    const [showOTP, setShowOTP] = useState(false);
    const [userEmail, setUserEmail] = useState("");
    const [sessionToken, setSessionToken] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [otpError, setOtpError] = useState("");
    const [isVerified, setIsVerified] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [verifiedData, setVerifiedData] = useState<any>(null);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>();

    const onSubmit = async (data: LoginFormData) => {
        try {
            setIsLoading(true);
            setOtpError("");
            const response = await authService.login(data);

            // After successful login request, show OTP input
            if (response.data.session_token) {
                setSessionToken(response.data.session_token);
            }
            setUserEmail(data.email);
            setShowOTP(true);
        } catch (error: any) {
            setOtpError(error.response?.data?.message || "Login failed. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleOTPComplete = async (otp: string) => {
        try {
            setIsLoading(true);
            setOtpError("");

            const response = await authService.verifyOTP({
                email: userEmail,
                otp: otp,
                session_token: sessionToken,
            });

            if (response.data.access) {
                // Store verified data but don't redirect yet
                setVerifiedData(response.data);
                setIsVerified(true);
                setShowToast(true);
                // Hide toast after 5 seconds
                setTimeout(() => setShowToast(false), 5000);
            }
        } catch (error: any) {
            setOtpError(error.response?.data?.message || "Invalid OTP. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleContinue = () => {
        if (verifiedData && verifiedData.access) {
            // Set token as cookie for authentication
            document.cookie = `token=${verifiedData.access}; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 days
            navigate(redirect, true);
        }
    };

    const handleCancelOTP = () => {
        setShowOTP(false);
        setUserEmail("");
        setSessionToken("");
        setOtpError("");
        setIsVerified(false);
        setShowToast(false);
        setVerifiedData(null);
    };

    // Show OTP input if OTP stage is active
    if (showOTP) {
        return (
            <OTPInput
                length={6}
                onComplete={handleOTPComplete}
                onCancel={handleCancelOTP}
                onContinue={handleContinue}
                isLoading={isLoading}
                error={otpError}
                isVerified={isVerified}
                showToast={showToast}
            />
        );
    }

    return (
        <div className="w-full max-w-md">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-[#F1F5F9] mb-2">Sign In</h2>
                <p className="text-[#94A3B8]">Enter your credentials to access your vault</p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                {/* Email Field */}
                <div>
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-[#F1F5F9] mb-2"
                    >
                        Email
                    </label>
                    <input
                        id="email"
                        type="email"
                        {...register("email", {
                            required: "Email is required",
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                message: "Invalid email address",
                            },
                        })}
                        className="w-full px-4 py-3 bg-[#1E293B] border border-[#7C3AED]/30 rounded-xl text-[#F1F5F9] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] focus:border-transparent transition-all"
                        placeholder="Enter your email"
                    />
                    {errors.email && (
                        <p className="mt-2 text-sm text-red-400">{errors.email.message}</p>
                    )}
                </div>

                {/* Password Field */}
                <div>
                    <label
                        htmlFor="password"
                        className="block text-sm font-medium text-[#F1F5F9] mb-2"
                    >
                        Password
                    </label>
                    <input
                        id="password"
                        type="password"
                        {...register("password", {
                            required: "Password is required",
                            minLength: {
                                value: 8,
                                message: "Password must be at least 8 characters",
                            },
                        })}
                        className="w-full px-4 py-3 bg-[#1E293B] border border-[#7C3AED]/30 rounded-xl text-[#F1F5F9] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] focus:border-transparent transition-all"
                        placeholder="Enter your password"
                    />
                    {errors.password && (
                        <p className="mt-2 text-sm text-red-400">
                            {errors.password.message}
                        </p>
                    )}
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-3 px-4 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] text-white font-semibold rounded-xl shadow-lg shadow-[#7C3AED]/30 hover:shadow-[#7C3AED]/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 cursor-pointer"
                >
                    {isLoading ? "Signing In..." : "Sign In"}
                </button>
            </form>

            {/* Sign up link */}
            <p className="mt-5 text-center text-[#94A3B8]">
                Don't have an account?{" "}
                <button
                    onClick={() => navigate("/register")}
                    className="text-[#10B981] hover:text-[#10B981]/80 font-semibold transition-colors cursor-pointer"
                >
                    Sign up
                </button>
            </p>
        </div>
    );
}