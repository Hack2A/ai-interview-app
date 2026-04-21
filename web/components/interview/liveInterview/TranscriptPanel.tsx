"use client";

import { TranscriptEntry } from "@/types/LiveInterviewTypes";
import { useEffect, useRef } from "react";

type TranscriptPanelProps = {
	entries: TranscriptEntry[];
	streamingText?: string;
	isAITyping?: boolean;
	isAISpeaking?: boolean;
	isUserSpeaking?: boolean;
};

/** Animated sound-wave bars shown next to a speaker's name. */
function SpeakingIndicator({ color }: { color: "violet" | "blue" }) {
	const bar = color === "violet" ? "bg-violet-500" : "bg-blue-500";
	return (
		<span className="flex items-end gap-px h-3.5 ml-1.5" aria-label="speaking">
			{[0, 150, 50, 200, 100].map((delay, i) => (
				<span
					key={i}
					className={`${bar} w-0.5 rounded-full animate-[soundbar_0.8s_ease-in-out_infinite]`}
					style={{
						animationDelay: `${delay}ms`,
						height: "100%",
					}}
				/>
			))}
		</span>
	);
}

export default function TranscriptPanel({
	entries,
	streamingText = "",
	isAITyping = false,
	isAISpeaking = false,
	isUserSpeaking = false,
}: TranscriptPanelProps) {
	const scrollRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [entries, streamingText, isAISpeaking, isUserSpeaking]);

	return (
		<>
			{/* Inject the soundbar keyframes globally once */}
			<style>{`
				@keyframes soundbar {
					0%, 100% { transform: scaleY(0.3); }
					50% { transform: scaleY(1); }
				}
			`}</style>

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

					{/* Live speaking pills */}
					<div className="ml-auto flex items-center gap-2">
						{isAISpeaking && (
							<span className="flex items-center gap-1 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold text-violet-700">
								<span className="flex items-end gap-px h-2.5">
									{[0, 150, 50].map((d, i) => (
										<span
											key={i}
											className="bg-violet-500 w-0.5 rounded-full animate-[soundbar_0.8s_ease-in-out_infinite]"
											style={{ animationDelay: `${d}ms`, height: "100%" }}
										/>
									))}
								</span>
								AI Speaking
							</span>
						)}
						{isUserSpeaking && !isAISpeaking && (
							<span className="flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold text-blue-700">
								<span className="flex items-end gap-px h-2.5">
									{[0, 100, 50].map((d, i) => (
										<span
											key={i}
											className="bg-blue-500 w-0.5 rounded-full animate-[soundbar_0.8s_ease-in-out_infinite]"
											style={{ animationDelay: `${d}ms`, height: "100%" }}
										/>
									))}
								</span>
								You
							</span>
						)}
					</div>
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
							{entries.map((entry, idx) => {
								const isLast = idx === entries.length - 1;
								const isInterviewer = entry.speaker === "Interviewer";
								const isThisEntryAISpeaking = isLast && isInterviewer && isAISpeaking && !isAITyping;
								const isThisEntryUserSpeaking = isLast && !isInterviewer && isUserSpeaking;

								return (
									<div
										key={entry.id}
										className="group rounded-xl px-3 py-2.5 hover:bg-slate-50 transition-colors"
									>
										<div className="flex items-center gap-2 mb-1">
											<span
												className={`text-xs font-bold ${isInterviewer ? "text-violet-600" : "text-blue-600"}`}
											>
												{entry.speaker}
											</span>

											{/* Speaking sound-wave indicator on the latest entry */}
											{isThisEntryAISpeaking && <SpeakingIndicator color="violet" />}
											{isThisEntryUserSpeaking && <SpeakingIndicator color="blue" />}

											<span className="text-[10px] text-slate-400 font-medium ml-auto">
												{entry.timestamp}
											</span>
										</div>
										<p className="text-sm text-slate-700 leading-relaxed">
											{entry.text}
										</p>
									</div>
								);
							})}

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
		</>
	);
}
