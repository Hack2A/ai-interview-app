"use client";

import { useEffect } from "react";

interface ToastProps {
    message: string;
    type?: "success" | "error" | "info";
    onClose?: () => void;
}

export default function Toast({ message, type = "success", onClose }: ToastProps) {
    useEffect(() => {
        if (onClose) {
            const timer = setTimeout(onClose, 5000);
            return () => clearTimeout(timer);
        }
    }, [onClose]);

    const bgColor = type === "success"
        ? "bg-[#10B981]"
        : type === "error"
            ? "bg-red-500"
            : "bg-blue-500";

    return (
        <div className={`fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-xl shadow-lg z-50 animate-slide-in-right`}>
            <div className="flex items-center gap-2">
                {type === "success" && (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                )}
                <p className="font-medium">{message}</p>
            </div>
        </div>
    );
}
