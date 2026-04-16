import { useEffect, useRef, useState, useCallback } from "react";

interface UseRealtimeStreamOptions {
	autoStart?: boolean;
	silenceDelay?: number; // MS of silence before auto-sending
	volumeThreshold?: number; // 0 to 255 volume threshold
}

/**
 * Hook that captures audio from a MediaStream via MediaRecorder.
 * Monitors volume using Web Audio API to detect when the user stops speaking.
 * Sends the combined binary blob through `sendAudio` upon silence detection.
 */
export function useRealtimeStream(
	stream: MediaStream | null,
	sendAudio: (data: Blob) => void,
	options: UseRealtimeStreamOptions = {},
) {
	const { autoStart = false, silenceDelay = 2000, volumeThreshold = 10 } = options;

	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const isStreamingRef = useRef(false);
	const sendAudioRef = useRef(sendAudio);

	const [isStreaming, setIsStreaming] = useState(false);
	const [isSpeaking, setIsSpeaking] = useState(false);

	// VAD Refs
	const audioContextRef = useRef<AudioContext | null>(null);
	const analyserRef = useRef<AnalyserNode | null>(null);
	const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
	const vadFrameRef = useRef<number | null>(null);
	const lastSpokeAtRef = useRef<number>(Date.now());
	const hasSpokenRef = useRef(false);

	// Ensure we only create the AudioContext once per component lifecycle
	useEffect(() => {
		const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
		audioContextRef.current = new AudioContextClass();
		return () => {
			if (audioContextRef.current?.state !== "closed") {
				audioContextRef.current?.close().catch(console.error);
			}
		};
	}, []);

	useEffect(() => {
		isStreamingRef.current = isStreaming;
	}, [isStreaming]);

	useEffect(() => {
		sendAudioRef.current = sendAudio;
	}, [sendAudio]);

	useEffect(() => {
		if (!stream) return;
		if (autoStart && !isStreamingRef.current) {
			startStreaming();
		} else if (isStreamingRef.current) {
			restartStreaming();
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [stream]);

	const detectSilence = () => {
		if (!analyserRef.current || !isStreamingRef.current) return;

		const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
		analyserRef.current.getByteFrequencyData(dataArray);

		let sum = 0;
		for (let i = 0; i < dataArray.length; i++) {
			sum += dataArray[i];
		}
		const averageVolume = sum / dataArray.length;

		if (averageVolume > volumeThreshold) {
			lastSpokeAtRef.current = Date.now();
			if (!hasSpokenRef.current) {
				hasSpokenRef.current = true;
				setIsSpeaking(true);
				console.log("🎙️ VAD: Speech detected.");
			}
		} else {
			if (hasSpokenRef.current) {
				const silenceDuration = Date.now() - lastSpokeAtRef.current;
				if (silenceDuration > silenceDelay) {
					console.log(`🎙️ VAD: ${silenceDelay}ms silence detected. Auto-sending audio...`);
					hasSpokenRef.current = false; // Reset for next chunk
					restartStreaming(); // This stops recorder, sends audio, and restarts
					return; // Break animation frame
				}
			}
		}

		vadFrameRef.current = requestAnimationFrame(detectSilence);
	};

	const startStreaming = () => {
		if (!stream || isStreamingRef.current) return;

		try {
			if (audioContextRef.current?.state === "suspended") {
				audioContextRef.current.resume();
			}

			const audioStream = new MediaStream(stream.getAudioTracks());
			const recorder = new MediaRecorder(audioStream, {
				mimeType: "audio/webm;codecs=opus",
			});

			const audioChunks: Blob[] = [];

			recorder.ondataavailable = (event) => {
				if (event.data.size > 0) {
					audioChunks.push(event.data);
				}
			};

			recorder.onerror = (err) => console.error("❌ Recorder error:", err);

			recorder.onstop = () => {
				if (audioChunks.length > 0) {
					const audioBlob = new Blob(audioChunks, { type: "audio/webm;codecs=opus" });
					sendAudioRef.current(audioBlob);
				}
			};

			recorder.start();
			mediaRecorderRef.current = recorder;
			setIsStreaming(true);
			hasSpokenRef.current = false;
			setIsSpeaking(false);

			// Connect VAD
			if (audioContextRef.current) {
				if (sourceRef.current) {
					sourceRef.current.disconnect();
				}
				sourceRef.current = audioContextRef.current.createMediaStreamSource(audioStream);
				analyserRef.current = audioContextRef.current.createAnalyser();
				analyserRef.current.fftSize = 256;
				sourceRef.current.connect(analyserRef.current);

				lastSpokeAtRef.current = Date.now();
				if (vadFrameRef.current) cancelAnimationFrame(vadFrameRef.current);
				detectSilence();
			}
		} catch (err) {
			console.error("❌ Failed to start streaming:", err);
		}
	};

	const stopStreaming = () => {
		// Stop VAD loop but DO NOT close the AudioContext
		if (vadFrameRef.current) cancelAnimationFrame(vadFrameRef.current);

		try {
			if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
				mediaRecorderRef.current.stop();
			}
			mediaRecorderRef.current = null;
		} catch (err) {
			console.error("❌ Stop error:", err);
		} finally {
			setIsStreaming(false);
			setIsSpeaking(false);
		}
	};

	const restartStreaming = useCallback(() => {
		stopStreaming();
		setTimeout(() => {
			startStreaming();
		}, 150);
	}, []);

	useEffect(() => {
		return () => {
			stopStreaming();
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	return {
		startStreaming,
		stopStreaming,
		isStreaming,
		isSpeaking,
	};
}
