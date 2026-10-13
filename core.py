"""PART 1 - Core: config, game data, shared state, audio, save/load, UI helpers.

All shared game state (health, mode, player_x, ...) lives HERE. Other modules read and
write it as `core.<name>` so every file sees the same values.
"""
import math
import json
import os
import random
import sys
from array import array

import pygame

# ==============================================================================
# Cryptic Escape: The Cursed Manor — Deluxe Edition
# Pure Pygame; zero external assets required.
# ------------------------------------------------------------------------------
# Features:
# - Pseudo-3D Raycasting Engine with Distance Shading & Torch Flicker
# - Dynamic 1D Depth Buffer (prevents sprites from clipping through walls)
# - Real-time HUD Minimap / Radar (Toggleable with 'M')
# - Sprint & Stamina Mechanics (Hold 'SHIFT') with Head-Bobbing & Footstep SFX
# - Lantern Flash Stun Defense ('SPACE' or Right Click) to blind The Hollow
# - In-Game Journal & Caesar Cipher Codex ('J') with built-in decoder wheel
# - Tension Heartbeat System (procedural audio accelerates as the monster nears)
# - Branching Dialogue with The Witness
# - Caesar Cipher Puzzle Mechanics
# - Character Customization Atelier & Settings Menu (Story/Normal/Nightmare)
# - Full Persistence (savegame.json & settings.json)
# ==============================================================================

pygame.init()
pygame.display.set_caption("Cryptic Escape: The Cursed Manor — Deluxe Edition")
WIDTH, HEIGHT = 1100, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
SAVE_FILE = os.path.join(BASE_DIR, "savegame.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

FONT = pygame.font.SysFont("georgia", 22)
SMALL = pygame.font.SysFont("georgia", 16)
TINY = pygame.font.SysFont("georgia", 13)
TITLE = pygame.font.SysFont("georgia", 42, bold=True)
BIG = pygame.font.SysFont("georgia", 54, bold=True)

DEFAULT_SETTINGS = {
    "master_volume": 0.65,
    "music_volume": 0.35,
    "sfx_volume": 0.8,
    "sensitivity": 0.0022,
    "dark_mode": True,
    "character_color": 2,
    "character_type": 0,
    "difficulty": "Normal",
    "minimap": True,
    "head_bob": True
}

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {**default, **data}
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return default.copy()

settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)

# External room artwork. Images are mapped onto the ray-cast wall surfaces,
# so they follow the game's pseudo-3D perspective instead of being flat overlays.
ASSET_DIR = os.path.join(BASE_DIR, "assets")
def load_room_texture(filename, fallback_color):
    path = os.path.join(ASSET_DIR, filename)
    try:
        image = pygame.image.load(path).convert()
        return pygame.transform.smoothscale(image, (512, 256))
    except (pygame.error, OSError):
        fallback = pygame.Surface((512, 256))
        fallback.fill(fallback_color)
        return fallback

ROOM_TEXTURES = [
    load_room_texture("livingroom.png", (65, 35, 40)),
    load_room_texture("painting.png", (35, 55, 48)),
    load_room_texture("passage.png", (25, 30, 42)),
]

def load_surface_texture(filename, fallback_size, fallback_color):
    """Load a high-detail texture from assets/ or beside the game file."""
    for path in (os.path.join(ASSET_DIR, filename), os.path.join(BASE_DIR, filename)):
        try:
            return pygame.image.load(path).convert()
        except (pygame.error, OSError):
            continue
    surface = pygame.Surface(fallback_size)
    surface.fill(fallback_color)
    return surface

# User-provided octagonal ceiling and geometric wooden floor.
CEILING_TEXTURE = load_surface_texture("ceiling.png", (512, 512), (24, 12, 24))
FLOOR_TEXTURE = load_surface_texture("floor.png", (512, 512), (55, 35, 24))
EXTRA_ROOM_TEXTURES = [
    load_room_texture("drawingroom.png", (25, 40, 38)),
    load_room_texture("room.png", (35, 35, 42)),
]
ROOM_TEXTURES.extend(EXTRA_ROOM_TEXTURES)
DINING_TEXTURE = load_room_texture("candle.png", (45, 30, 25))
save_data = load_json(SAVE_FILE, {"level": 0, "health": 100, "clues": [], "won": False})

LEVELS = [
    {
        "name": "The Forgotten Foyer",
        "map": [
            "111111111111",
            "100000000001",
            "101110011101",
            "100010000001",
            "100010111101",
            "100000100001",
            "101100100101",
            "100000000001",
            "111111111111"
        ],
        "start": (1.5, 1.5), "exit": (10.5, 7.5), "clue": (5.5, 3.5),
        "answer": "THE KEY IS UNDER THE CANDLE",
        "hint": "Caesar shift: move each letter 2 steps backward.",
        "enemy": (8.5, 5.5), "friend": (3.5, 5.5),
        "intro": "A portrait follows your gaze. Beneath it, fresh dust spells your name. Somewhere upstairs, a dinner bell rings for a family that died a century ago."
    },
    {
        "name": "The Whispering Library",
        "map": [
            "111111111111",
            "100000000001",
            "101101110101",
            "100000000001",
             "111011011101",
            "100000000001",
            "101110110101",
            "100000000001",
            "111111111111"
        ],
        "start": (1.5, 1.5), "exit": (10.5, 7.5), "clue": (7.5, 3.5),
        "answer": "THE SECRET PASSAGE IS EAST",
        "hint": "Shift every letter BACK by two positions.",
        "enemy": (9.5, 5.5), "friend": (4.5, 3.5),
        "intro": "The books whisper a name that was scratched from every family record. One book is warm, as if someone has just closed it, though the dust on its cover is untouched."
    },
    {
        "name": "The Moonlit Crypt",
        "map": [
            "111111111111",
            "100000000001",
            "101011110101",
            "100000000001",
            "101110111101",
            "100000000001",
            "101011110101",
            "100000000001",
            "111111111111"
        ],
        "start": (1.5, 1.5), "exit": (10.5, 7.5), "clue": (5.5, 5.5),
        "answer": "THE LIGHT WILL SET YOU FREE",
        "hint": "Decode the seal with shift -2, then unlock the moon door.",
        "enemy": (9.5, 3.5), "friend": (3.5, 5.5),
        "intro": "The dead do not want revenge. They want the truth to stay buried. Blue light spills from the sealed doorway, and a voice behind it asks whether you came to remember or to forgive."
    }
]

def caesar(value, shift):
    out = []
    for ch in value.upper():
        if "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + shift) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)

for lev in LEVELS:
    lev["cipher"] = caesar(lev["answer"], 2)

level_index = max(0, min(int(save_data.get("level", 0)), len(LEVELS) - 1))
health = max(1, min(100, int(save_data.get("health", 100))))
stamina = 100.0
lantern_oil = 100.0
clues_found = set(save_data.get("clues", []))
if save_data.get("won"):
    level_index, health, clues_found = 0, 100, set()

player_x, player_y = LEVELS[level_index]["start"]
player_angle = 0.0
mode = "menu"
settings_return_mode = "menu"
is_running = True
message = "The manor has been waiting for you."
message_timer = 4.0
wrong_answer_timer = 0.0
puzzle_input = ""
puzzle_feedback = ""
enemy_x, enemy_y = LEVELS[level_index]["enemy"]
enemy_alert = False
enemy_stunned = 0.0
damage_cooldown = 0.0
dialogue_index = 0
dialogue_choices = []
dialogue_speaker = ""
dialogue_lines = []
current_dialogue = "intro"
slider_drag = None
ambient_time = 0.0
step_cycle = 0.0
bob_offset = 0.0
screen_flash = 0.0
heartbeat_timer = 0.0
footstep_timer = 0.0
depth_buffer = []

# Deluxe story and mini-game state
quest_flags = set(save_data.get("quest_flags", []))
mini_game_state = {"name": "", "cards": [], "revealed": [], "matched": set(), "sequence": [],
                   "player_sequence": [], "phase": "ready", "timer": 0.0, "round": 1,
                   "candles": [0, 0, 0, 0, 0], "feedback": ""}
menu_petal_seed = [random.random() for _ in range(34)]
active_theme = settings.get("active_theme", "Haunted")
SEASON_THEMES = {
    "Haunted": {"accent": (165, 111, 206), "particle": (173, 153, 211), "subtitle": "The portraits are watching."},
    "Halloween": {"accent": (255, 112, 42), "particle": (255, 135, 49), "subtitle": "Pumpkins glow where no candle burns."},
    "Christmas": {"accent": (83, 220, 151), "particle": (245, 248, 255), "subtitle": "A silent snowfall covers old footprints."},
    "Winter Snow": {"accent": (122, 204, 255), "particle": (232, 246, 255), "subtitle": "The manor sleeps beneath blue frost."},
    "Blood Moon": {"accent": (224, 65, 100), "particle": (240, 90, 115), "subtitle": "Tonight, the moon remembers everything."},
}
if active_theme not in SEASON_THEMES:
    active_theme = "Haunted"
season_particles = [{"x": random.random(), "y": random.random(), "speed": random.uniform(.035, .13), "phase": random.random()*6.28, "size": random.randint(1, 4)} for _ in range(100)]
story_pages = {
    "story_portrait": ("THE PORTRAIT THAT BLINKED", [
        "At 11:13, the portrait in the west hall blinked. Not both eyes. Just the left one, the eye painted over after the fire.",
        "You lift the frame. Behind it, someone has scratched: 'A family can bury a body. It cannot bury what the body remembers.'",
        "The painted girl is not the monster. She is the witness the family tried to erase. When you turn away, the portrait has changed: now there are four people in it, and one has no face."
    ]),
    "story_christmas": ("THE CHRISTMAS ROOM", [
        "The ballroom is frozen in the middle of a Christmas party from 1897. Paper stars hang motionless, and a tree glows with lights that have no wires.",
        "A music box plays a carol with one note missing. The missing note is the name of the child who was locked outside during the storm.",
        "You place a silver star on the tree. For one warm second, every ghost in the room looks alive. A small voice whispers, 'You remembered me.'"
    ]),
    "story_train": ("THE LAST TRAIN AT MIDNIGHT", [
        "A station platform waits under the cellar. A black train arrives every night, though the tracks end at a brick wall.",
        "Its conductor has no ticket punch, only a pocket watch stopped at the moment the manor's first secret was made.",
        "The train does not carry the dead away. It carries their forgotten memories back to the place that stole them. One empty seat bears your name."
    ]),
    "story_secret": ("THE FAMILY SECRET", [
        "The manor's founder did not seek eternal life. He feared that the truth about his family would outlive him.",
        "He sealed the truth inside three ciphers and made a guardian from every memory he had refused to face. That guardian became the Hollow.",
        "The Witness and the Hollow are two halves of the same lost child: one remembers the kindness, the other remembers the betrayal. Freeing one without hearing the other will leave the curse unfinished."
    ]),
}

QUESTS = [
    ("main", "Break the three cipher seals", "Decode the message hidden in each chapter."),
    ("optional", "The kindest soul", "Find the pink flower memory and learn why it matters."),
    ("optional", "A song without a singer", "Reproduce the ghostly signal in the music room."),
    ("optional", "Five lights, one truth", "Light the candles in the order revealed by the manor."),
    ("optional", "Collector of forgotten things", "Complete the flower-memory pairs."),
]

def set_game_mode(new_mode):
    """Central mode switcher guaranteeing mouse grab/visibility states remain synchronized."""
    global mode
    mode = new_mode
    if mode == "game":
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
    else:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

# Downloaded sound effects
SOUND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "assets", "sounds"
)

def load_external_sound(filename):
    path = os.path.join(SOUND_DIR, filename)
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, OSError) as error:
        print(f"Could not load {filename}: {error}")
        return None

sound_footsteps_file = None

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    sound_footsteps_file = load_external_sound("footsteps.mp3")

except pygame.error as error:
    print("Audio initialization failed:", error)



def start_background_music():
    music_path = os.path.join(SOUND_DIR, "background.mp3")

    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(
            settings.get("master_volume", 0.65)
            * settings.get("music_volume", 0.5)
        )
        pygame.mixer.music.play(-1)
    except (pygame.error, OSError) as error:
        print("Could not load background music:", error)

# Procedural Sound Synthesizer (Zero audio files required)
def make_tone(freq=440, duration=0.10, volume=0.15, decay=False):
    sample_rate = 22050
    n = int(sample_rate * duration)
    buf = array("h")
    for i in range(n):
        fade = min(1.0, i / 250, (n - i) / 400)
        curr_freq = freq * (1.0 - 0.45 * (i / n)) if decay else freq
        val = int(32767 * volume * fade * math.sin(2 * math.pi * curr_freq * i / sample_rate))
        buf.append(max(-32767, min(32767, val)))
    return pygame.mixer.Sound(buffer=buf.tobytes())

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
    sound_click = make_tone(660, 0.06, 0.13)
    sound_success = make_tone(880, 0.16, 0.18)
    sound_warning = make_tone(115, 0.22, 0.17)
    sound_whisper = make_tone(310, 0.10, 0.08)
    sound_heartbeat = make_tone(58, 0.09, 0.28, decay=True)
    sound_footstep = make_tone(130, 0.04, 0.06, decay=True)
    sound_flash = make_tone(540, 0.25, 0.22, decay=True)
except Exception:
    sound_click = sound_success = sound_warning = sound_whisper = sound_heartbeat = sound_footstep = sound_flash = None

    sound_heartbeat = sound_footstep = sound_flash = None

def play_sound(snd):
    if snd:
        try:
            vol = settings.get("master_volume", 0.65) * settings.get("sfx_volume", 0.8)
            snd.set_volume(max(0.0, min(1.0, vol)))
            snd.play()
        except Exception:
            pass

def persist_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass

def persist_save(won=False):
    data = {
        "level": level_index,
        "health": health,
        "clues": sorted(list(clues_found)),
        "won": won,
        "difficulty": settings.get("difficulty", "Normal"),
        "quest_flags": sorted(quest_flags)
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass

def current_level():
    return LEVELS[level_index]

def map_cell(x, y):
    lev = current_level()
    ix, iy = int(x), int(y)
    if iy < 0 or iy >= len(lev["map"]) or ix < 0 or ix >= len(lev["map"][0]):
        return 1
    return int(lev["map"][iy][ix])

def can_move(x, y):
    return map_cell(x, y) == 0

def reset_level(idx):
    global level_index, player_x, player_y, player_angle, enemy_x, enemy_y, enemy_alert
    global health, stamina, lantern_oil, enemy_stunned
    level_index = idx
    lev = current_level()
    player_x, player_y = lev["start"]
    player_angle = 0.0
    enemy_x, enemy_y = lev["enemy"]
    enemy_alert = False
    enemy_stunned = 0.0
    health = 100
    stamina = 100.0
    lantern_oil = 100.0
    persist_save()

def set_message(txt, seconds=3.0):
    global message, message_timer
    message, message_timer = txt, seconds

def text(surface, value, x, y, font=FONT, color=None, center=False):
    if color is None:
        color = (239, 228, 248) if settings.get("dark_mode", True) else (38, 28, 48)
    img = font.render(str(value), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    surface.blit(img, rect)
    return rect

def wrap_text(value, font, max_width):
    words = value.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def panel(surface, rect, alpha=225):
    box = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    if settings.get("dark_mode", True):
        pygame.draw.rect(box, (9, 9, 24, alpha), box.get_rect(), border_radius=14)
        pygame.draw.rect(box, (156, 104, 220, 235), box.get_rect(), 2, border_radius=14)
    else:
        pygame.draw.rect(box, (248, 242, 255, alpha), box.get_rect(), border_radius=14)
        pygame.draw.rect(box, (93, 65, 143, 235), box.get_rect(), 2, border_radius=14)
    surface.blit(box, rect[:2])

def draw_button(label, rect, active=False):
    r = pygame.Rect(rect)
    hover = r.collidepoint(pygame.mouse.get_pos())
    dark = settings.get("dark_mode", True)
    fill = (48, 31, 74) if dark else (226, 213, 243)
    if hover or active:
        fill = (105, 53, 143) if dark else (194, 164, 227)
    pygame.draw.rect(screen, fill, r, border_radius=10)
    pygame.draw.rect(screen, (210, 166, 255), r, 2, border_radius=10)
    text(screen, label, r.centerx, r.centery, SMALL, center=True)
    return r
