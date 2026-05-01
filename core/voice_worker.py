import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from PySide6.QtCore import QThread, Signal


class VoiceWorker(QThread):
    partial_signal = Signal(str)
    command_signal = Signal(str)
    active_signal = Signal(bool)

    def __init__(self, model_path: str, sample_rate=16000):
        super().__init__()
        self.model_path = model_path
        self.sample_rate = sample_rate
        self._running = True

        # Wake word + command vocabulary
        self.grammar = [
            "hey", "health",
            "zoom", "in", "out", "reset",
            "next", "previous", "prev", "page",
            "open", "pdf",
            "scroll", "up", "down", "left", "right",
            "confirm"
        ]

    def _resolve_sample_rate(self) -> int:
        """
        Prefer requested rate, but fall back to the default input device rate
        when needed to avoid stream startup failures on some systems.
        """
        try:
            dev_info = sd.query_devices(kind="input")
            default_sr = int(dev_info.get("default_samplerate") or self.sample_rate)
            if default_sr > 0:
                return default_sr
        except Exception:
            pass
        return int(self.sample_rate)

    def run(self):
        try:
            model = Model(self.model_path)
        except Exception as e:
            self.partial_signal.emit("Voice disabled")
            print("Voice disabled:", e)
            return

        input_rate = self._resolve_sample_rate()
        rec = KaldiRecognizer(model, input_rate, json.dumps(self.grammar))
        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            if status:
                # Surface device issues in the UI indicator for easier troubleshooting.
                self.partial_signal.emit(f"Mic status: {status}")
            q.put(bytes(indata))

        self.partial_signal.emit(f"Voice ready ({input_rate} Hz)")
        self.active_signal.emit(False)

        try:
            with sd.RawInputStream(
                samplerate=input_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=callback
            ):
                while self._running:
                    try:
                        data = q.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    if not data or not self._running:
                        continue

                    self.active_signal.emit(True)

                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = (result.get("text") or "").strip().lower()
                        if text:
                            self.partial_signal.emit(text)
                            cmd = self._parse_command(text)
                            if cmd:
                                self.command_signal.emit(cmd)
                    else:
                        partial = json.loads(rec.PartialResult()).get("partial", "").strip().lower()
                        if partial:
                            self.partial_signal.emit(partial)

        except Exception as e:
            self.partial_signal.emit("Voice runtime error")
            print("Voice error:", e)
        finally:
            self.active_signal.emit(False)

    def _parse_command(self, text: str):
        normalized = " ".join(text.lower().strip().split())
        if not normalized:
            return None

        # Allow minor recognition variation while still requiring wake intent.
        has_wake = any(
            wake in normalized
            for wake in ("hey health", "hey healthy", "a health", "hay health")
        )
        if not has_wake:
            return None

        # Remove known wake prefixes if present.
        tail = normalized
        for wake in ("hey health", "hey healthy", "a health", "hay health"):
            if tail.startswith(wake):
                tail = tail.replace(wake, "", 1).strip()
                break

        # PDF actions
        if "open pdf" in tail:
            return "OPEN_PDF"
        if "next page" in tail:
            return "NEXT_PAGE"
        if "previous page" in tail or "prev page" in tail:
            return "PREV_PAGE"

        # Zoom
        if "zoom in" in tail:
            return "ZOOM_IN"
        if "zoom out" in tail:
            return "ZOOM_OUT"
        if "reset zoom" in tail:
            return "RESET_ZOOM"
        if "confirm zoom" in tail:
            return "CONFIRM_ZOOM"

        # Scroll
        if "scroll down" in tail:
            return "SCROLL_DOWN"
        if "scroll up" in tail:
            return "SCROLL_UP"
        if "scroll left" in tail:
            return "SCROLL_LEFT"
        if "scroll right" in tail:
            return "SCROLL_RIGHT"

        return None

    def stop(self):
        self._running = False
