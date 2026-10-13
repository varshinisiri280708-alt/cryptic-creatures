# Cryptic Escape: The Cursed Manor

A Pygame gothic-horror puzzle adventure built with a modular Python structure, split into core, rendering, screens, and game modules.

The game preserves the original ray-cast mansion, three chapters, The Hollow, the Witness, Caesar seals, flower-memory puzzle, settings, and procedural vector artwork. Sound assets have also been added to enhance the horror atmosphere.

## Run Locally

Use Python 3.10 or newer.

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

### macOS/Linux

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Controls

- **W / A / S / D**: Move
- **Mouse**: Look around
- **Arrow keys**: Turn
- **E**: Interact with the Witness, cyan seal, or Moon Door
- **F**: Open the flower-memory puzzle
- **J**: Open the journal
- **1–3**: Choose a dialogue option
- **Enter / Space / Click**: Finish or advance dialogue text
- **Esc**: Pause or return from a sub-screen

## Sound Assets

The project includes a sound-assets folder at `assets/sounds/`.

- `background.mp3` — Background music
- `footsteps.mp3` — Player movement sound
- `opening.mp3` — Opening sound
- `celebration.mp3` — Victory sound
- `lost.mp3` — Failure sound

Only include the sound files that are present in the repository. Sound effects must be loaded and connected to the corresponding game events in the code to play during gameplay.

## Improvements in This Version

- Cleaned Markdown-escaped characters so the Python source is executable.
- Added settings validation to avoid crashes from malformed settings JSON.
- Made saved clue data defensive against malformed values.
- Save files retain the solved flower-memory state.
- Dialogue lines reveal with a typewriter effect; input first finishes the current line before advancing.
- Added an in-game journal showing decoded seals, flower-memory status, and the current objective.
- Added two reachable ending variants: restoring the Witness's flower memory unlocks the more complete ending.
- Preserved the original Pygame rendering approach and avoided external art dependencies.
- Added external MP3 sound assets for background music and gameplay sound effects.

## Test Status

- Python syntax compilation: **Passed**
- Caesar cipher round-trip checks for all three seals: **Passed**
- Grid reachability checks for each chapter's exit, clue, friend, and enemy positions: **Passed**
- Full interactive runtime test: **Not run in the original test environment** because Pygame was not installed and package download access was unavailable.

Install the dependencies on your computer and run the game locally to verify gameplay and audio.

## Save Files and Settings

The game creates `savegame.json` and `settings.json` beside the game when it runs.
