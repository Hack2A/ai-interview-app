"use client";

import { RefObject, useEffect, useRef, useState, useCallback } from "react";
import { UseFormRegister } from "react-hook-form";
import { Camera, Mic, ShieldCheck, Volume2, RefreshCw, ChevronDown } from "lucide-react";
import {
	DeviceStatus,
	Difficulty,
	InterviewFormData,
	InterviewType,
	ResumeMode,
	getDeviceStatusText,
} from "@/types/Interivewtypes";

type PreviewStepProps = {
	register: UseFormRegister<InterviewFormData>;
	cameraStatus: DeviceStatus;
	microphoneStatus: DeviceStatus;
	videoRef: RefObject<HTMLVideoElement | null>;
	handleCameraCheck: (deviceId?: string) => Promise<void>;
	handleMicrophoneCheck: (deviceId?: string) => Promise<void>;
	resumeMode: ResumeMode;
	interviewType: InterviewType;
	difficulty: Difficulty;
	aiProctoring: boolean;
	// Device lists + selections
	availableCameras: MediaDeviceInfo[];
	availableMics: MediaDeviceInfo[];
	availableSpeakers: MediaDeviceInfo[];
	selectedCameraId: string;
	selectedMicId: string;
	selectedSpeakerId: string;
	onCameraChange: (deviceId: string) => void;
	onMicChange: (deviceId: string) => void;
	onSpeakerChange: (deviceId: string) => void;
	// Live mic stream for volume meter
	micStream: MediaStream | null;
};

/** Real-time audio volume meter using Web Audio API. Returns 0–100. */
function useVolumeMeter(stream: MediaStream | null) {
	const [volume, setVolume] = useState(0);
	const animFrameRef = useRef<number | null>(null);
	const audioCtxRef = useRef<AudioContext | null>(null);

	useEffect(() => {
		if (!stream) {
			setVolume(0);
			return;
		}

		const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
		const ctx = new AudioCtx();
		audioCtxRef.current = ctx;

		const analyser = ctx.createAnalyser();
		analyser.fftSize = 256;
		const source = ctx.createMediaStreamSource(stream);
		source.connect(analyser);

		const data = new Uint8Array(analyser.frequencyBinCount);

		const tick = () => {
			analyser.getByteFrequencyData(data);
			const avg = data.reduce((a, b) => a + b, 0) / data.length;
			// Normalize to 0–100 (avg rarely exceeds ~80)
			setVolume(Math.min(100, Math.round((avg / 80) * 100)));
			animFrameRef.current = requestAnimationFrame(tick);
		};

		tick();

		return () => {
			if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
			source.disconnect();
			ctx.close().catch(() => { });
		};
	}, [stream]);

	return volume;
}

/** A styled <select> for device picking. */
function DeviceSelect({
	id,
	devices,
	value,
	onChange,
	disabled,
}: {
	id: string;
	devices: MediaDeviceInfo[];
	value: string;
	onChange: (id: string) => void;
	disabled: boolean;
}) {
	return (
		<div className="relative">
			<select
				id={id}
				value={value}
				onChange={(e) => onChange(e.target.value)}
				disabled={disabled}
				className="w-full appearance-none rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-9 text-sm text-slate-700 shadow-sm transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
			>
				{devices.length === 0 ? (
					<option value="">No devices found</option>
				) : (
					devices.map((d) => (
						<option key={d.deviceId} value={d.deviceId}>
							{d.label || `Device ${d.deviceId.slice(0, 8)}`}
						</option>
					))
				)}
			</select>
			<ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
		</div>
	);
}

/** Animated volume bar with color coding. */
function VolumeMeter({ volume, active }: { volume: number; active: boolean }) {
	const barColor =
		volume < 20 ? "bg-slate-300" : volume < 60 ? "bg-emerald-400" : volume < 85 ? "bg-amber-400" : "bg-red-500";

	return (
		<div className="mt-3">
			<div className="mb-1 flex items-center justify-between text-xs text-slate-500">
				<span className="flex items-center gap-1.5">
					<span
						className={`inline-block h-2 w-2 rounded-full transition-colors ${active && volume > 10 ? "animate-pulse bg-emerald-500" : "bg-slate-300"
							}`}
					/>
					{active ? (volume > 10 ? "Sound detected" : "Listening…") : "Mic inactive"}
				</span>
				<span className="font-mono font-semibold">{active ? `${volume}%` : "—"}</span>
			</div>
			<div className="h-3 w-full overflow-hidden rounded-full bg-slate-100">
				<div
					className={`h-full rounded-full transition-all duration-75 ${barColor}`}
					style={{ width: `${active ? volume : 0}%` }}
				/>
			</div>
			{/* Fine-grained segment bars for visual flair */}
			<div className="mt-1 flex gap-0.5">
				{Array.from({ length: 20 }).map((_, i) => {
					const segmentThreshold = (i + 1) * 5;
					const filled = active && volume >= segmentThreshold;
					const color =
						i < 10 ? "bg-emerald-400" : i < 16 ? "bg-amber-400" : "bg-red-500";
					return (
						<div
							key={i}
							className={`h-1.5 flex-1 rounded-sm transition-colors duration-75 ${filled ? color : "bg-slate-100"
								}`}
						/>
					);
				})}
			</div>
		</div>
	);
}

export default function PreviewStep({
	register,
	cameraStatus,
	microphoneStatus,
	videoRef,
	handleCameraCheck,
	handleMicrophoneCheck,
	resumeMode,
	interviewType,
	difficulty,
	aiProctoring,
	availableCameras,
	availableMics,
	availableSpeakers,
	selectedCameraId,
	selectedMicId,
	selectedSpeakerId,
	onCameraChange,
	onMicChange,
	onSpeakerChange,
	micStream,
}: PreviewStepProps) {
	const volume = useVolumeMeter(microphoneStatus === "ready" ? micStream : null);
	const isMicActive = microphoneStatus === "ready";

	const handleCameraDeviceChange = (id: string) => {
		onCameraChange(id);
		handleCameraCheck(id);
	};

	const handleMicDeviceChange = (id: string) => {
		onMicChange(id);
		handleMicrophoneCheck(id);
	};

	return (
		<section className="space-y-5">
			<div>
				<h2 className="text-2xl font-semibold text-slate-900">Preview &amp; Proctoring</h2>
				<p className="text-sm text-slate-600">
					Toggle AI proctoring, verify your camera and microphone, then start the interview.
				</p>
			</div>

			{/* AI Proctoring toggle */}
			<div className="rounded-xl border border-slate-200 p-4">
				<label className="flex cursor-pointer items-center justify-between">
					<div className="flex items-center gap-3">
						<ShieldCheck className="h-5 w-5 text-slate-700" />
						<div>
							<p className="font-semibold text-slate-900">Enable AI Proctoring</p>
							<p className="text-sm text-slate-600">Monitor interview integrity with AI checks.</p>
						</div>
					</div>
					<input type="checkbox" className="h-5 w-5 accent-blue-600" {...register("aiProctoring")} />
				</label>
			</div>

			<div className="grid gap-4 lg:grid-cols-2">
				{/* ── Camera ── */}
				<div className="rounded-xl border border-slate-200 p-4">
					<div className="mb-3 flex items-center justify-between">
						<div className="flex items-center gap-2 text-slate-900">
							<Camera className="h-5 w-5" />
							<p className="font-semibold">Camera</p>
						</div>
						<span
							className={`text-xs font-semibold ${cameraStatus === "ready"
								? "text-emerald-600"
								: cameraStatus === "blocked"
									? "text-red-500"
									: "text-slate-500"
								}`}
						>
							{getDeviceStatusText(cameraStatus, "✓ Ready")}
						</span>
					</div>

					<video
						ref={videoRef}
						autoPlay
						muted
						playsInline
						className="h-44 w-full rounded-lg bg-slate-100 object-cover"
					/>

					{/* Camera device selector */}
					{availableCameras.length > 0 && (
						<div className="mt-3">
							<label className="mb-1 block text-xs font-medium text-slate-500">Camera device</label>
							<DeviceSelect
								id="camera-select"
								devices={availableCameras}
								value={selectedCameraId}
								onChange={handleCameraDeviceChange}
								disabled={cameraStatus === "checking"}
							/>
						</div>
					)}

					<button
						type="button"
						onClick={() => handleCameraCheck(selectedCameraId || undefined)}
						disabled={cameraStatus === "checking"}
						className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-60"
					>
						<RefreshCw className={`h-4 w-4 ${cameraStatus === "checking" ? "animate-spin" : ""}`} />
						{cameraStatus === "checking" ? "Checking…" : "Check Camera"}
					</button>
				</div>

				{/* ── Microphone ── */}
				<div className="rounded-xl border border-slate-200 p-4">
					<div className="mb-3 flex items-center justify-between">
						<div className="flex items-center gap-2 text-slate-900">
							<Mic className="h-5 w-5" />
							<p className="font-semibold">Microphone</p>
						</div>
						<span
							className={`text-xs font-semibold ${microphoneStatus === "ready"
								? "text-emerald-600"
								: microphoneStatus === "blocked"
									? "text-red-500"
									: "text-slate-500"
								}`}
						>
							{getDeviceStatusText(microphoneStatus, "✓ Ready")}
						</span>
					</div>

					{/* Noise / volume meter area */}
					<div className="flex h-44 flex-col justify-between rounded-lg bg-slate-50 p-4 border border-slate-100">
						<div className="text-center">
							<Mic
								className={`mx-auto mb-2 h-10 w-10 transition-all ${isMicActive
									? volume > 10
										? "text-emerald-500 scale-110"
										: "text-blue-400"
									: "text-slate-300"
									}`}
							/>
							<p className="text-xs text-slate-500">
								{isMicActive
									? "Speak into your microphone"
									: "Click “Check Microphone” to test"}
							</p>
						</div>
						<VolumeMeter volume={volume} active={isMicActive} />
					</div>

					{/* Mic device selector */}
					{availableMics.length > 0 && (
						<div className="mt-3">
							<label className="mb-1 block text-xs font-medium text-slate-500">Microphone device</label>
							<DeviceSelect
								id="mic-select"
								devices={availableMics}
								value={selectedMicId}
								onChange={handleMicDeviceChange}
								disabled={microphoneStatus === "checking"}
							/>
						</div>
					)}

					<button
						type="button"
						onClick={() => handleMicrophoneCheck(selectedMicId || undefined)}
						disabled={microphoneStatus === "checking"}
						className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-60"
					>
						<RefreshCw className={`h-4 w-4 ${microphoneStatus === "checking" ? "animate-spin" : ""}`} />
						{microphoneStatus === "checking" ? "Checking…" : "Check Microphone"}
					</button>
				</div>
			</div>

			{/* ── Speaker selector ── */}
			{availableSpeakers.length > 0 && (
				<div className="rounded-xl border border-slate-200 p-4">
					<div className="mb-3 flex items-center gap-2 text-slate-900">
						<Volume2 className="h-5 w-5" />
						<p className="font-semibold">Speaker / Audio Output</p>
					</div>
					<DeviceSelect
						id="speaker-select"
						devices={availableSpeakers}
						value={selectedSpeakerId}
						onChange={onSpeakerChange}
						disabled={false}
					/>
					<p className="mt-2 text-xs text-slate-500">
						This is where you&apos;ll hear the AI interviewer&apos;s voice.
					</p>
				</div>
			)}

			{/* Summary */}
			<div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
				<p className="font-semibold text-slate-900">Current Selection Summary</p>
				<ul className="mt-2 space-y-1">
					<li>Resume mode: {resumeMode}</li>
					<li>Interview type: {interviewType}</li>
					<li>Difficulty: {difficulty}</li>
					<li>AI Proctoring: {aiProctoring ? "Enabled" : "Disabled"}</li>
				</ul>
			</div>
		</section>
	);
}
