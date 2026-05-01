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
        self._last_x = None
        self._last_t = None

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
            self._last_x = None
            self._last_t = None
            return None

        hand = lm_data["hands"][0]
        pts = hand["landmarks"]

        # Landmark indices
        index_tip = pts[8]
        middle_tip = pts[12]
        ring_tip = pts[16]
        pinky_tip = pts[20]
        thumb_tip = pts[4]

        index_pip = pts[6]
        middle_pip = pts[10]
        ring_pip = pts[14]
        pinky_pip = pts[18]
        thumb_ip = pts[3]
        thumb_mcp = pts[2]

        # Finger extended detection
        def extended(tip, pip):
            return tip[1] < pip[1] - 0.02

        index_ext = extended(index_tip, index_pip)
        middle_ext = extended(middle_tip, middle_pip)
        ring_ext = extended(ring_tip, ring_pip)
        pinky_ext = extended(pinky_tip, pinky_pip)
        thumb_ext = (
            abs(thumb_tip[0] - thumb_mcp[0]) > 0.09
            and thumb_tip[1] < thumb_ip[1] + 0.03
        )

        ext_count = sum([index_ext, middle_ext, ring_ext, pinky_ext])
        total_count = ext_count + (1 if thumb_ext else 0)
        now = time.time()

        if not self._cooldown_ok():
            self._last_x = index_tip[0]
            self._last_t = now
            return None

        # Practical page navigation gestures:
        # - 3 fingers (index+middle+ring) => next page
        # - 4 fingers (index+middle+ring+pinky) => previous page
        if index_ext and middle_ext and ring_ext and not pinky_ext:
            self._last_x = index_tip[0]
            self._last_t = now
            return self._emit("SWIPE_RIGHT")
        if index_ext and middle_ext and ring_ext and pinky_ext:
            self._last_x = index_tip[0]
            self._last_t = now
            return self._emit("SWIPE_LEFT")

        self._last_x = index_tip[0]
        self._last_t = now

        # ✋ Full open palm (with thumb) -> Scroll down
        if total_count >= 5:
            return self._emit("SCROLL_DOWN")

        # ✊ Fist → Scroll up
        if total_count == 0:
            return self._emit("SCROLL_UP")

        # ☝ One finger → Zoom in
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return self._emit("ZOOM_IN")

        # ✌ Two fingers → Zoom out
        if index_ext and middle_ext and not ring_ext and not pinky_ext:
            return self._emit("ZOOM_OUT")

        return None
