# Cryptic Escape: The Cursed Manor

A Pygame (split into core, rendering, screens and game modules) gothic-horror puzzle adventure. The upgrade preserves the original ray-cast mansion, three chapters, The Hollow, the Witness, Caesar seals, flower-memory puzzle, settings, and procedural vector artwork/audio.

## Run locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

macOS/Linux:
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Controls

- **W / A / S / D**: move
- **Mouse**: look around
- **Arrow keys**: turn
- **E**: interact with the Witness, cyan seal, or Moon Door
- **F**: open the flower-memory puzzle
- **J**: open the journal
- **1–3**: choose a dialogue option
- **Enter / Space / click**: finish or advance dialogue text
- **Esc**: pause / return from a sub-screen

## Improvements in this version

- Cleaned Markdown-escaped characters so the Python source is executable.
- Added settings validation to avoid crashes from malformed settings JSON.
- Made saved clue data defensive against malformed values.
- Save files now retain the solved flower-memory state.
- Dialogue lines reveal with a typewriter effect; input first finishes the current line before advancing.
- Added an in-game journal showing decoded seals, flower-memory status, and the current objective.
- Added two reachable ending variants: restoring the Witness's flower memory unlocks the more complete ending.
- Preserved the original Pygame rendering approach and avoided external art dependencies.

## Test status

- Python syntax compilation: **passed**.
- Caesar cipher round-trip checks for all three seals: **passed**.
- Grid reachability checks for each chapter's exit, clue, friend, and enemy positions: **passed**.
- Full interactive runtime test: **not run in this environment** because Pygame is not installed and package download access is unavailable. Install dependencies on your computer before launching the game.

Save and settings files (`savegame.json` and `settings.json`) are created beside the game when it runs.
