"use client";

import { TranscriptEntry } from "@/types/LiveInterviewTypes";
import { useEffect, useRef } from "react";

type TranscriptPanelProps = {
	entries: TranscriptEntry[];
	streamingText?: string;
	isAITyping?: boolean;
};

export default function TranscriptPanel({
	entries,
	streamingText = "",
	isAITyping = false,
}: TranscriptPanelProps) {
	const scrollRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [entries, streamingText]);

	return (
		<div className="flex flex-col w-90 min-w-75 bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
			{/* Header */}
			<div className="flex items-center gap-2 px-5 py-3.5 border-b border-slate-100">
				<span className="relative flex h-2 w-2">
					<span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
					<span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
				</span>
				<h2 className="text-sm font-semibold text-slate-900">
					Live Transcript
				</h2>
			</div>

			{/* Transcript entries */}
			<div
				ref={scrollRef}
				className="flex-1 overflow-y-auto px-4 py-3 space-y-3"
			>
				{entries.length === 0 && !isAITyping ? (
					<div className="flex items-center justify-center h-full text-sm text-slate-400 py-12">
						Transcript will appear here…
					</div>
				) : (
					<>
						{entries.map((entry) => (
							<div
								key={entry.id}
								className="group rounded-xl px-3 py-2.5 hover:bg-slate-50 transition-colors"
							>
								<div className="flex items-center gap-2 mb-1">
									<span
										className={`text-xs font-bold ${
											entry.speaker === "You"
												? "text-blue-600"
												: "text-violet-600"
										}`}
									>
										{entry.speaker}
									</span>
									<span className="text-[10px] text-slate-400 font-medium">
										{entry.timestamp}
									</span>
								</div>
								<p className="text-sm text-slate-700 leading-relaxed">
									{entry.text}
								</p>
							</div>
						))}

						{/* Streaming AI response — shown while AI is typing */}
						{isAITyping && streamingText && (
							<div className="rounded-xl px-3 py-2.5 bg-violet-50/50 border border-violet-100/50">
								<div className="flex items-center gap-2 mb-1">
									<span className="text-xs font-bold text-violet-600">
										Interviewer
									</span>
									<span className="flex items-center gap-1">
										<span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
										<span className="text-[10px] text-violet-400 font-medium">
											typing…
										</span>
									</span>
								</div>
								<p className="text-sm text-slate-700 leading-relaxed">
									{streamingText}
									<span className="inline-block w-0.5 h-4 bg-violet-500 ml-0.5 animate-pulse align-middle" />
								</p>
							</div>
						)}

						{/* Typing indicator without text yet */}
						{isAITyping && !streamingText && (
							<div className="rounded-xl px-3 py-2.5 bg-violet-50/50 border border-violet-100/50">
								<div className="flex items-center gap-2">
									<span className="text-xs font-bold text-violet-600">
										Interviewer
									</span>
									<div className="flex items-center gap-1">
										<span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce [animation-delay:0ms]" />
										<span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce [animation-delay:150ms]" />
										<span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 animate-bounce [animation-delay:300ms]" />
									</div>
								</div>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);
}
