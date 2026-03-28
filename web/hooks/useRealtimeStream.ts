import { useEffect, useRef, useState } from "react";

interface UseRealtimeStreamOptions {
	/** When true, streaming starts automatically once the stream is available */
	autoStart?: boolean;
}

export function useRealtimeStream(
	stream: MediaStream | null,
	options: UseRealtimeStreamOptions = {}
) {
	const { autoStart = false } = options;

	const wsRef = useRef<WebSocket | null>(null);
	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const isStreamingRef = useRef(false);

	const [isStreaming, setIsStreaming] = useState(false);

	// keep ref in sync
	useEffect(() => {
		isStreamingRef.current = isStreaming;
	}, [isStreaming]);

	// auto-start streaming when stream becomes available
	useEffect(() => {
		if (!stream) return;

		if (autoStart && !isStreamingRef.current) {
			startStreaming();
		} else if (isStreamingRef.current) {
			// restart on device switch
			restartStreaming();
		}
	}, [stream]);

	const startStreaming = () => {
		if (!stream || isStreamingRef.current) return;

		try {
			const audioStream = new MediaStream(stream.getAudioTracks());

			const recorder = new MediaRecorder(audioStream, {
				mimeType: "audio/webm;codecs=opus",
			});

			const ws = new WebSocket("ws://localhost:8000/ws/interview");

			ws.onopen = () => {
				console.log("✅ WebSocket connected");
				recorder.start(250); // chunk every 250ms
				setIsStreaming(true);
			};

			ws.onerror = (err) => {
				console.error("❌ WebSocket error:", err);
				stopStreaming();
			};

			ws.onclose = () => {
				console.log("🔌 WebSocket closed");
				setIsStreaming(false);
			};

			recorder.ondataavailable = (event) => {
				if (
					event.data.size > 0 &&
					ws.readyState === WebSocket.OPEN &&
					ws.bufferedAmount < 1_000_000 // basic backpressure check
				) {
					ws.send(event.data);
				}
			};

			recorder.onerror = (err) => {
				console.error("❌ Recorder error:", err);
			};

			recorder.onstop = () => {
				console.log("🎙️ Recorder stopped");
			};

			wsRef.current = ws;
			mediaRecorderRef.current = recorder;
		} catch (err) {
			console.error("❌ Failed to start streaming:", err);
		}
	};

	const stopStreaming = () => {
		try {
			if (mediaRecorderRef.current) {
				mediaRecorderRef.current.stop();
				mediaRecorderRef.current = null;
			}

			if (wsRef.current) {
				if (wsRef.current.readyState === WebSocket.OPEN) {
					wsRef.current.close();
				}
				wsRef.current = null;
			}
		} catch (err) {
			console.error("❌ Stop error:", err);
		} finally {
			setIsStreaming(false);
		}
	};

	const restartStreaming = async () => {
		stopStreaming();

		// wait for cleanup (important)
		setTimeout(() => {
			startStreaming();
		}, 100);
	};

	// cleanup on unmount
	useEffect(() => {
		return () => {
			stopStreaming();
		};
	}, []);

	return {
		startStreaming,
		stopStreaming,
		isStreaming,
	};
}
