import { useEffect, useState } from "react";

export function useControlbar() {
	const [isMuted, setIsMuted] = useState(false);
	const [isVideoOff, setIsVideoOff] = useState(false);
	const [isSettingsOpen, setIsSettingsOpen] = useState(false);
	const [isDisconnectOpen, setIsDisconnectOpen] = useState(false);
	const [stream, setStream] = useState<MediaStream | null>(null);
	const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
	const [selectedCamera, setSelectedCamera] = useState<string | undefined>();
	const [selectedMicrophone, setSelectedMicrophone] = useState<
		string | undefined
	>();
	const [selectedSpeaker, setSelectedSpeaker] = useState<
		string | undefined
	>();

	// Initialize media stream and enumerate devices
	useEffect(() => {
		let mediaStream: MediaStream;

		const initMedia = async () => {
			try {
				mediaStream = await navigator.mediaDevices.getUserMedia({
					video: true,
					audio: true,
				});

				setStream(mediaStream);

				const deviceList =
					await navigator.mediaDevices.enumerateDevices();
				setDevices(deviceList);

				const cam = deviceList.find((d) => d.kind === "videoinput");
				const mic = deviceList.find((d) => d.kind === "audioinput");
				const spk = deviceList.find((d) => d.kind === "audiooutput");

				setSelectedCamera(cam?.deviceId);
				setSelectedMicrophone(mic?.deviceId);
				setSelectedSpeaker(spk?.deviceId);
			} catch (err) {
				console.error("Media error:", err);
			}
		};

		initMedia();

		return () => {
			mediaStream?.getTracks().forEach((track) => track.stop());
		};
	}, []);

	const cameras = devices.filter((d) => d.kind === "videoinput");
	const mics = devices.filter((d) => d.kind === "audioinput");
	const speakers = devices.filter((d) => d.kind === "audiooutput");

	const switchDevices = async (cameraId?: string, micId?: string) => {
		if (stream) {
			stream.getTracks().forEach((track) => track.stop());
		}

		try {
			const newStream = await navigator.mediaDevices.getUserMedia({
				video: cameraId ? { deviceId: { exact: cameraId } } : true,
				audio: micId ? { deviceId: { exact: micId } } : true,
			});

			setStream(newStream);

			newStream.getAudioTracks().forEach((track) => {
				track.enabled = !isMuted;
			});

			newStream.getVideoTracks().forEach((track) => {
				track.enabled = !isVideoOff;
			});
		} catch (err) {
			console.error("Error switching devices:", err);
		}
	};

	const handleCameraChange = (id: string) => {
		setSelectedCamera(id);
		switchDevices(id, selectedMicrophone);
	};

	const handleMicChange = (id: string) => {
		setSelectedMicrophone(id);
		switchDevices(selectedCamera, id);
	};

	const handleToggleMute = () => {
		if (!stream) return;

		stream.getAudioTracks().forEach((track) => {
			track.enabled = !track.enabled;
		});

		setIsMuted((prev) => !prev);
	};

	const handleToggleVideo = async () => {
		if (!stream) return;

		const videoTrack = stream.getVideoTracks()[0];

		if (!videoTrack) return;

		if (videoTrack.readyState === "ended") {
			await switchDevices(selectedCamera, selectedMicrophone);
			setIsVideoOff(false);
			return;
		}

		// normal toggle
		videoTrack.enabled = !videoTrack.enabled;
		setIsVideoOff((prev) => !prev);
	};

	return {
		// State
		isMuted,
		isVideoOff,
		isSettingsOpen,
		isDisconnectOpen,
		stream,
		cameras,
		mics,
		speakers,
		selectedCamera,
		selectedMicrophone,
		selectedSpeaker,

		// State setters
		setIsSettingsOpen,
		setIsDisconnectOpen,
		setSelectedSpeaker,

		// Handlers
		handleToggleMute,
		handleToggleVideo,
		handleCameraChange,
		handleMicChange,
	};
}
