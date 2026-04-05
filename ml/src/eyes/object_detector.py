"""YOLOv8-nano object detector for proctoring — detects phones, books, earpieces, and secondary screens."""
import logging
from pathlib import Path
from typing import Optional

import numpy as np

from config import settings

logger = logging.getLogger("ObjectDetector")

# Classes we care about from COCO (YOLOv8 default dataset)
PROCTORING_CLASSES = {
    67: "cell phone",
    73: "book",
    63: "laptop",
    65: "remote",
    26: "handbag",
}

# Classes that specifically indicate earpiece / audio cheating
EARPIECE_INDICATOR_CLASSES = {
    67: "cell phone",  # phone near ear
}


class ObjectDetector:
    """Lightweight YOLOv8-nano wrapper for proctoring object detection.

    Auto-downloads the model on first use (~6MB).
    Filters detections to only proctoring-relevant object classes.
    """

    def __init__(self) -> None:
        self._model = None
        self._available = False
        self._load_model()

    def _load_model(self) -> None:
        """Load YOLOv8-nano, downloading if necessary."""
        try:
            from ultralytics import YOLO

            model_path = settings.YOLO_MODEL_PATH

            if model_path.exists():
                self._model = YOLO(str(model_path))
                logger.info(f"Loaded YOLO model from {model_path}")
            else:
                # Auto-download the nano model
                model_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info("Downloading YOLOv8-nano model (~6MB)...")
                self._model = YOLO("yolov8n.pt")
                # Save to our models dir for future runs
                import shutil
                src = Path("yolov8n.pt")
                if src.exists():
                    shutil.move(str(src), str(model_path))
                    logger.info(f"Model saved to {model_path}")

            self._available = True
        except ImportError:
            logger.warning("ultralytics not installed — object detection disabled. pip install ultralytics")
            self._available = False
        except Exception as e:
            logger.error(f"YOLO model load failed: {e}")
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    def detect(self, frame: np.ndarray) -> list[dict]:
        """Run detection on a single frame.

        Returns:
            List of dicts with: class_name, class_id, confidence, bbox (x1,y1,x2,y2)
        """
        if not self._available or self._model is None:
            return []

        try:
            results = self._model(
                frame,
                conf=settings.YOLO_CONFIDENCE_THRESHOLD,
                verbose=False,
                stream=False,
            )

            detections = []
            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    class_id = int(box.cls[0])
                    if class_id not in PROCTORING_CLASSES:
                        continue

                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    detections.append({
                        "class_id": class_id,
                        "class_name": PROCTORING_CLASSES[class_id],
                        "confidence": round(conf, 3),
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    })

            return detections

        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return []

    def detect_phone_near_ear(self, detections: list[dict], face_bbox: Optional[tuple] = None) -> bool:
        """Check if a phone detection overlaps with the ear region of the face.

        Args:
            detections: Output from self.detect()
            face_bbox: Optional (x1, y1, x2, y2) of the detected face.

        Returns:
            True if a phone is likely near the candidate's ear.
        """
        phone_detections = [d for d in detections if d["class_name"] == "cell phone"]
        if not phone_detections:
            return False

        if face_bbox is None:
            # Without face bbox, any phone detection is suspicious
            return bool(phone_detections)

        fx1, fy1, fx2, fy2 = face_bbox
        face_width = fx2 - fx1
        face_height = fy2 - fy1

        for phone in phone_detections:
            px1, py1, px2, py2 = phone["bbox"]
            # Check if phone overlaps with the ear regions (left/right 30% of face)
            ear_left_region = (fx1 - face_width * 0.3, fy1, fx1 + face_width * 0.3, fy2)
            ear_right_region = (fx2 - face_width * 0.3, fy1, fx2 + face_width * 0.3, fy2)

            if self._boxes_overlap(phone["bbox"], ear_left_region) or \
               self._boxes_overlap(phone["bbox"], ear_right_region):
                return True

        return False

    @staticmethod
    def _boxes_overlap(box_a, box_b) -> bool:
        """Check if two bounding boxes overlap."""
        ax1, ay1, ax2, ay2 = box_a
        bx1, by1, bx2, by2 = box_b
        return not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2)
""" Description="Created isolated YOLOv8-nano wrapper with phone-near-ear detection, COCO class filtering, and auto-download." IsArtifact=false Overwrite=false """
