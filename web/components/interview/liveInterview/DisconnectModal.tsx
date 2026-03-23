"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle } from "lucide-react";

type DisconnectModalProps = {
    isOpen: boolean;
    onCancel: () => void;
    onConfirm: () => void;
};

export default function DisconnectModal({
    isOpen,
    onCancel,
    onConfirm,
}: DisconnectModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
                        onClick={onCancel}
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 10 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    >
                        <div className="w-full max-w-sm rounded-2xl bg-white shadow-2xl border border-slate-200/60 p-6 text-center">
                            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-amber-50 mx-auto mb-4">
                                <AlertTriangle className="w-6 h-6 text-amber-500" />
                            </div>

                            <h2 className="text-lg font-semibold text-slate-900 mb-2">
                                End Interview?
                            </h2>
                            <p className="text-sm text-slate-500 mb-6 leading-relaxed">
                                Are you sure you want to conclude and submit your interview? This action cannot be undone.
                            </p>

                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={onCancel}
                                    className="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors active:scale-95"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="button"
                                    onClick={onConfirm}
                                    className="flex-1 rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700 transition-colors active:scale-95 shadow-md shadow-red-200"
                                >
                                    End & Submit
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
