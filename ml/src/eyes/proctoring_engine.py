import cv2
import mediapipe as mp
import numpy as np
import logging

logger = logging.getLogger("ProctoringEngine")

class ProctoringEngine:
    def __init__(self):
        try:
            from mediapipe.python.solutions import face_mesh as mp_face_mesh
            
            self.mp_face_mesh = mp_face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

        
        self.iris_left = list(range(474, 479))
        self.iris_right = list(range(469, 474))
        
        self.left_eye_indices = [33, 133, 160, 159, 158, 157, 173]
        self.right_eye_indices = [362, 263, 387, 386, 385, 384, 398]
        
        logger.info("Proctoring engine initialized")
    
    def detect_faces(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return 0, None
        
        return len(results.multi_face_landmarks), results.multi_face_landmarks
    
    def calculate_gaze_direction(self, face_landmarks, frame_shape):
        try:
            h, w = frame_shape[:2]
            
            if not face_landmarks or not face_landmarks.landmark:
                return "unknown", 0.5, 0.5
            
            if len(face_landmarks.landmark) < max(self.iris_left + self.left_eye_indices):
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
            
            if horizontal_ratio < 0.25:
                gaze = "left"
            elif horizontal_ratio > 0.75:
                gaze = "right"
            
            if vertical_ratio > 0.75:
                gaze = "down"
            elif vertical_ratio < 0.25:
                gaze = "up"
            
            return gaze, horizontal_ratio, vertical_ratio
        except Exception as e:
            logger.error(f"Gaze calculation error: {e}")
            return "unknown", 0.5, 0.5
    
    def calculate_head_pose(self, face_landmarks, frame_shape):
        h, w = frame_shape[:2]
        
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
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return 0, 0, 0
        
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
        
        pitch = angles[0] * 360
        yaw = angles[1] * 360
        roll = angles[2] * 360
        
        return pitch, yaw, roll
    
    def analyze_frame(self, frame):
        violations = []
        
        face_count, landmarks = self.detect_faces(frame)
        
        if face_count == 0:
            violations.append("user_left")
            return violations, {"face_count": 0, "gaze": "unknown"}
        
        if face_count > 1:
            violations.append("multiple_people")
        
        face_landmarks = landmarks[0]
        
        gaze, h_ratio, v_ratio = self.calculate_gaze_direction(face_landmarks, frame.shape)
        
        if gaze == "down":
            violations.append("looking_down")
        elif gaze in ["left", "right"]:
            violations.append("looking_away")
        
        try:
            pitch, yaw, roll = self.calculate_head_pose(face_landmarks, frame.shape)
            
            if pitch < -25:
                if "looking_down" not in violations:
                    violations.append("head_tilted_down")
        except:
            pitch, yaw, roll = 0, 0, 0
        
        return violations, {
            "face_count": face_count,
            "gaze": gaze,
            "head_pose": {"pitch": pitch, "yaw": yaw, "roll": roll}
        }
    
    def cleanup(self):
        self.face_mesh.close()
