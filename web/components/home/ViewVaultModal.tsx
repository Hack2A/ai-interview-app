"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { X, Lock, Shield } from "lucide-react";

type VaultItemData = {
    id: string;
    name: string;
    content: string;
    isAdvanced: boolean;
};

type ViewVaultModalProps = {
    isOpen: boolean;
    item: VaultItemData | null;
    isLoading?: boolean;
    onClose: () => void;
    onUnlock?: (seed: string) => void;
};

type SecurityPhraseForm = {
    securityWords: string;
};

export default function ViewVaultModal({ isOpen, item, isLoading, onClose, onUnlock }: ViewVaultModalProps) {
    const [unlockError, setUnlockError] = useState("");

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
    } = useForm<SecurityPhraseForm>();

    const handleClose = () => {
        setUnlockError("");
        reset();
        onClose();
    };

    const handleUnlock = (data: SecurityPhraseForm) => {
        const words = data.securityWords?.trim().split(/\s+/) || [];
        if (words.length !== 12) {
            setUnlockError("Please enter exactly 12 words");
            return;
        }
        // Call the onUnlock callback with the seed phrase
        if (onUnlock) {
            onUnlock(data.securityWords);
        }
        setUnlockError("");
        reset();
    };

    if (!isOpen || !item) return null;

    // Show unlock form if it's an advanced item without content
    const needsUnlock = item.isAdvanced && !item.content;

    if (isLoading) {
        return (
            <>
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" />
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="bg-[#1E293B] border border-[#7C3AED]/30 rounded-2xl shadow-2xl p-8">
                        <div className="text-center">
                            <div className="w-12 h-12 border-4 border-[#7C3AED] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                            <p className="text-[#94A3B8]">Fetching item details...</p>
                        </div>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={handleClose} />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-[#1E293B] border border-[#7C3AED]/30 rounded-2xl shadow-2xl shadow-[#7C3AED]/20 w-full max-w-lg max-h-[90vh] overflow-y-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-[#7C3AED]/20">
                        <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 ${item.isAdvanced ? 'bg-[#10B981]/20' : 'bg-[#7C3AED]/20'} rounded-lg flex items-center justify-center`}>
                                {item.isAdvanced ? (
                                    <Shield className="w-5 h-5 text-[#10B981]" />
                                ) : (
                                    <Lock className="w-5 h-5 text-[#7C3AED]" />
                                )}
                            </div>
                            <h2 className="text-2xl font-bold text-[#F1F5F9]">{item.name}</h2>
                        </div>
                        <button
                            onClick={handleClose}
                            className="text-[#94A3B8] hover:text-[#F1F5F9] transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-6">
                        {needsUnlock ? (
                            // Security Phrase Form
                            <form onSubmit={handleSubmit(handleUnlock)} className="space-y-4">
                                <div className="text-center mb-6">
                                    <div className="w-16 h-16 bg-[#10B981]/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Shield className="w-8 h-8 text-[#10B981]" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-[#F1F5F9] mb-2">
                                        Advanced Security Enabled
                                    </h3>
                                    <p className="text-[#94A3B8] text-sm">
                                        Enter your 12-word security phrase to unlock this item
                                    </p>
                                </div>

                                <div>
                                    <label htmlFor="securityWords" className="block text-sm font-medium text-[#F1F5F9] mb-2">
                                        Security Phrase
                                    </label>
                                    <textarea
                                        id="securityWords"
                                        rows={3}
                                        {...register("securityWords", {
                                            required: "Security phrase is required",
                                            validate: (value) => {
                                                const words = value?.trim().split(/\s+/) || [];
                                                return words.length === 12 || "Please enter exactly 12 words";
                                            },
                                        })}
                                        className="w-full px-4 py-3 bg-[#0F172A] border border-[#10B981]/30 rounded-xl text-[#F1F5F9] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:border-transparent transition-all resize-none"
                                        placeholder="Enter 12 words separated by spaces..."
                                    />
                                    {errors.securityWords && (
                                        <p className="mt-2 text-sm text-red-400">{errors.securityWords.message}</p>
                                    )}
                                    {unlockError && (
                                        <p className="mt-2 text-sm text-red-400">{unlockError}</p>
                                    )}
                                </div>

                                <button
                                    type="submit"
                                    className="w-full py-3 px-4 bg-linear-to-r from-[#059669] to-[#10B981] text-white font-semibold rounded-xl shadow-lg shadow-[#10B981]/30 hover:shadow-[#10B981]/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-[#10B981]/50"
                                >
                                    Unlock Item
                                </button>
                            </form>
                        ) : (
                            // Display Content
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-[#94A3B8] mb-2">
                                        Content
                                    </label>
                                    <div className="p-4 bg-[#0F172A] border border-[#7C3AED]/20 rounded-xl">
                                        <p className="text-[#F1F5F9] whitespace-pre-wrap wrap-break-word">
                                            {item.content}
                                        </p>
                                    </div>
                                </div>

                                {item.isAdvanced && (
                                    <div className="p-3 bg-[#10B981]/10 border border-[#10B981]/30 rounded-xl flex items-center gap-2">
                                        <Shield className="w-4 h-4 text-[#10B981] shrink-0" />
                                        <p className="text-xs text-[#10B981]">
                                            This item is protected with advanced security
                                        </p>
                                    </div>
                                )}

                                <button
                                    onClick={handleClose}
                                    className="w-full py-3 px-4 bg-[#475569] text-white font-semibold rounded-xl hover:bg-[#64748B] transition-all focus:outline-none focus:ring-2 focus:ring-[#475569]/50"
                                >
                                    Close
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
