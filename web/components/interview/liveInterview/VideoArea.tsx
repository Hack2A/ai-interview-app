"use client";

import { VideoAreaProps } from "@/types/LiveInterviewTypes";
import { CameraOff, MicOff } from "lucide-react";
import { useCallback } from "react";

export default function VideoArea({
	isVideoOff,
	isMuted,
	userName = "You",
	stream,
}: VideoAreaProps) {
	const videoCallbackRef = useCallback(
		(node: HTMLVideoElement | null) => {
			if (node && stream) {
				node.srcObject = stream;
			}
		},
		[stream],
	);

	return (
		<div
			className="relative flex-1 min-h-0 rounded-2xl overflow-hidden bg-slate-900"
			style={{ resize: "both" }}
		>
			{/* Main video (AI Interviewer) */}
			<div className="absolute inset-0 flex items-center justify-center">
				<div className="absolute inset-0 bg-linear-to-br from-slate-800 via-slate-900 to-slate-950" />
				<div className="relative z-10 flex flex-col items-center gap-3">
					<div className="flex items-center justify-center w-28 h-28 rounded-full bg-slate-800/60 ring-2 ring-violet-500/30 overflow-hidden">
						<img
							src="/ai-mascot.png"
							alt="AI Interviewer"
							className="w-full h-full object-cover"
						/>
					</div>
					<p className="text-sm font-medium text-slate-300">
						AI Interviewer
					</p>
				</div>
			</div>

			{/* Self-view PIP overlay */}
			<div className="absolute top-4 right-4 z-20 w-70 h-40 rounded-xl overflow-hidden shadow-2xl ring-1 ring-white/10">
				{isVideoOff ? (
					<div className="flex items-center justify-center w-full h-full bg-slate-800">
						<div className="flex flex-col items-center gap-1.5">
							<CameraOff className="w-5 h-5 text-slate-400" />
							<span className="text-xs text-slate-400">
								Camera off
							</span>
						</div>
					</div>
				) : (
					<div className="w-full h-full bg-linear-to-br from-indigo-900 via-violet-900 to-purple-900 flex items-center justify-center">
						<video
							ref={videoCallbackRef}
							autoPlay
							playsInline
							muted
							className="w-full h-full object-cover"
						/>
					</div>
				)}

				{/* PIP name badge */}
				<div className="absolute bottom-2 left-2 right-2 flex items-center justify-between">
					<span className="flex items-center gap-1.5 rounded-md bg-black/60 backdrop-blur-sm px-2 py-0.5 text-xs font-medium text-white">
						{userName}
					</span>
					{isMuted && (
						<span className="flex items-center justify-center w-5 h-5 rounded-full bg-red-500/90">
							<MicOff className="w-3 h-3 text-white" />
						</span>
					)}
				</div>
			</div>
		</div>
	);
}
