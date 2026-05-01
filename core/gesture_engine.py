import time
from enum import Enum


class AppMode(Enum):
    SURGICAL = "surgical"
    WARD = "ward"


class GestureEngine:
    def __init__(self, mode=AppMode.SURGICAL):
        self.mode = mode
        self.cooldown = 0.7 if mode == AppMode.SURGICAL else 0.4
        self._last_emit = 0

    def set_mode(self, mode):
        self.mode = mode
        self.cooldown = 0.7 if mode == AppMode.SURGICAL else 0.4

    def _cooldown_ok(self):
        return (time.time() - self._last_emit) >= self.cooldown

    def _emit(self, g):
        self._last_emit = time.time()
        return g

    def detect(self, lm_data):
        if not lm_data.get("hands"):
            return None

        hand = lm_data["hands"][0]
        pts = hand["landmarks"]

        # Landmark indices
        index_tip = pts[8]
        middle_tip = pts[12]
        ring_tip = pts[16]
        pinky_tip = pts[20]

        index_pip = pts[6]
        middle_pip = pts[10]
        ring_pip = pts[14]
        pinky_pip = pts[18]

        # Finger extended detection
        def extended(tip, pip):
            return tip[1] < pip[1] - 0.02

        index_ext = extended(index_tip, index_pip)
        middle_ext = extended(middle_tip, middle_pip)
        ring_ext = extended(ring_tip, ring_pip)
        pinky_ext = extended(pinky_tip, pinky_pip)

        ext_count = sum([index_ext, middle_ext, ring_ext, pinky_ext])

        if not self._cooldown_ok():
            return None

        # ✋ Open palm → Scroll down
        if ext_count >= 4:
            return self._emit("SCROLL_DOWN")

        # ✊ Fist → Scroll up
        if ext_count == 0:
            return self._emit("SCROLL_UP")

        # ☝ One finger → Zoom in
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return self._emit("ZOOM_IN")

        # ✌ Two fingers → Zoom out
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return self._emit("ZOOM_OUT")

        return None
