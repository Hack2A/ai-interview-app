"use client";

import { useState, useRef, KeyboardEvent, ClipboardEvent } from "react";
import Toast from "./Toast";

interface OTPInputProps {
    length?: number;
    onComplete: (otp: string) => void;
    onCancel?: () => void;
    onContinue?: () => void;
    isLoading?: boolean;
    error?: string;
    isVerified?: boolean;
    showToast?: boolean;
    hasSeedPhrase?: boolean;
}

export default function OTPInput({
    length = 6,
    onComplete,
    onCancel,
    onContinue,
    isLoading = false,
    error,
    isVerified = false,
    showToast = false,
    hasSeedPhrase = false
}: OTPInputProps) {
    const [otp, setOtp] = useState<string[]>(Array(length).fill(""));
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    const handleChange = (index: number, value: string) => {
        // Only allow numbers
        if (value && !/^\d$/.test(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        // Auto-focus next input
        if (value && index < length - 1) {
            inputRefs.current[index + 1]?.focus();
        }

        // Call onComplete when all digits are entered
        if (newOtp.every(digit => digit !== "") && newOtp.length === length) {
            onComplete(newOtp.join(""));
        }
    };

    const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Backspace") {
            if (!otp[index] && index > 0) {
                // Move to previous input if current is empty
                inputRefs.current[index - 1]?.focus();
            } else {
                // Clear current input
                const newOtp = [...otp];
                newOtp[index] = "";
                setOtp(newOtp);
            }
        } else if (e.key === "ArrowLeft" && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === "ArrowRight" && index < length - 1) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData("text/plain").trim();

        // Only accept numeric strings of correct length
        if (!/^\d+$/.test(pastedData)) return;

        const pastedDigits = pastedData.slice(0, length).split("");
        const newOtp = [...otp];

        pastedDigits.forEach((digit, index) => {
            if (index < length) {
                newOtp[index] = digit;
            }
        });

        setOtp(newOtp);

        // Focus last filled input or next empty
        const lastFilledIndex = Math.min(pastedDigits.length - 1, length - 1);
        inputRefs.current[lastFilledIndex]?.focus();

        // Auto-submit if complete
        if (newOtp.every(digit => digit !== "")) {
            onComplete(newOtp.join(""));
        }
    };

    const handleReset = () => {
        setOtp(Array(length).fill(""));
        inputRefs.current[0]?.focus();
    };

    return (
        <div className="w-full max-w-md">
            {showToast && <Toast message="OTP verified successfully!" type="success" />}

            <div className="mb-8 text-center">
                <h2 className="text-3xl font-bold text-[#F1F5F9] mb-2">
                    {isVerified ? "Verification Complete" : "Verify OTP"}
                </h2>
                <p className="text-[#94A3B8]">
                    {isVerified
                        ? "Your OTP has been verified successfully"
                        : "Enter the 6-digit code sent to your email"}
                </p>
            </div>

            <div className="flex justify-center gap-2 mb-6">
                {otp.map((digit, index) => (
                    <input
                        key={index}
                        ref={(el) => {
                            inputRefs.current[index] = el;
                        }}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(index, e)}
                        onPaste={handlePaste}
                        disabled={isLoading}
                        className="w-12 h-14 text-center text-2xl font-bold bg-[#1E293B] border border-[#7C3AED]/30 rounded-xl text-[#F1F5F9] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] focus:border-transparent transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        autoComplete="off"
                    />
                ))}
            </div>

            {error && (
                <p className="mb-4 text-sm text-red-400 text-center">{error}</p>
            )}

            <div className="space-y-3">
                {isVerified && !hasSeedPhrase ? (
                    <button
                        onClick={onContinue}
                        className="w-full py-3 px-4 bg-linear-to-r from-[#10B981] to-[#059669] text-white font-semibold rounded-xl shadow-lg shadow-[#10B981]/30 hover:shadow-[#10B981]/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-[#10B981]/50 cursor-pointer"
                    >
                        Continue
                    </button>
                ) : isVerified && hasSeedPhrase ? (
                    <div className="text-center py-3 text-[#94A3B8]">
                        Please save your recovery phrase to continue
                    </div>
                ) : (
                    <button
                        onClick={() => onComplete(otp.join(""))}
                        disabled={otp.some(digit => digit === "") || isLoading}
                        className="w-full py-3 px-4 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] text-white font-semibold rounded-xl shadow-lg shadow-[#7C3AED]/30 hover:shadow-[#7C3AED]/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 cursor-pointer"
                    >
                        {isLoading ? "Verifying..." : "Verify OTP"}
                    </button>
                )}

                {!isVerified && (
                    <div className="flex gap-2">
                        <button
                            onClick={handleReset}
                            disabled={isLoading}
                            className="flex-1 py-2 px-4 bg-[#1E293B] border border-[#7C3AED]/30 text-[#F1F5F9] font-medium rounded-xl hover:bg-[#1E293B]/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                        >
                            Clear
                        </button>

                        {onCancel && (
                            <button
                                onClick={onCancel}
                                disabled={isLoading}
                                className="flex-1 py-2 px-4 bg-[#1E293B] border border-[#7C3AED]/30 text-[#F1F5F9] font-medium rounded-xl hover:bg-[#1E293B]/80 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                )}
            </div>

            {!isVerified && (
                <p className="mt-5 text-center text-[#94A3B8]">
                    Didn't receive the code?{" "}
                    <button
                        onClick={handleReset}
                        disabled={isLoading}
                        className="text-[#10B981] hover:text-[#10B981]/80 font-semibold transition-colors cursor-pointer disabled:opacity-50"
                    >
                        Resend OTP
                    </button>
                </p>
            )}
        </div>
    );
}
