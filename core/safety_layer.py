import time
from dataclasses import dataclass
from core.gesture_engine import AppMode

# Keep risky set empty for smoother direct gesture UX.
# Voice-confirm flow remains available for future high-risk commands.
RISKY = set()

@dataclass
class SafetyDecision:
    state: str
    reason: str = ""
    progress_pct: int = 0
    voice_phrase: str = ""

class SafetyLayer:
    def __init__(self, mode=AppMode.SURGICAL):
        self.set_mode(mode)

    def set_mode(self, mode):
        self.mode = mode
        self.hold_seconds = 2.0 if mode == AppMode.SURGICAL else 1.0
        self._hold_start = None
        self._pending = None
        self._await_voice_phrase = None
        self._last_gesture = None
        self._repeat_count = 0
        self._repeat_needed = 2 if mode == AppMode.SURGICAL else 1

    def evaluate(self, gesture: str) -> SafetyDecision:
        if gesture == self._last_gesture:
            self._repeat_count += 1
        else:
            self._last_gesture = gesture
            self._repeat_count = 1

        if self._repeat_count < self._repeat_needed:
            return SafetyDecision(state="REJECTED", reason="accidental-rejection")

        if gesture in RISKY:
            if self.mode == AppMode.SURGICAL:
                if self._pending != gesture:
                    self._pending = gesture
                    self._hold_start = time.time()
                    return SafetyDecision(state="HOLDING", progress_pct=0)

                elapsed = time.time() - self._hold_start
                pct = int(min(100, (elapsed / self.hold_seconds) * 100))
                if elapsed < self.hold_seconds:
                    return SafetyDecision(state="HOLDING", progress_pct=pct)

                self._await_voice_phrase = "zoom"
                return SafetyDecision(state="NEEDS_VOICE_CONFIRM", voice_phrase="zoom")

            if self._pending != gesture:
                self._pending = gesture
                self._hold_start = time.time()
                return SafetyDecision(state="HOLDING", progress_pct=0)

            elapsed = time.time() - self._hold_start
            pct = int(min(100, (elapsed / self.hold_seconds) * 100))
            if elapsed < self.hold_seconds:
                return SafetyDecision(state="HOLDING", progress_pct=pct)

        self._pending = None
        self._hold_start = None
        self._await_voice_phrase = None
        return SafetyDecision(state="APPROVED")

    def accept_voice(self, cmd: str):
        if not self._await_voice_phrase:
            return None

        cmd = cmd.lower().strip()
        is_confirm = (
            cmd == "confirm_zoom"
            or (cmd.startswith("confirm") and self._await_voice_phrase in cmd)
        )
        if is_confirm and self._pending:
            approved_gesture = self._pending
            self._await_voice_phrase = None
            self._pending = None
            self._hold_start = None
            return approved_gesture
        return None
