"use client";

import { ControlBarProps } from "@/types/LiveInterviewTypes";
import { Mic, MicOff, Camera, CameraOff, Settings, PhoneOff } from "lucide-react";

export default function ControlBar({
    isMuted,
    isVideoOff,
    onToggleMute,
    onToggleVideo,
    onOpenSettings,
    onDisconnect,
}: ControlBarProps) {
    return (
        <div className="flex items-center justify-center gap-3 py-4 px-6">
            <div className="flex items-center gap-2 rounded-2xl bg-white/80 backdrop-blur-md shadow-lg shadow-slate-200/50 border border-slate-200/60 px-5 py-2.5">
                {/* Settings */}
                <button
                    type="button"
                    onClick={onOpenSettings}
                    className="flex items-center justify-center w-11 h-11 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all duration-200 active:scale-95"
                    aria-label="Settings"
                >
                    <Settings className="w-5 h-5" />
                </button>

                {/* Mute / Unmute */}
                <button
                    type="button"
                    onClick={onToggleMute}
                    className={`flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 active:scale-95 ${
                        isMuted
                            ? "bg-red-50 text-red-600 hover:bg-red-100"
                            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                    aria-label={isMuted ? "Unmute" : "Mute"}
                >
                    {isMuted ? (
                        <MicOff className="w-5 h-5" />
                    ) : (
                        <Mic className="w-5 h-5" />
                    )}
                </button>

                {/* Video On / Off */}
                <button
                    type="button"
                    onClick={onToggleVideo}
                    className={`flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 active:scale-95 ${
                        isVideoOff
                            ? "bg-red-50 text-red-600 hover:bg-red-100"
                            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                    aria-label={isVideoOff ? "Turn camera on" : "Turn camera off"}
                >
                    {isVideoOff ? (
                        <CameraOff className="w-5 h-5" />
                    ) : (
                        <Camera className="w-5 h-5" />
                    )}
                </button>

                {/* Disconnect */}
                <button
                    type="button"
                    onClick={onDisconnect}
                    className="flex items-center justify-center w-11 h-11 rounded-xl bg-red-600 text-white hover:bg-red-700 transition-all duration-200 active:scale-95 shadow-md shadow-red-200"
                    aria-label="Disconnect"
                >
                    <PhoneOff className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
}
