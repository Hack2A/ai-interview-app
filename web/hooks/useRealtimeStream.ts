import { useEffect, useRef, useState } from "react";

interface UseRealtimeStreamOptions {
	/** When true, streaming starts automatically once the stream is available */
	autoStart?: boolean;
}

/**
 * Hook that captures audio from a MediaStream via MediaRecorder
 * and sends binary chunks through a provided callback.
 *
 * The callback is typically `interviewHook.sendAudio` from useInterview,
 * which forwards chunks to the InterviewWebSocket.
 */
export function useRealtimeStream(
	stream: MediaStream | null,
	sendAudio: (data: Blob) => void,
	options: UseRealtimeStreamOptions = {},
) {
	const { autoStart = false } = options;

	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const isStreamingRef = useRef(false);
	const sendAudioRef = useRef(sendAudio);

	const [isStreaming, setIsStreaming] = useState(false);

	// Keep refs in sync
	useEffect(() => {
		isStreamingRef.current = isStreaming;
	}, [isStreaming]);

	useEffect(() => {
		sendAudioRef.current = sendAudio;
	}, [sendAudio]);

	// Auto-start when stream becomes available
	useEffect(() => {
		if (!stream) return;

		if (autoStart && !isStreamingRef.current) {
			startStreaming();
		} else if (isStreamingRef.current) {
			// Restart on device switch
			restartStreaming();
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [stream]);

	const startStreaming = () => {
		if (!stream || isStreamingRef.current) return;

		try {
			const audioStream = new MediaStream(stream.getAudioTracks());

			const recorder = new MediaRecorder(audioStream, {
				mimeType: "audio/webm;codecs=opus",
			});

			recorder.ondataavailable = (event) => {
				if (event.data.size > 0) {
					sendAudioRef.current(event.data);
				}
			};

			recorder.onerror = (err) => {
				console.error("❌ Recorder error:", err);
			};

			recorder.onstop = () => {
				console.log("🎙️ Recorder stopped");
			};

			recorder.start(250); // chunk every 250ms
			mediaRecorderRef.current = recorder;
			setIsStreaming(true);
			console.log("✅ Audio streaming started");
		} catch (err) {
			console.error("❌ Failed to start streaming:", err);
		}
	};

	const stopStreaming = () => {
		try {
			if (mediaRecorderRef.current) {
				if (mediaRecorderRef.current.state !== "inactive") {
					mediaRecorderRef.current.stop();
				}
				mediaRecorderRef.current = null;
			}
		} catch (err) {
			console.error("❌ Stop error:", err);
		} finally {
			setIsStreaming(false);
		}
	};

	const restartStreaming = () => {
		stopStreaming();
		setTimeout(() => {
			startStreaming();
		}, 100);
	};

	// Cleanup on unmount
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
	};
}
