import cv2
import threading
import time
import logging
from src.eyes.proctoring_engine import ProctoringEngine
from config import settings

logger = logging.getLogger("ProctoringMonitor")

class ProctoringMonitor:
    def __init__(self):
        self.engine = ProctoringEngine()
        self.is_running = False
        self.thread = None
        self.cap = None
        
        self.violation_log = []
        self.violation_counters = {
            "user_left": 0,
            "multiple_people": 0,
            "looking_away": 0,
            "looking_down": 0,
            "head_tilted_down": 0
        }
        
        self.continuous_violation_tracker = {}
        self.threshold_seconds = settings.VIOLATION_THRESHOLD_SECONDS
    
    def start(self):
        if self.is_running:
            return
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Failed to open webcam")
                return
            
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info("Proctoring monitor started")
        except Exception as e:
            logger.error(f"Failed to start proctoring: {e}")
    
    def _monitor_loop(self):
        fps = settings.PROCTORING_FPS
        frame_interval = 1.0 / fps
        
        cv2.namedWindow("BeaverAI Proctoring", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("BeaverAI Proctoring", 640, 480)
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(frame_interval)
                    continue
                
                violations, metadata = self.engine.analyze_frame(frame)
                
                display_frame = frame.copy()
                
                if metadata and 'gaze' in metadata:
                    gaze_text = f"Gaze: {metadata['gaze']}"
                    cv2.putText(display_frame, gaze_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if metadata.get('face_count', 0) > 0:
                        cv2.putText(display_frame, f"Faces: {metadata['face_count']}", 
                                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if violations:
                    y_offset = 90
                    for violation in violations:
                        warning_text = violation.replace("_", " ").upper()
                        cv2.putText(display_frame, f"WARNING: {warning_text}", 
                                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, (0, 0, 255), 2)
                        y_offset += 30
                
                cv2.imshow("BeaverAI Proctoring", display_frame)
                cv2.waitKey(1)
                
                current_time = time.time()
                
               
                for violation_type in violations:
                    
                    if violation_type not in self.continuous_violation_tracker:
                       
                        self._log_violation(violation_type, 0, is_sustained=False)
                        self.continuous_violation_tracker[violation_type] = current_time
                    else:
                        
                        duration = current_time - self.continuous_violation_tracker[violation_type]
                        
                        if duration >= self.threshold_seconds:
                            
                            self._log_violation(violation_type, duration, is_sustained=True)
                            self.continuous_violation_tracker[violation_type] = current_time
                
                
                active_violations = set(violations)
                for vtype in list(self.continuous_violation_tracker.keys()):
                    if vtype not in active_violations:
                        del self.continuous_violation_tracker[vtype]
                
                time.sleep(frame_interval)
                
            except Exception as e:
                logger.error(f"Proctoring loop error: {e}")
                time.sleep(frame_interval)
        
        cv2.destroyAllWindows()
    
    def _log_violation(self, violation_type, duration, is_sustained=False):
        self.violation_counters[violation_type] += 1
        
        log_entry = {
            "type": violation_type,
            "timestamp": time.time(),
            "duration": round(duration, 2),
            "sustained": is_sustained
        }
        self.violation_log.append(log_entry)
        
        if is_sustained:
            logger.warning(f"Sustained violation: {violation_type} for {duration:.1f}s")
        else:
            logger.info(f"Violation detected: {violation_type}")
    
    def get_violations_summary(self):
        total_violations = sum(self.violation_counters.values())
        
        severity = "low"
        if total_violations > 10:
            severity = "high"
        elif total_violations > 5:
            severity = "medium"
        
        return {
            "total_violations": total_violations,
            "violation_counts": self.violation_counters.copy(),
            "violation_log": self.violation_log.copy(),
            "severity": severity
        }
    
    def stop(self):
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        
        try:
            self.engine.cleanup()
        except:
            pass
        
        logger.info("Proctoring monitor stopped")
