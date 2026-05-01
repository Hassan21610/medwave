# MedWave

MedWave is a computer vision based, touchless interaction system for sterile clinical environments. It lets medical professionals control digital systems with hand gestures instead of physical input devices, helping reduce contact with keyboards, mice, and screens during procedures.

The app uses a camera to detect hand landmarks in real time, maps predefined gestures to actions such as scrolling, zooming, and page navigation, and provides a medical PDF viewing workflow for patient reports and imaging documents.

## Why It Matters

In surgical and sterile clinical settings, touching shared input devices can break sterility and increase infection risk. MedWave demonstrates how AI powered human-computer interaction can help clinicians navigate digital content directly, reduce dependency on assistants, and modernise hospital workflows.

## Features

- Real-time hand landmark detection with MediaPipe
- Gesture based PDF navigation, scrolling, and zoom controls
- Touchless workflow designed for medical imaging and reports
- Face based user authentication with OpenCV
- Optional offline voice commands using Vosk
- PySide6 desktop interface with camera preview and safety status

## Tech Stack

- Python
- OpenCV
- MediaPipe
- PyAutoGUI
- PySide6
- PyMuPDF
- Vosk and SoundDevice for optional voice control

## Project Structure

```text
core/      Gesture, camera, safety, voice, auth, and action logic
ui/        PySide6 windows, widgets, theme, and PDF viewer
models/    MediaPipe hand landmark model
assets/    Optional local assets such as the Vosk speech model
main.py    Application entry point
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For voice commands, download the Vosk small English model and extract it to:

```text
assets/vosk-model-small-en-us-0.15/
```

The application will still run without the Vosk model, but voice control will be disabled.

## Run

```bash
python main.py
```

## Notes

Local biometric and runtime data are intentionally excluded from Git:

- `auth_faces/`
- `auth_model.yml`
- `auth_labels.json`
- `uploads/`

This keeps the public repository safe while allowing each installation to enroll users and upload clinical documents locally.

