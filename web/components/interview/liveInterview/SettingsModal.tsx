"use client";

import { SettingsModalProps } from "@/types/LiveInterviewTypes";
import { X, Camera, Mic, Speaker } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function SettingsModal({
    isOpen,
    onClose,
    cameras,
    microphones,
    speakers,
    selectedCamera,
    selectedMicrophone,
    selectedSpeaker,
    onCameraChange,
    onMicrophoneChange,
    onSpeakerChange,
}: SettingsModalProps) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
                        onClick={onClose}
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 10 }}
                        transition={{ duration: 0.2, ease: "easeOut" }}
                        className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    >
                        <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl border border-slate-200/60">
                            {/* Header */}
                            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                                <h2 className="text-lg font-semibold text-slate-900">
                                    Device Settings
                                </h2>
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-slate-100 transition-colors"
                                    aria-label="Close settings"
                                >
                                    <X className="w-4 h-4 text-slate-500" />
                                </button>
                            </div>

                            {/* Body */}
                            <div className="px-6 py-5 space-y-5">
                                {/* Camera */}
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                                        <Camera className="w-4 h-4 text-slate-400" />
                                        Camera
                                    </label>
                                    <select
                                        value={selectedCamera}
                                        onChange={(e) =>
                                            onCameraChange(e.target.value)
                                        }
                                        className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                                    >
                                        {cameras.map((device) => (
                                            <option
                                                key={device.deviceId}
                                                value={device.deviceId}
                                            >
                                                {device.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Microphone */}
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                                        <Mic className="w-4 h-4 text-slate-400" />
                                        Microphone
                                    </label>
                                    <select
                                        value={selectedMicrophone}
                                        onChange={(e) =>
                                            onMicrophoneChange(e.target.value)
                                        }
                                        className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                                    >
                                        {microphones.map((device) => (
                                            <option
                                                key={device.deviceId}
                                                value={device.deviceId}
                                            >
                                                {device.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Speaker */}
                                <div className="space-y-2">
                                    <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                                        <Speaker className="w-4 h-4 text-slate-400" />
                                        Speaker
                                    </label>
                                    <select
                                        value={selectedSpeaker}
                                        onChange={(e) =>
                                            onSpeakerChange(e.target.value)
                                        }
                                        className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition-all"
                                    >
                                        {speakers.map((device) => (
                                            <option
                                                key={device.deviceId}
                                                value={device.deviceId}
                                            >
                                                {device.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            {/* Footer */}
                            <div className="px-6 py-4 border-t border-slate-100 flex justify-end">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="rounded-xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white hover:bg-slate-800 transition-colors active:scale-95"
                                >
                                    Done
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
