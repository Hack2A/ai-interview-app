"use client";

import { useState } from "react";
import type { CareerInput } from "@/types/careerTypes";

interface CareerToolFormProps {
    inputs: CareerInput[];
    onSubmit: (formData: Record<string, string>) => void;
    isLoading: boolean;
    accentColor: string;
}

export default function CareerToolForm({
    inputs,
    onSubmit,
    isLoading,
    accentColor,
}: CareerToolFormProps) {
    const [formState, setFormState] = useState<Record<string, string>>(() => {
        const initial: Record<string, string> = {};
        inputs.forEach((input) => {
            initial[input.name] = input.default ?? "";
        });
        return initial;
    });

    const handleChange = (name: string, value: string) => {
        setFormState((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formState);
    };

    const allRequiredFilled = inputs
        .filter((i) => i.required)
        .every((i) => formState[i.name]?.trim());

    return (
        <form onSubmit={handleSubmit} className="space-y-5">
            {inputs.map((input) => (
                <div key={input.name} className="group">
                    <label
                        htmlFor={`career-${input.name}`}
                        className="block text-sm font-semibold text-gray-700 mb-2"
                    >
                        {input.label}
                        {input.required && (
                            <span className="text-red-400 ml-1">*</span>
                        )}
                        {!input.required && (
                            <span className="text-gray-400 font-normal ml-1.5 text-xs">
                                Optional
                            </span>
                        )}
                    </label>

                    {input.type === "textarea" ? (
                        <textarea
                            id={`career-${input.name}`}
                            value={formState[input.name]}
                            onChange={(e) =>
                                handleChange(input.name, e.target.value)
                            }
                            required={input.required}
                            rows={6}
                            placeholder={`Enter ${input.label.toLowerCase()}…`}
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50/50 
                                text-sm text-gray-800 placeholder-gray-400
                                focus:outline-none focus:ring-2 focus:border-transparent
                                transition-all duration-200 resize-y min-h-[120px]"
                            style={{
                                // @ts-ignore
                                "--tw-ring-color": accentColor + "40",
                            } as React.CSSProperties}
                            onFocus={(e) => {
                                e.target.style.borderColor = accentColor;
                                e.target.style.boxShadow = `0 0 0 3px ${accentColor}25`;
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = "#e5e7eb";
                                e.target.style.boxShadow = "none";
                            }}
                        />
                    ) : (
                        <input
                            id={`career-${input.name}`}
                            type="text"
                            value={formState[input.name]}
                            onChange={(e) =>
                                handleChange(input.name, e.target.value)
                            }
                            required={input.required}
                            placeholder={
                                input.default
                                    ? `Default: ${input.default}`
                                    : `Enter ${input.label.toLowerCase()}…`
                            }
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50/50 
                                text-sm text-gray-800 placeholder-gray-400
                                focus:outline-none focus:ring-2 focus:border-transparent
                                transition-all duration-200"
                            onFocus={(e) => {
                                e.target.style.borderColor = accentColor;
                                e.target.style.boxShadow = `0 0 0 3px ${accentColor}25`;
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = "#e5e7eb";
                                e.target.style.boxShadow = "none";
                            }}
                        />
                    )}
                </div>
            ))}

            <button
                type="submit"
                disabled={isLoading || !allRequiredFilled}
                className="w-full py-3.5 px-6 rounded-xl text-white font-semibold text-sm
                    shadow-lg transition-all duration-300
                    disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none
                    hover:shadow-xl hover:scale-[1.01] active:scale-[0.99]
                    flex items-center justify-center gap-2 cursor-pointer"
                style={{
                    background: `linear-gradient(135deg, ${accentColor}, ${accentColor}dd)`,
                    boxShadow: `0 8px 24px ${accentColor}35`,
                }}
            >
                {isLoading ? (
                    <>
                        <svg
                            className="animate-spin h-4 w-4"
                            viewBox="0 0 24 24"
                            fill="none"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                            />
                            <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                            />
                        </svg>
                        Processing…
                    </>
                ) : (
                    "Run Analysis"
                )}
            </button>
        </form>
    );
}
