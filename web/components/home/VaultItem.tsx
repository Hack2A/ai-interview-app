"use client";

import { Lock, Shield } from "lucide-react";

type VaultItemProps = {
    id: string;
    name: string;
    isAdvanced: boolean;
    onClick: () => void;
};

export default function VaultItem({ id, name, isAdvanced, onClick }: VaultItemProps) {
    return (
        <div
            onClick={onClick}
            className="group relative p-4 bg-[#1E293B] border border-[#7C3AED]/30 rounded-xl hover:border-[#7C3AED]/60 hover:shadow-lg hover:shadow-[#7C3AED]/20 transition-all cursor-pointer"
        >
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`w-10 h-10 ${isAdvanced ? 'bg-[#10B981]/20' : 'bg-[#7C3AED]/20'} rounded-lg flex items-center justify-center flex-shrink-0`}>
                        {isAdvanced ? (
                            <Shield className="w-5 h-5 text-[#10B981]" />
                        ) : (
                            <Lock className="w-5 h-5 text-[#7C3AED]" />
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <h3 className="text-[#F1F5F9] font-medium truncate">{name}</h3>
                        <p className="text-xs text-[#94A3B8] mt-0.5">
                            {isAdvanced ? "Advanced Security" : "Standard Security"}
                        </p>
                    </div>
                </div>
                <div className="text-[#94A3B8] group-hover:text-[#7C3AED] transition-colors">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </div>
            </div>
        </div>
    );
}
