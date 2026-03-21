"use client";

import { useState } from "react";
import { Copy, Check, AlertTriangle, Shield, Download } from "lucide-react";

type SeedPopupProps = {
    isOpen: boolean;
    seedPhrase: string[];
    onClose: () => void;
};

export default function SeedPopup({ isOpen, seedPhrase, onClose }: SeedPopupProps) {
    const [hasCopied, setHasCopied] = useState(false);
    const [hasSaved, setHasSaved] = useState(false);

    if (!isOpen) return null;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(seedPhrase.join(" "));
            setHasCopied(true);
            setTimeout(() => setHasCopied(false), 2000);
        } catch (error) {
            console.error("Failed to copy:", error);
        }
    };

    const handleSave = () => {
        try {
            // Create the content for the file
            const content = `Cryptrael Vault Recovery Phrase
================================

IMPORTANT: Keep this phrase safe and private!

Your 12-word recovery phrase:
${seedPhrase.map((word, index) => `${index + 1}. ${word}`).join('\n')}

================================
Generated: ${new Date().toLocaleString()}

⚠️ WARNING:
- Never share this recovery phrase with anyone
- Store it in a secure location
- You'll need this to recover your vault
- Cryptrael Vault cannot recover this phrase if you lose it
`;

            // Create a blob and download link
            const blob = new Blob([content], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `Cryptrael Vault-Recovery-Phrase-${Date.now()}.txt`;

            // Trigger download
            document.body.appendChild(link);
            link.click();

            // Cleanup
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            setHasSaved(true);
        } catch (error) {
            console.error("Failed to download seed phrase:", error);
            alert("Failed to download recovery phrase. Please copy it manually.");
        }
    };

    const handleClose = () => {
        if (hasSaved) {
            onClose();
        }
    };

    return (
        <>
            {/* Backdrop - Non-dismissible */}
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50" />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-[#1E293B] border border-[#7C3AED]/30 rounded-2xl shadow-2xl shadow-[#7C3AED]/20 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                    {/* Header */}
                    <div className="p-6 border-b border-[#7C3AED]/20">
                        <div className="flex items-center justify-center gap-3 mb-4">
                            <div className="w-12 h-12 bg-[#10B981]/20 rounded-full flex items-center justify-center">
                                <Shield className="w-6 h-6 text-[#10B981]" />
                            </div>
                        </div>
                        <h2 className="text-2xl font-bold text-[#F1F5F9] text-center">
                            Save Your Recovery Phrase
                        </h2>
                        <p className="text-[#94A3B8] text-center mt-2">
                            This is the only time you'll see your recovery phrase. Keep it safe!
                        </p>
                    </div>

                    {/* Warning Banner */}
                    <div className="mx-6 mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                        <div className="flex gap-3">
                            <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                            <div>
                                <h3 className="text-amber-500 font-semibold mb-1">Important!</h3>
                                <ul className="text-amber-200/90 text-sm space-y-1">
                                    <li>• Write down these words in order and store them safely</li>
                                    <li>• Never share your recovery phrase with anyone</li>
                                    <li>• You'll need this phrase to recover your vault if you lose access</li>
                                    <li>• We cannot recover your phrase if you lose it</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    {/* Seed Phrase Grid */}
                    <div className="p-6">
                        <div className="grid grid-cols-3 gap-3 mb-6">
                            {seedPhrase.map((word, index) => (
                                <div
                                    key={index}
                                    className="bg-[#0F172A] border border-[#7C3AED]/20 rounded-lg p-3 flex items-center gap-2"
                                >
                                    <span className="text-[#7C3AED] font-semibold text-sm">
                                        {index + 1}.
                                    </span>
                                    <span className="text-[#F1F5F9] font-medium">
                                        {word}
                                    </span>
                                </div>
                            ))}
                        </div>

                        {/* Action Buttons */}
                        <div className="space-y-3">
                            <button
                                onClick={handleCopy}
                                className="w-full px-6 py-3 bg-[#7C3AED]/20 hover:bg-[#7C3AED]/30 border border-[#7C3AED]/50 text-[#F1F5F9] rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2"
                            >
                                {hasCopied ? (
                                    <>
                                        <Check className="w-5 h-5" />
                                        Copied to Clipboard!
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-5 h-5" />
                                        Copy Recovery Phrase
                                    </>
                                )}
                            </button>

                            <button
                                onClick={handleSave}
                                disabled={hasSaved}
                                className={`w-full px-6 py-3 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${hasSaved
                                    ? "bg-[#10B981] text-white cursor-default"
                                    : "bg-[#7C3AED] hover:bg-[#6D28D9] text-white"
                                    }`}
                            >
                                {hasSaved ? (
                                    <>
                                        <Check className="w-5 h-5" />
                                        Saved Securely
                                    </>
                                ) : (
                                    <>
                                        <Download className="w-5 h-5" />
                                        I Have Saved My Recovery Phrase
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Continue Button (Only shown after save) */}
                        {hasSaved && (
                            <button
                                onClick={handleClose}
                                className="w-full mt-3 px-6 py-3 bg-[#10B981] hover:bg-[#059669] text-white rounded-xl font-semibold transition-all duration-200"
                            >
                                Continue to Dashboard
                            </button>
                        )}

                        {/* Save Reminder */}
                        {!hasSaved && (
                            <p className="text-center text-[#94A3B8] text-sm mt-4">
                                You must confirm you've saved your recovery phrase to continue
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}