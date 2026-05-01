import pyautogui
from core.gesture_engine import AppMode

class ActionExecutor:
    def execute_gesture(self, gesture: str, mode: AppMode):
        if gesture == "SWIPE_RIGHT":
            pyautogui.press("right")
        elif gesture == "SWIPE_LEFT":
            pyautogui.press("left")
        elif gesture == "OPEN_PALM_SCROLL":
            pyautogui.scroll(-250)
        elif gesture == "FIST_ZOOM":
            pyautogui.hotkey("ctrl", "+")
        elif gesture == "TWO_FINGERS_SELECT":
            pyautogui.click()

    def execute_voice(self, cmd: str):
        cmd = cmd.lower()
        if "open" in cmd and "ct" in cmd:
            pyautogui.hotkey("ctrl", "o")
