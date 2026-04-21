"use client";

import { CameraOff, MicOff } from "lucide-react";
import { useCallback } from "react";

interface VideoAreaProps {
	isVideoOff: boolean;
	isMuted: boolean;
	userName?: string;
	stream: MediaStream | null;
	isAISpeaking?: boolean;
	isUserSpeaking?: boolean;
}

export default function VideoArea({
	isVideoOff,
	isMuted,
	userName = "You",
	stream,
	isAISpeaking = false,
	isUserSpeaking = false,
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

					{/* AI avatar with speaking ring */}
					<div className="relative flex items-center justify-center">
						{/* Outer ring — expands when AI is speaking */}
						{isAISpeaking && (
							<>
								<span className="absolute inset-0 rounded-full bg-violet-500/30 animate-ping" style={{ margin: "-8px" }} />
								<span className="absolute inset-0 rounded-full border-2 border-violet-400/60 animate-pulse" style={{ margin: "-4px" }} />
							</>
						)}
						<div
							className={`flex items-center justify-center w-28 h-28 rounded-full overflow-hidden transition-all duration-300 ${isAISpeaking
								? "ring-4 ring-violet-500/70 shadow-[0_0_30px_rgba(139,92,246,0.5)]"
								: "ring-2 ring-violet-500/30"
								}`}
						>
							<img
								src="/ai-mascot.png"
								alt="AI Interviewer"
								className="w-full h-full object-cover"
							/>
						</div>
					</div>

					<div className="flex items-center gap-2">
						<p className="text-sm font-medium text-slate-300">
							AI Interviewer
						</p>
						{isAISpeaking && (
							<span className="flex items-end gap-px h-3" aria-label="AI speaking">
								{[0, 150, 50, 200, 100].map((delay, i) => (
									<span
										key={i}
										className="bg-violet-400 w-0.5 rounded-full"
										style={{
											height: "100%",
											animation: `soundbar 0.8s ease-in-out ${delay}ms infinite`,
										}}
									/>
								))}
							</span>
						)}
					</div>
				</div>
			</div>

			{/* Self-view PIP overlay */}
			<div
				className={`absolute top-4 right-4 z-20 w-70 h-40 rounded-xl overflow-hidden shadow-2xl transition-all duration-300 ${isUserSpeaking && !isMuted
					? "ring-2 ring-blue-400/80 shadow-[0_0_20px_rgba(59,130,246,0.4)]"
					: "ring-1 ring-white/10"
					}`}
			>
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
						{/* Sound-wave bars on PIP when user is speaking */}
						{isUserSpeaking && !isMuted && (
							<span className="flex items-end gap-px h-2.5 ml-0.5">
								{[0, 100, 50].map((d, i) => (
									<span
										key={i}
										className="bg-blue-400 w-0.5 rounded-full"
										style={{
											height: "100%",
											animation: `soundbar 0.8s ease-in-out ${d}ms infinite`,
										}}
									/>
								))}
							</span>
						)}
					</span>
					{isMuted && (
						<span className="flex items-center justify-center w-5 h-5 rounded-full bg-red-500/90">
							<MicOff className="w-3 h-3 text-white" />
						</span>
					)}
				</div>
			</div>

			{/* CSS keyframes for soundbar animation */}
			<style>{`
				@keyframes soundbar {
					0%, 100% { transform: scaleY(0.3); }
					50% { transform: scaleY(1); }
				}
			`}</style>
		</div>
	);
}
