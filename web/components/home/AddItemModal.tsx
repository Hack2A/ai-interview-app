"use client";

import { useForm } from "react-hook-form";
import { useState } from "react";
import { X, HelpCircle } from "lucide-react";

type AddItemFormData = {
    itemName: string;
    itemContent: string;
    securityWords?: string;
};

type AddItemModalProps = {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: AddItemFormData & { isAdvanced: boolean }) => Promise<boolean>;
};

export default function AddItemModal({ isOpen, onClose, onSubmit }: AddItemModalProps) {
    const [isAdvancedMode, setIsAdvancedMode] = useState(false);
    const [showConfirmClose, setShowConfirmClose] = useState(false);
    const [isDirty, setIsDirty] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
        watch,
    } = useForm<AddItemFormData>();

    // Watch for changes to mark form as dirty
    const watchedFields = watch();
    const hasChanges = watchedFields.itemName || watchedFields.itemContent || watchedFields.securityWords;

    const handleClose = () => {
        if (hasChanges) {
            setShowConfirmClose(true);
        } else {
            reset();
            setIsAdvancedMode(false);
            onClose();
        }
    };

    const handleConfirmClose = () => {
        setShowConfirmClose(false);
        reset();
        setIsAdvancedMode(false);
        onClose();
    };

    const handleFormSubmit = async (data: AddItemFormData) => {
        try {
            setIsSubmitting(true);
            const success = await onSubmit({ ...data, isAdvanced: isAdvancedMode });
            if (success) {
                reset();
                setIsAdvancedMode(false);
                onClose();
            }
        } catch (error) {
            console.error("Error submitting form:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" onClick={handleClose} />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-[#1E293B] border border-[#7C3AED]/30 rounded-2xl shadow-2xl shadow-[#7C3AED]/20 w-full max-w-lg max-h-[90vh] overflow-y-auto">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-[#7C3AED]/20">
                        <h2 className="text-2xl font-bold text-[#F1F5F9]">Add New Item</h2>
                        <button
                            onClick={handleClose}
                            className="text-[#94A3B8] hover:text-[#F1F5F9] transition-colors"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-5">
                        {/* Item Name */}
                        <div>
                            <label htmlFor="itemName" className="block text-sm font-medium text-[#F1F5F9] mb-2">
                                Item Name
                            </label>
                            <input
                                id="itemName"
                                type="text"
                                {...register("itemName", {
                                    required: "Item name is required",
                                    minLength: {
                                        value: 3,
                                        message: "Item name must be at least 3 characters",
                                    },
                                })}
                                className="w-full px-4 py-3 bg-[#0F172A] border border-[#7C3AED]/30 rounded-xl text-[#F1F5F9] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] focus:border-transparent transition-all"
                                placeholder="Enter item name"
                            />
                            {errors.itemName && (
                                <p className="mt-2 text-sm text-red-400">{errors.itemName.message}</p>
                            )}
                        </div>

                        {/* Item Content */}
                        <div>
                            <label htmlFor="itemContent" className="block text-sm font-medium text-[#F1F5F9] mb-2">
                                Item Content
                            </label>
                            <textarea
                                id="itemContent"
                                rows={5}
                                {...register("itemContent", {
                                    required: "Item content is required",
                                })}
                                className="w-full px-4 py-3 bg-[#0F172A] border border-[#7C3AED]/30 rounded-xl text-[#F1F5F9] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#7C3AED] focus:border-transparent transition-all resize-none"
                                placeholder="Enter your secret content here..."
                            />
                            {errors.itemContent && (
                                <p className="mt-2 text-sm text-red-400">{errors.itemContent.message}</p>
                            )}
                        </div>

                        {/* Advanced Security Toggle */}
                        <div className="flex items-center justify-between p-4 bg-[#0F172A] border border-[#7C3AED]/20 rounded-xl">
                            <div className="flex items-center gap-2">
                                <span className="text-[#F1F5F9] font-medium">Advanced Security</span>
                                <div className="group relative">
                                    <HelpCircle className="w-4 h-4 text-[#94A3B8] cursor-help" />
                                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-[#0F172A] border border-[#7C3AED]/30 rounded-lg text-xs text-[#94A3B8] whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                        Advanced Option
                                    </div>
                                </div>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={isAdvancedMode}
                                    onChange={(e) => setIsAdvancedMode(e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-[#475569] peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[#7C3AED] rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#7C3AED]"></div>
                            </label>
                        </div>

                        {/* 12-Word Security Phrase (only if advanced mode) */}
                        {isAdvancedMode && (
                            <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                                <label htmlFor="securityWords" className="block text-sm font-medium text-[#F1F5F9] mb-2">
                                    12-Word Security Phrase
                                </label>
                                <textarea
                                    id="securityWords"
                                    rows={3}
                                    {...register("securityWords", {
                                        required: isAdvancedMode ? "Security phrase is required for advanced mode" : false,
                                        validate: (value) => {
                                            if (!isAdvancedMode) return true;
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
                                <p className="mt-2 text-xs text-[#94A3B8]">
                                    This phrase will be required to access this item later. Keep it safe!
                                </p>
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-3 pt-4">
                            <button
                                type="button"
                                onClick={handleClose}
                                className="flex-1 py-3 px-4 bg-[#475569] text-white font-semibold rounded-xl hover:bg-[#64748B] transition-all focus:outline-none focus:ring-2 focus:ring-[#475569]/50"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="flex-1 py-3 px-4 bg-linear-to-r from-[#5B21B6] to-[#7C3AED] text-white font-semibold rounded-xl shadow-lg shadow-[#7C3AED]/30 hover:shadow-[#7C3AED]/50 hover:scale-[1.02] transition-all focus:outline-none focus:ring-2 focus:ring-[#7C3AED]/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                            >
                                {isSubmitting ? "Adding..." : "Add Item"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* Confirmation Dialog */}
            {showConfirmClose && (
                <>
                    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-60" />
                    <div className="fixed inset-0 z-70 flex items-center justify-center p-4">
                        <div className="bg-[#1E293B] border border-red-500/30 rounded-2xl shadow-2xl shadow-red-500/20 w-full max-w-md p-6">
                            <h3 className="text-xl font-bold text-[#F1F5F9] mb-3">Discard Changes?</h3>
                            <p className="text-[#94A3B8] mb-6">
                                All your changes will be lost. Are you sure you want to discard them?
                            </p>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowConfirmClose(false)}
                                    className="flex-1 py-2.5 px-4 bg-[#475569] text-white font-semibold rounded-xl hover:bg-[#64748B] transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleConfirmClose}
                                    className="flex-1 py-2.5 px-4 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-all"
                                >
                                    Discard
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
