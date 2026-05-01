import cv2
import mediapipe as mp
import time
from PySide6.QtCore import QThread, Signal

BaseOptions = mp.tasks.BaseOptions
vision = mp.tasks.vision
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
RunningMode = vision.RunningMode


class CameraWorker(QThread):
    raw_frame_signal = Signal(object)    # raw frame (BGR) for face auth/signup
    frame_signal = Signal(object)        # annotated frame for UI preview
    landmarks_signal = Signal(object)    # dict payload for gesture engine

    def __init__(
        self,
        cam_index=0,
        model_path="models/hand_landmarker.task",
        detect_fps=12,
        preview_fps=30,
        mirror=True
    ):
        super().__init__()
        self.cam_index = cam_index
        self.model_path = model_path
        self.mirror = mirror

        self._running = True

        # detection throttle
        self.detect_interval = 1.0 / float(max(1, detect_fps))
        self._last_detect_time = 0.0

        # preview throttle (optional)
        self.preview_interval = 1.0 / float(max(1, preview_fps))
        self._last_preview_time = 0.0

        # last payload for drawing
        self._last_payload = {"hands": [], "frame_size": (0, 0)}

        # timestamp baseline for VIDEO mode
        self._t0 = time.time()

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        if not cap.isOpened():
            print("❌ Camera not found. Try cam_index=1")
            return

        try:
            while self._running:
                ok, frame = cap.read()
                if not ok:
                    continue

                # mirror makes gestures feel natural (like a selfie camera)
                if self.mirror:
                    frame = cv2.flip(frame, 1)

                # raw frame for auth/signup
                self.raw_frame_signal.emit(frame)

                now = time.time()

                # Detect landmarks at throttled fps
                if (now - self._last_detect_time) >= self.detect_interval:
                    self._last_detect_time = now

                    # IMPORTANT: stop cleanly if requested
                    if not self._running:
                        break

                    payload = self._detect(frame)
                    self._last_payload = payload
                    self.landmarks_signal.emit(payload)

                # Draw last known landmarks for UI preview (also throttled)
                if (now - self._last_preview_time) >= self.preview_interval:
                    self._last_preview_time = now
                    annotated = self._draw_landmarks(frame.copy(), self._last_payload)
                    self.frame_signal.emit(annotated)

                # tiny sleep prevents maxing CPU
                time.sleep(0.001)

        except Exception as e:
            print("CameraWorker crashed:", e)

        finally:
            try:
                cap.release()
            except Exception:
                pass

            try:
                self.landmarker.close()
            except Exception:
                pass

    def _detect(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape

        # VIDEO mode requires increasing timestamps (use real elapsed time)
        ts_ms = int((time.time() - self._t0) * 1000)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.landmarker.detect_for_video(mp_image, ts_ms)

        payload = {"hands": [], "frame_size": (w, h)}

        if result.hand_landmarks:
            for hand_lms in result.hand_landmarks:
                pts = [(lm.x, lm.y, lm.z) for lm in hand_lms]
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                payload["hands"].append({
                    "landmarks": pts,
                    "bbox": (min(xs), min(ys), max(xs), max(ys))
                })

        return payload

    def _draw_landmarks(self, frame_bgr, payload):
        w = payload.get("frame_size", (0, 0))[0]
        h = payload.get("frame_size", (0, 0))[1]
        if w == 0 or h == 0:
            h, w = frame_bgr.shape[:2]

        for hand in payload.get("hands", []):
            for (x, y, _z) in hand["landmarks"]:
                px = int(x * w)
                py = int(y * h)
                cv2.circle(frame_bgr, (px, py), 3, (0, 255, 0), -1)

        return frame_bgr

    def stop(self):
        self._running = False
