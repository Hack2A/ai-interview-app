"use client";

import { Plus } from "lucide-react";

type NewItemProps = {
    onClick: () => void;
};

export default function NewItem({ onClick }: NewItemProps) {
    return (
        <div
            onClick={onClick}
            className="group relative overflow-hidden p-8 bg-linear-to-br from-[#1E293B] to-[#0F172A] border-2 border-dashed border-[#7C3AED]/40 rounded-2xl hover:border-[#7C3AED]/80 hover:shadow-2xl hover:shadow-[#7C3AED]/20 transition-all cursor-pointer"
        >
            {/* Animated background blob */}
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-[#7C3AED]/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-500" />

            <div className="relative flex flex-col items-center justify-center gap-4">
                <div className="w-16 h-16 bg-linear-to-br from-[#5B21B6] to-[#7C3AED] rounded-2xl flex items-center justify-center shadow-lg shadow-[#7C3AED]/30 group-hover:scale-110 group-hover:shadow-[#7C3AED]/50 transition-all">
                    <Plus className="w-8 h-8 text-white" />
                </div>

                <div className="text-center">
                    <h3 className="text-xl font-bold text-[#F1F5F9] mb-2">
                        Add New Item to Vault
                    </h3>
                    <p className="text-[#94A3B8] text-sm">
                        Click to securely store your sensitive information
                    </p>
                </div>
            </div>
        </div>
    );
}