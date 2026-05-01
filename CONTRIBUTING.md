# Contributing to MedWave

Thanks for your interest in improving MedWave.

## Development Setup

1. Create a virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run the app:
   - `python main.py`

## Pull Request Guidelines

- Keep changes focused and small.
- Update `README.md` when behavior changes (especially gesture or voice mappings).
- Preserve privacy defaults:
  - never commit face enrollment data
  - never commit local auth models or uploaded patient documents
- Test basic flows before opening a PR:
  - camera starts
  - gesture actions trigger expected PDF controls
  - voice commands parse and execute

## Coding Notes

- Keep command names consistent across gesture, safety, voice, and UI handlers.
- Prefer explicit user feedback for state transitions (ready, listening, error, holding).
- Avoid silent failures where possible; surface user-friendly status text.
