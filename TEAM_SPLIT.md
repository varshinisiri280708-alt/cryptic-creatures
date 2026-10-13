# Cryptic Escape — Team Split (4 members)

The original single 1,981-line `cryptic\\\\\\\_escape.py` is now 4 parts. Each member owns and pushes ONE part.
Run the game with `python main.py` (needs all 4 parts present).

|Member|Part|Files (push these)|What it contains|Lines|
|-|-|-|-|-|
|1|**Core \& Data**|`core.py`, `assets/`, `requirements.txt`,|Config, fonts, textures, 3 level maps + Caesar ciphers, themes, quests, **all shared game state**, procedural sound, save/load, text/panel/button helpers|\~420|
|2|**Rendering \& Visuals**|`rendering.py`,`settings.json`, `.gitignore`|Seasonal effects, wall paintings, menu background, lantern flash, monster \& spirit drawing, minimap, ray-casting `draw\\\\\\\_world`, 3D title menu|\~540|
|3|**Screens, Dialogue \& Puzzles**|`screens.py`|Journal, Witness dialogue, interact, cipher puzzle, settings, customize, overlays, instructions, hub/story/theme/quest galleries, mini-games|\~565|
|4|**Game Loop \& Entry**|`game.py`, `main.py`, `README.md`, `TEAM\\\\\\\_SPLIT.md`|`main()` loop: input, movement, enemy AI, stamina, heartbeat, state switching, crash log|\~490|

## Dependency order (no circular imports)

`core.py` <- `rendering.py` <- `screens.py` <- `game.py` <- `main.py`

## Shared state rule

Variables that change while playing (health, mode, player\_x, level\_index, settings, ...) live in `core.py`.
Other files access them as `core.health`, `core.mode`, etc. Never write `health = ...` in another file; write `core.health = ...`.

## Git steps (each member)

```bash
# Member 1 (once): create repo, push first
git init \\\\\\\&\\\\\\\& git add core.py assets requirements.txt settings.json .gitignore
git commit -m "Add core module and assets" \\\\\\\&\\\\\\\& git branch -M main
git remote add origin <REPO\\\\\\\_URL> \\\\\\\&\\\\\\\& git push -u origin main

# Members 2, 3, 4 (after Member 1 pushed)
git clone <REPO\\\\\\\_URL> \\\\\\\&\\\\\\\& cd <repo>
git checkout -b part-<N>-<name>
git add <your files>
git commit -m "Add <your part>"
git push -u origin part-<N>-<name>      # then open a Pull Request, merge into main
```

Since every member touches different files, there are no merge conflicts.

## Run

```bash
pip install -r requirements.txt
python main.py
```

