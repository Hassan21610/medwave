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
            "scroll", "up", "down"
        ]

    def run(self):
        try:
            model = Model(self.model_path)
        except Exception as e:
            self.partial_signal.emit("Voice disabled")
            print("Voice disabled:", e)
            return

        rec = KaldiRecognizer(model, self.sample_rate, json.dumps(self.grammar))
        q = queue.Queue()

        def callback(indata, frames, time_info, status):
            q.put(bytes(indata))

        self.active_signal.emit(False)

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=callback
            ):
                while self._running:
                    data = q.get()
                    if not data:
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
            print("Voice error:", e)
        finally:
            self.active_signal.emit(False)

    def _parse_command(self, text: str):
        # Require wake word at the start
        if not text.startswith("hey health"):
            return None

        # Normalize: remove the wake word prefix
        tail = text.replace("hey health", "", 1).strip()

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

        # Scroll
        if "scroll down" in tail:
            return "SCROLL_DOWN"
        if "scroll up" in tail:
            return "SCROLL_UP"

        return None

    def stop(self):
        self._running = False
