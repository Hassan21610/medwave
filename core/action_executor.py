import pyautogui
from core.gesture_engine import AppMode

class ActionExecutor:
    def execute_gesture(self, gesture: str, mode: AppMode):
        if gesture in ("SWIPE_RIGHT", "NEXT_PAGE"):
            pyautogui.press("right")
        elif gesture in ("SWIPE_LEFT", "PREV_PAGE"):
            pyautogui.press("left")
        elif gesture == "SCROLL_DOWN":
            pyautogui.scroll(-250)
        elif gesture == "SCROLL_UP":
            pyautogui.scroll(250)
        elif gesture == "ZOOM_IN":
            pyautogui.hotkey("ctrl", "+")
        elif gesture == "ZOOM_OUT":
            pyautogui.hotkey("ctrl", "-")
        elif gesture == "RESET_ZOOM":
            pyautogui.hotkey("ctrl", "0")

    def execute_voice(self, cmd: str):
        cmd = cmd.lower()
        if "open" in cmd and "pdf" in cmd:
            pyautogui.hotkey("ctrl", "o")
