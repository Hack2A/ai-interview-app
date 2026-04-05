"""Proctoring engine — full CV analysis using MediaPipe FaceMesh + YOLOv8.

Detects:
- Face presence / multiple people
- Gaze direction (iris tracking)
- Head pose (solvePnP pitch/yaw/roll)
- Mouth movement (lip landmarks)
- Earpiece indicators (ear-region analysis)
- Prohibited objects (phone, book, laptop via YOLOv8-nano)
"""
import logging
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from config import settings

logger = logging.getLogger("ProctoringEngine")

# ── Thresholds ────────────────────────────────────────────────────
GAZE_LEFT_THRESHOLD = 0.25
GAZE_RIGHT_THRESHOLD = 0.75
GAZE_UP_THRESHOLD = 0.25
GAZE_DOWN_THRESHOLD = 0.75
HEAD_TILT_DOWN_THRESHOLD = -25
HEAD_YAW_THRESHOLD = 30

# Mouth landmarks: upper lip top (13), lower lip bottom (14), left corner (78), right corner (308)
MOUTH_UPPER = 13
MOUTH_LOWER = 14
MOUTH_LEFT = 78
MOUTH_RIGHT = 308

# Ear region landmarks for earpiece heuristic
LEFT_EAR_LANDMARKS = [234, 227, 137, 177]
RIGHT_EAR_LANDMARKS = [454, 447, 366, 401]


class ProctoringEngine:
    """Computer vision engine for interview proctoring using MediaPipe FaceMesh + YOLO."""

    def __init__(self) -> None:
        try:
            from mediapipe.python.solutions import face_mesh as mp_face_mesh
            self.mp_face_mesh = mp_face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except (ImportError, AttributeError):
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

        # Iris and eye landmark indices
        self.iris_left = list(range(474, 479))
        self.iris_right = list(range(469, 474))
        self.left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        self.right_eye_indices = [362, 263, 387, 386, 385, 384, 398]

        # Object detector (lazy-loaded)
        self._object_detector = None
        self._object_detection_enabled = settings.ENABLE_OBJECT_DETECTION

        logger.info("Proctoring engine initialized")

    # ── Object Detector (lazy) ────────────────────────────────────

    @property
    def object_detector(self):
        if self._object_detector is None and self._object_detection_enabled:
            try:
                from src.eyes.object_detector import ObjectDetector
                self._object_detector = ObjectDetector()
                if not self._object_detector.is_available:
                    self._object_detector = None
                    self._object_detection_enabled = False
            except Exception as e:
                logger.warning(f"Object detector init failed: {e}")
                self._object_detection_enabled = False
        return self._object_detector

    # ── Face Detection ────────────────────────────────────────────

    def detect_faces(self, frame: np.ndarray) -> tuple[int, Optional[list]]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return 0, None

        return len(results.multi_face_landmarks), results.multi_face_landmarks

    # ── Gaze Direction ────────────────────────────────────────────

    def calculate_gaze_direction(self, face_landmarks, frame_shape: tuple) -> tuple[str, float, float]:
        try:
            h, w = frame_shape[:2]

            if not face_landmarks or not face_landmarks.landmark:
                return "unknown", 0.5, 0.5

            if len(face_landmarks.landmark) <= max(self.iris_left + self.left_eye_indices):
                return "unknown", 0.5, 0.5

            left_iris_points = []
            for idx in self.iris_left:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    left_iris_points.append((x, y))

            if not left_iris_points:
                return "center", 0.5, 0.5

            left_iris_center = np.mean(left_iris_points, axis=0)

            left_eye_points = []
            for idx in self.left_eye_indices:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    left_eye_points.append((x, y))

            if not left_eye_points:
                return "center", 0.5, 0.5

            eye_left = min([p[0] for p in left_eye_points])
            eye_right = max([p[0] for p in left_eye_points])
            eye_top = min([p[1] for p in left_eye_points])
            eye_bottom = max([p[1] for p in left_eye_points])

            eye_width = eye_right - eye_left
            eye_height = eye_bottom - eye_top

            if eye_width == 0 or eye_height == 0:
                return "center", 0.5, 0.5

            horizontal_ratio = (left_iris_center[0] - eye_left) / (eye_width + 1e-6)
            vertical_ratio = (left_iris_center[1] - eye_top) / (eye_height + 1e-6)

            gaze = "center"

            if horizontal_ratio < GAZE_LEFT_THRESHOLD:
                gaze = "left"
            elif horizontal_ratio > GAZE_RIGHT_THRESHOLD:
                gaze = "right"

            if vertical_ratio > GAZE_DOWN_THRESHOLD:
                gaze = "down"
            elif vertical_ratio < GAZE_UP_THRESHOLD:
                gaze = "up"

            return gaze, horizontal_ratio, vertical_ratio
        except Exception as e:
            logger.error(f"Gaze calculation error: {e}")
            return "unknown", 0.5, 0.5

    # ── Head Pose ─────────────────────────────────────────────────

    def calculate_head_pose(self, face_landmarks, frame_shape: tuple) -> tuple[float, float, float]:
        """Estimate head pose (pitch, yaw, roll) using solvePnP."""
        h, w = frame_shape[:2]

        required_indices = [1, 152, 33, 263, 61, 291]
        max_index = max(required_indices)

        if len(face_landmarks.landmark) <= max_index:
            return 0, 0, 0

        nose_tip = face_landmarks.landmark[1]
        chin = face_landmarks.landmark[152]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        left_mouth = face_landmarks.landmark[61]
        right_mouth = face_landmarks.landmark[291]

        image_points = np.array([
            (nose_tip.x * w, nose_tip.y * h),
            (chin.x * w, chin.y * h),
            (left_eye.x * w, left_eye.y * h),
            (right_eye.x * w, right_eye.y * h),
            (left_mouth.x * w, left_mouth.y * h),
            (right_mouth.x * w, right_mouth.y * h)
        ], dtype=np.float64)

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0),
            (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0),
            (150.0, -150.0, -125.0)
        ])

        focal_length = w
        center = (w // 2, h // 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1))

        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return 0, 0, 0

        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)

        return angles[0], angles[1], angles[2]  # pitch, yaw, roll

    # ── Mouth Movement Analysis ───────────────────────────────────

    def analyze_mouth(self, face_landmarks, frame_shape: tuple) -> dict:
        """Analyze mouth openness from FaceMesh lip landmarks.

        Returns dict with:
            - mouth_open_ratio: float (0 = closed, 1 = wide open)
            - is_mouth_open: bool (exceeds threshold)
            - mouth_width: pixel width of mouth
        """
        h, w = frame_shape[:2]
        max_idx = max(MOUTH_UPPER, MOUTH_LOWER, MOUTH_LEFT, MOUTH_RIGHT)

        if len(face_landmarks.landmark) <= max_idx:
            return {"mouth_open_ratio": 0, "is_mouth_open": False, "mouth_width": 0}

        upper = face_landmarks.landmark[MOUTH_UPPER]
        lower = face_landmarks.landmark[MOUTH_LOWER]
        left = face_landmarks.landmark[MOUTH_LEFT]
        right = face_landmarks.landmark[MOUTH_RIGHT]

        # Vertical distance (lip separation)
        vertical_dist = abs(lower.y - upper.y) * h
        # Horizontal distance (mouth width) as normalization reference
        horizontal_dist = abs(right.x - left.x) * w

        if horizontal_dist < 1:
            return {"mouth_open_ratio": 0, "is_mouth_open": False, "mouth_width": 0}

        ratio = vertical_dist / horizontal_dist

        return {
            "mouth_open_ratio": round(ratio, 3),
            "is_mouth_open": ratio > settings.MOUTH_OPEN_THRESHOLD,
            "mouth_width": round(horizontal_dist, 1),
        }

    # ── Earpiece Detection (Heuristic) ────────────────────────────

    def detect_earpiece(self, face_landmarks, frame: np.ndarray) -> dict:
        """Heuristic earpiece detection using ear-region color/texture analysis.

        Checks if the ear region has an abnormal dark cluster that could indicate
        an earbud. This is inherently noisy — confidence is always moderate.
        """
        h, w = frame.shape[:2]

        if len(face_landmarks.landmark) <= max(LEFT_EAR_LANDMARKS + RIGHT_EAR_LANDMARKS):
            return {"earpiece_detected": False, "confidence": 0, "side": None}

        for side, indices in [("left", LEFT_EAR_LANDMARKS), ("right", RIGHT_EAR_LANDMARKS)]:
            points = []
            for idx in indices:
                if idx < len(face_landmarks.landmark):
                    lm = face_landmarks.landmark[idx]
                    points.append((int(lm.x * w), int(lm.y * h)))

            if len(points) < 3:
                continue

            pts = np.array(points)
            x_min = max(0, pts[:, 0].min() - 10)
            x_max = min(w, pts[:, 0].max() + 10)
            y_min = max(0, pts[:, 1].min() - 10)
            y_max = min(h, pts[:, 1].max() + 10)

            if x_max <= x_min or y_max <= y_min:
                continue

            ear_region = frame[y_min:y_max, x_min:x_max]
            if ear_region.size == 0:
                continue

            # Convert to grayscale and look for dark clusters (earbuds are usually dark)
            gray = cv2.cvtColor(ear_region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            dark_ratio = np.count_nonzero(thresh) / (thresh.size + 1e-6)

            # Earbuds typically create a concentrated dark region
            if dark_ratio > 0.35:
                return {
                    "earpiece_detected": True,
                    "confidence": round(min(dark_ratio, 0.85), 2),
                    "side": side,
                }

        return {"earpiece_detected": False, "confidence": 0, "side": None}

    # ── Get Face Bounding Box ─────────────────────────────────────

    def get_face_bbox(self, face_landmarks, frame_shape: tuple) -> tuple:
        """Extract bounding box from face landmarks."""
        h, w = frame_shape[:2]
        xs = [lm.x * w for lm in face_landmarks.landmark]
        ys = [lm.y * h for lm in face_landmarks.landmark]
        return (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))

    # ── Main Analysis ─────────────────────────────────────────────

    def analyze_frame(self, frame: np.ndarray) -> tuple[list[str], dict]:
        """Analyze a single frame for all proctoring violations.

        Returns:
            (violations_list, metadata_dict)
        """
        violations = []
        metadata = {}

        face_count, landmarks = self.detect_faces(frame)
        metadata["face_count"] = face_count

        if face_count == 0:
            violations.append("user_left")
            metadata["gaze"] = "unknown"
            # Still run object detection even without face
            if self.object_detector:
                obj_detections = self.object_detector.detect(frame)
                if obj_detections:
                    metadata["objects"] = obj_detections
                    for det in obj_detections:
                        violations.append(f"object_{det['class_name'].replace(' ', '_')}")
            return violations, metadata

        if face_count > 1:
            violations.append("multiple_people")

        face_landmarks = landmarks[0]

        # ── Gaze ──
        gaze, h_ratio, v_ratio = self.calculate_gaze_direction(face_landmarks, frame.shape)
        metadata["gaze"] = gaze
        metadata["gaze_ratios"] = {"horizontal": round(h_ratio, 3), "vertical": round(v_ratio, 3)}

        if gaze == "down":
            violations.append("looking_down")
        elif gaze in ["left", "right"]:
            violations.append("looking_away")

        # ── Head Pose ──
        try:
            pitch, yaw, roll = self.calculate_head_pose(face_landmarks, frame.shape)
            metadata["head_pose"] = {"pitch": round(pitch, 1), "yaw": round(yaw, 1), "roll": round(roll, 1)}

            if pitch < HEAD_TILT_DOWN_THRESHOLD:
                if "looking_down" not in violations:
                    violations.append("head_tilted_down")

            if abs(yaw) > HEAD_YAW_THRESHOLD:
                if "looking_away" not in violations:
                    violations.append("head_turned_away")
        except (cv2.error, ValueError, IndexError) as e:
            logger.debug(f"Head pose estimation failed: {e}")
            metadata["head_pose"] = {"pitch": 0, "yaw": 0, "roll": 0}

        # ── Mouth Movement ──
        if settings.ENABLE_MOUTH_ANALYSIS:
            mouth_data = self.analyze_mouth(face_landmarks, frame.shape)
            metadata["mouth"] = mouth_data
            if mouth_data["is_mouth_open"]:
                violations.append("mouth_open")

        # ── Earpiece Detection ──
        if settings.ENABLE_EARPIECE_DETECTION:
            earpiece_data = self.detect_earpiece(face_landmarks, frame)
            metadata["earpiece"] = earpiece_data
            if earpiece_data["earpiece_detected"]:
                violations.append("earpiece_suspected")

        # ── Object Detection (YOLO) ──
        if self.object_detector:
            obj_detections = self.object_detector.detect(frame)
            if obj_detections:
                metadata["objects"] = obj_detections
                face_bbox = self.get_face_bbox(face_landmarks, frame.shape)

                for det in obj_detections:
                    viol_name = f"object_{det['class_name'].replace(' ', '_')}"
                    if viol_name not in violations:
                        violations.append(viol_name)

                # Phone-near-ear check (supplements earpiece heuristic)
                if self.object_detector.detect_phone_near_ear(obj_detections, face_bbox):
                    if "earpiece_suspected" not in violations:
                        violations.append("phone_near_ear")

        return violations, metadata

    def cleanup(self) -> None:
        """Release MediaPipe resources."""
        self.face_mesh.close()
