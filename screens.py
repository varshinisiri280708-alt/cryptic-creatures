"""PART 3 - Screens, dialogue, puzzles, hub galleries & mini-games.

Imports shared state from core.py as `core.<name>` and drawing helpers from rendering.py.
"""
import math
import random

import pygame

import core
from core import *
from rendering import *

def draw_journal():
    draw_world()
    overlay = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    core.screen.blit(overlay, (0, 0))

    panel(core.screen, (core.WIDTH // 2 - 380, 45, 760, core.HEIGHT - 90), 245)
    text(core.screen, "MANOR JOURNAL & CIPHER CODEX", core.WIDTH // 2, 75, TITLE, center=True)

    y = 135
    text(core.screen, "CHAPTER SEALS & PROGRESS", core.WIDTH // 2 - 330, y, SMALL, (216, 177, 255))
    y += 26
    for i, lev in enumerate(LEVELS):
        status = "[SOLVED]" if i in core.clues_found else ("[ACTIVE]" if i == core.level_index else "[LOCKED]")
        color = (130, 240, 160) if i in core.clues_found else ((240, 200, 110) if i == core.level_index else (160, 150, 180))
        text(core.screen, f"Seal {i + 1}: {lev['name']} — {status}", core.WIDTH // 2 - 330, y, SMALL, color)
        y += 24
        if i in core.clues_found or i == core.level_index:
            text(core.screen, f"   Cipher: {lev['cipher']}", core.WIDTH // 2 - 330, y, TINY, (190, 225, 255))
            y += 20
            if i in core.clues_found:
                text(core.screen, f"   Decoded: {lev['answer']}", core.WIDTH // 2 - 330, y, TINY, (140, 255, 180))
                y += 22

    y += 10
    text(core.screen, "CAESAR CIPHER WHEEL (SHIFT -2)", core.WIDTH // 2 - 330, y, SMALL, (216, 177, 255))
    y += 28

    plain = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z"
    cipher = "C D E F G H I J K L M N O P Q R S T U V W X Y Z A B"
    text(core.screen, f"Encoded (+2):   {cipher}", core.WIDTH // 2 - 330, y, TINY, (245, 170, 170))
    y += 22
    text(core.screen, f"Decoded (-2):   {plain}", core.WIDTH // 2 - 330, y, TINY, (160, 245, 180))
    y += 30

    text(core.screen, "SURVIVAL TACTICS", core.WIDTH // 2 - 330, y, SMALL, (216, 177, 255))
    y += 24
    tactics = [
        "• Hold SHIFT to sprint away when The Hollow charges at you.",
        "• Press SPACE to trigger the Lantern Flash. It blinds and pushes the beast back.",
        "• Your Lantern Oil recharges slowly over time while resting."
    ]
    for tac in tactics:
        text(core.screen, tac, core.WIDTH // 2 - 330, y, TINY, (220, 215, 235))
        y += 20

    back_btn = draw_button("Close Journal (J / ESC)", (core.WIDTH // 2 - 130, core.HEIGHT - 95, 260, 42))
    return back_btn

def start_dialogue(kind="intro"):
    core.current_dialogue = kind
    core.dialogue_index = 0
    if kind == "intro":
        core.dialogue_speaker = ("THE WITNESS" if core.level_index == 0 else ("THE TRAPPED CARETAKER" if core.level_index == 1 else "THE HOLLOW"))
        level_openings = [
            [current_level()["intro"], "The owner removed one name from every ledger, portrait, and birth record. The ink is newer than the pages around it.", "I heard the master say: 'If the house forgets her, the world will follow.' Find the brass register in the west hall.", "The candle marks the place where the missing page was hidden. Do not trust the family tree hanging above it."],
            [current_level()["intro"], "I am the caretaker. I locked myself in this wing when the portraits began changing at twelve. Each frame shows a different version of the same night.", "The clock does not measure time here; it counts the lies still believed. When it strikes midnight, look at the portrait with no eyes.", "I hid the winding key inside a music box. The tune is backwards because the room remembers events in reverse."],
            [current_level()["intro"], "You were summoned because you carry the only memory the family could not steal: the choice made before the fire.", "I am called the Hollow because they carved every name from me. I guarded the truth, but the lock became my prison.", "Three seals remain. Break them to uncover who called you here—and decide whether the truth will free the dead or bind the living."],
        ]
        core.dialogue_lines = level_openings[core.level_index][:]
        core.dialogue_choices = ([ ("Ask about the erased name", "identity"), ("Ask about the Hollow", "hollow"), ("Leave quietly", "close") ] if core.level_index == 0 else ([ ("Ask about the changing portraits", "history"), ("Ask about the clock", "mirror"), ("Leave quietly", "close") ] if core.level_index == 1 else [ ("Ask why I was summoned", "history"), ("Ask about the three seals", "hollow"), ("Leave quietly", "close") ]))
    elif kind == "identity":
        core.dialogue_speaker = "THE WITNESS"
        core.dialogue_lines = [
            "I was once the manor's youngest daughter. The fire took my face, not my memory.",
            "My name is written in the cipher you are about to solve. Read it, and I may remember the rest.",
            "I hid the first key beneath a candle before the fire began. The flame never touched it; the family simply stopped looking.",
            "When the portrait eyes turn toward the window, someone in the room is lying."
        ]
        core.dialogue_choices = [("Ask what happened here", "history"), ("Return to the clue", "close")]
    elif kind == "hollow":
        core.dialogue_speaker = "THE WITNESS"
        core.dialogue_lines = [
            "The Hollow was a keeper, not a killer. Someone taught it to hunt anyone carrying the truth.",
            "If it catches you, do not curse it. Ask what it is protecting.",
            "I heard it speak once. It said, 'I kept the promise even after everyone forgot what was promised.'",
            "The red in its eyes is not rage. It is the last light from the room where the truth was buried."
        ]
        core.dialogue_choices = [("Ask about the curse", "history"), ("Return to the clue", "close")]
    elif kind == "flower_story":
        core.dialogue_speaker = "THE WITNESS"
        core.dialogue_lines = [
            "Those flowers were planted by someone who refused to let the house become cruel.",
            "Each petal held a memory. The family tried to burn the memories, but kindness grows back in strange places.",
            "If you restore the flower pattern, I may remember the name I lost."
        ]
        core.dialogue_choices = [("I will restore it", "close"), ("Who planted them?", "history")]
    elif kind == "mirror":
        core.dialogue_speaker = "THE WITNESS"
        core.dialogue_lines = [
            "Do not trust the mirror when it shows you a room you have not entered.",
            "The reflection is not predicting your future. It is remembering a past the house stole from you."
        ]
        core.dialogue_choices = [("Return to exploring", "close"), ("Ask about the stolen memory", "history")]
    elif kind in story_pages:
        core.dialogue_speaker, core.dialogue_lines = story_pages[kind]
        core.dialogue_choices = [("Read the next memory", "story_next"), ("Return to stories", "story_gallery")]
    elif kind == "history":
        core.dialogue_speaker = "THE WITNESS"
        core.dialogue_lines = [
            "The family tried to trade a memory for immortality. They chose the memory of their own crime.",
            "Three seals hold that stolen memory. Break them, and the manor will have to remember.",
            "The first seal tells you where the key was hidden. The second reveals who opened the passage. The last asks whether the guilty deserve to be heard.",
            "Do not rush to destroy the Hollow. It is the lock as much as it is the jailer."
        ]    
        core.dialogue_choices = [("Return to the clue", "close")]
    set_game_mode("dialogue")

def draw_dialogue():
    draw_world()
    overlay = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 115))
    core.screen.blit(overlay, (0, 0))
    box = (core.WIDTH // 2 - 390, core.HEIGHT - 260, 780, 230)
    panel(core.screen, box, 242)
    pygame.draw.circle(core.screen, (25, 44, 62), (box[0] + 72, box[1] + 76), 43)
    pygame.draw.circle(core.screen, (93, 223, 247), (box[0] + 72, box[1] + 76), 43, 2)
    pygame.draw.ellipse(core.screen, (92, 225, 245), (box[0] + 52, box[1] + 51, 40, 52))
    pygame.draw.circle(core.screen, (235, 255, 255), (box[0] + 64, box[1] + 69), 4)
    pygame.draw.circle(core.screen, (235, 255, 255), (box[0] + 80, box[1] + 69), 4)
    text(core.screen, core.dialogue_speaker, box[0] + 135, box[1] + 18, SMALL, (139, 225, 255))
    line = core.dialogue_lines[min(core.dialogue_index, len(core.dialogue_lines) - 1)]
    for i, row in enumerate(wrap_text(line, SMALL, 590)[:3]):
        text(core.screen, row, box[0] + 135, box[1] + 48 + i * 23, SMALL)
    if core.dialogue_index >= len(core.dialogue_lines) - 1:
        for i, (label, _) in enumerate(core.dialogue_choices):
            draw_button(f"{i + 1}. {label}", (box[0] + 135 + (i % 2) * 300, box[1] + 142 + (i // 2) * 43, 280, 35))
        text(core.screen, "Choose with mouse or press 1–3", box[0] + 135, box[1] + 208, TINY, (184, 165, 205))
    else:
        text(core.screen, "Press ENTER / SPACE or click to continue", box[0] + 135, box[1] + 190, TINY, (184, 165, 205))

def choose_dialogue(index):
    if index < 0 or index >= len(core.dialogue_choices):
        return
    action = core.dialogue_choices[index][1]
    play_sound(sound_click)
    if action == "story_next":
        if core.dialogue_index < len(core.dialogue_lines)-1:
            core.dialogue_index += 1
        else:
            core.dialogue_choices = [("Return to stories", "story_gallery"), ("Keep exploring", "close")]
        return
    if action == "story_gallery":
        set_game_mode("story_gallery")
    elif action == "close":
        set_game_mode("game")
        set_message("The Witness's words linger in the cold air.", 3)
    else:
        start_dialogue(action)

def interact():
    lev = current_level()
    clue_dist = math.hypot(lev["clue"][0] - core.player_x, lev["clue"][1] - core.player_y)
    exit_dist = math.hypot(lev["exit"][0] - core.player_x, lev["exit"][1] - core.player_y)
    friend_dist = math.hypot(lev["friend"][0] - core.player_x, lev["friend"][1] - core.player_y)
    if friend_dist < 1.5:
        start_dialogue("flower_story" if "flower_memory" in quest_flags else "intro")
        return
    if clue_dist < 1.45 and core.level_index not in core.clues_found:
        core.puzzle_input, core.puzzle_feedback = "", ""
        set_game_mode("puzzle")
        return
    if exit_dist < 1.5:
        if core.level_index not in core.clues_found:
            set_message("The moon seal is closed. Decode the Witness's message first.", 4)
            play_sound(sound_warning)
        elif core.level_index < len(LEVELS) - 1:
            reset_level(core.level_index + 1)
            set_message("The staircase descends. Something below has heard you.", 4)
            play_sound(sound_success)
            start_dialogue("intro")
        else:
            persist_save(won=True)
            set_game_mode("victory")
            play_sound(sound_success)
        return
    set_message("Nothing close enough. Find the cyan sigil or the floating Witness.", 2.5)

def submit_puzzle():

    answer = "".join(ch for ch in core.puzzle_input.strip().upper() if ch.isalpha())
    expected = "".join(ch for ch in current_level()["answer"] if ch.isalpha())

    if answer == expected:
        core.clues_found.add(core.level_index)
        persist_save()
        core.puzzle_feedback = "CORRECT! SEAL BROKEN! WELL DONE!"
        play_sound(sound_success)

        if core.level_index < len(LEVELS) - 1:
            # Show a celebration screen and let the player choose to continue.
            set_game_mode("level_complete")
        else:
            # The final cipher completes the whole game.
            persist_save(won=True)
            set_game_mode("victory")
    else:
        core.puzzle_feedback = "WRONG ANSWER! Returning to the beginning..."
        play_sound(sound_warning)
        core.wrong_answer_timer = 2.5
        set_game_mode("wrong_answer")

def draw_settings():
    draw_menu_background()
    panel(core.screen, (core.WIDTH // 2 - 310, 25, 620, core.HEIGHT - 50), 240)
    text(core.screen, "SETTINGS", core.WIDTH // 2, 56, TITLE, center=True)
    items = [("Master volume", "master_volume", 108), ("Music volume", "music_volume", 166),
             ("Sound effects", "sfx_volume", 224), ("Mouse sensitivity", "sensitivity", 282)]
    sliders = []
    for label, key, y in items:
        text(core.screen, label, core.WIDTH // 2 - 235, y, SMALL)
        shown = f"{int(core.settings[key] * 100)}%" if "volume" in key else f"{core.settings[key] * 1000:.1f}"
        text(core.screen, shown, core.WIDTH // 2 + 230, y, SMALL)
        r = pygame.Rect(core.WIDTH // 2 - 235, y + 24, 470, 9)
        lo, hi = (0.0, 1.0) if "volume" in key else (0.0008, 0.005)
        pygame.draw.rect(core.screen, (62, 48, 83), r, border_radius=5)
        ratio = max(0.0, min(1.0, (core.settings[key] - lo) / (hi - lo)))
        pygame.draw.rect(core.screen, (171, 106, 240), (r.x, r.y, int(r.w * ratio), r.h), border_radius=5)
        pygame.draw.circle(core.screen, (244, 228, 255), (r.x + int(r.w * ratio), r.centery), 8)
        sliders.append((key, r, lo, hi))

    text(core.screen, "Radar overlay", core.WIDTH // 2 - 235, 342, SMALL)
    radar_btn = draw_button("ENABLED" if core.settings.get("minimap", True) else "DISABLED", (core.WIDTH // 2 + 85, 334, 150, 34))

    text(core.screen, "Head bobbing", core.WIDTH // 2 - 235, 388, SMALL)
    bob_btn = draw_button("ENABLED" if core.settings.get("head_bob", True) else "DISABLED", (core.WIDTH // 2 + 85, 380, 150, 34))

    text(core.screen, "Interface theme", core.WIDTH // 2 - 235, 434, SMALL)
    theme = draw_button("DARK MODE: ON" if core.settings.get("dark_mode", True) else "LIGHT MODE: ON", (core.WIDTH // 2 + 35, 426, 200, 34))

    text(core.screen, "Difficulty", core.WIDTH // 2 - 235, 480, SMALL)
    diff_rects = {}
    for i, diff in enumerate(["Story", "Normal", "Nightmare"]):
        diff_rects[diff] = draw_button(diff, (core.WIDTH // 2 - 40 + i * 105, 472, 98, 34), core.settings.get("difficulty") == diff)

    reset = draw_button("Reset defaults", (core.WIDTH // 2 - 220, 532, 190, 38))
    back = draw_button("Back", (core.WIDTH // 2 + 30, 532, 190, 38))
    buttons = {"theme": theme, "radar": radar_btn, "bob": bob_btn, "reset": reset, "back": back, **diff_rects}
    return sliders, buttons

def draw_customize():
    draw_menu_background()
    panel(core.screen, (core.WIDTH // 2 - 300, 55, 600, core.HEIGHT - 110), 240)
    text(core.screen, "CHARACTER SELECT", core.WIDTH // 2, 88, TITLE, center=True)
    names = ["Manor Hunter", "Moon Witch", "Royal Knight", "Phantom"]
    idx = int(core.settings.get("character_type", 0)) % len(names)
    colors = [(35, 31, 50), (43, 76, 111), (105, 35, 65), (43, 87, 65), (118, 98, 139)]
    cloak = colors[int(core.settings.get("character_color", 2)) % len(colors)]
    cx, cy = core.WIDTH // 2, 245
    pygame.draw.ellipse(core.screen, (2, 2, 9), (cx-90, cy+80, 180, 27))
    if idx == 0:
        pygame.draw.polygon(core.screen, cloak, [(cx-68,cy+95),(cx-48,cy+5),(cx-25,cy-10),(cx+25,cy-10),(cx+48,cy+5),(cx+68,cy+95)])
        pygame.draw.ellipse(core.screen,(214,170,139),(cx-25,cy-62,50,62))
        pygame.draw.arc(core.screen,(30,18,35),(cx-28,cy-75,56,72),math.pi,2*math.pi,10)
    elif idx == 1:
        pygame.draw.polygon(core.screen, cloak, [(cx-75,cy+95),(cx-40,cy-8),(cx+40,cy-8),(cx+75,cy+95)])
        pygame.draw.polygon(core.screen,(40,25,62),[(cx-40,cy-48),(cx,cy-112),(cx+40,cy-48)])
        pygame.draw.ellipse(core.screen,(214,184,166),(cx-22,cy-58,44,55))
    elif idx == 2:
        pygame.draw.polygon(core.screen, cloak, [(cx-65,cy+95),(cx-55,cy-4),(cx+55,cy-4),(cx+65,cy+95)])
        pygame.draw.rect(core.screen,(150,160,180),(cx-31,cy-65,62,64),border_radius=9)
        pygame.draw.rect(core.screen,(55,65,85),(cx-22,cy-45,44,9),border_radius=3)
        pygame.draw.polygon(core.screen,(190,195,210),[(cx-30,cy-65),(cx-20,cy-88),(cx,cy-72),(cx+20,cy-88),(cx+30,cy-65)])
    else:
        pygame.draw.polygon(core.screen, cloak, [(cx-75,cy+95),(cx-55,cy-25),(cx-30,cy-50),(cx+30,cy-50),(cx+55,cy-25),(cx+75,cy+95),(cx+35,cy+75),(cx,cy+98),(cx-35,cy+75)])
        pygame.draw.ellipse(core.screen,(195,220,235),(cx-28,cy-72,56,68))
        pygame.draw.ellipse(core.screen,(25,30,55),(cx-20,cy-48,12,8))
        pygame.draw.ellipse(core.screen,(25,30,55),(cx+8,cy-48,12,8))
    text(core.screen, "Choose your hero", core.WIDTH // 2, 365, FONT, center=True)
    text(core.screen, names[idx], core.WIDTH // 2, 400, SMALL, (216,177,255), center=True)
    left = draw_button("◀ Previous", (core.WIDTH//2-205, 450, 165, 43))
    right = draw_button("Next ▶", (core.WIDTH//2+40, 450, 165, 43))
    back = draw_button("Save & Back", (core.WIDTH//2-105, 515, 210, 43))
    return left, right, back

def draw_puzzle():
    draw_world()
    overlay = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 155))
    core.screen.blit(overlay, (0, 0))
    panel(core.screen, (core.WIDTH // 2 - 355, core.HEIGHT // 2 - 210, 710, 420), 245)
    text(core.screen, "THE WITNESS' CIPHER", core.WIDTH // 2, core.HEIGHT // 2 - 165, TITLE, center=True)
    text(core.screen, "Decode this message. Caesar shift: -2", core.WIDTH // 2, core.HEIGHT // 2 - 112, SMALL, center=True)
    text(core.screen, current_level()["cipher"], core.WIDTH // 2, core.HEIGHT // 2 - 66, BIG, (107, 225, 255), center=True)
    text(core.screen, current_level()["hint"], core.WIDTH // 2, core.HEIGHT // 2 - 18, SMALL, center=True)
    inp = pygame.Rect(core.WIDTH // 2 - 270, core.HEIGHT // 2 + 24, 540, 48)
    pygame.draw.rect(core.screen, (25, 18, 42), inp, border_radius=8)
    pygame.draw.rect(core.screen, (161, 116, 226), inp, 2, border_radius=8)
    cursor = "▌" if (pygame.time.get_ticks() // 450) % 2 == 0 else ""
    text(core.screen, core.puzzle_input + cursor, inp.x + 14, inp.y + 10, FONT, (245, 235, 255))
    text(core.screen, "Type the full decoded sentence and press ENTER. Press J for Journal wheel. ESC closes.",
         core.WIDTH // 2, core.HEIGHT // 2 + 94, SMALL, center=True)
    if core.puzzle_feedback:
        color = (125, 255, 180) if "Correct" in core.puzzle_feedback else (255, 145, 160)
        text(core.screen, core.puzzle_feedback, core.WIDTH // 2, core.HEIGHT // 2 + 145, SMALL, color, center=True)

def draw_overlay(title, subtitle, buttons):
    draw_menu_background()
    panel(core.screen, (core.WIDTH // 2 - 310, core.HEIGHT // 2 - 235, 620, 470), 240)
    text(core.screen, title, core.WIDTH // 2, core.HEIGHT // 2 - 168, TITLE, center=True)
    for i, line in enumerate(wrap_text(subtitle, SMALL, 520)[:2]):
        text(core.screen, line, core.WIDTH // 2, core.HEIGHT // 2 - 118 + i * 22, SMALL, center=True)
    rects = {}
    start_y = core.HEIGHT // 2 - 48
    for i, label in enumerate(buttons):
        rects[label] = draw_button(label, (core.WIDTH // 2 - 165, start_y + i * 57, 330, 43))
    return rects

def draw_instructions():
    draw_menu_background()
    panel(core.screen, (core.WIDTH // 2 - 380, 50, 760, core.HEIGHT - 100), 242)
    text(core.screen, "HOW TO SURVIVE", core.WIDTH // 2, 80, TITLE, center=True)
    instructions = [
        ("MOVE", "W / A / S / D — walk and strafe. Arrow keys can also turn."),
        ("SPRINT", "Hold LEFT SHIFT to sprint. Consumes stamina."),
        ("LANTERN STUN", "Press SPACE or RIGHT CLICK to emit a blinding flash. Stuns the monster!"),
        ("JOURNAL", "Press J to view solved seals, notes, and the built-in cipher wheel."),
        ("RADAR", "Press M to toggle the real-time mini-map radar overlay."),
        ("CIPHERS", "Seals use Caesar cipher (+2). Shift letters backward by 2 (e.g. C -> A)."),
        ("INTERACT", "Press E near the floating Witness, cyan sigil, or Moon Door."),
    ]
    y = 132
    for head, body in instructions:
        text(core.screen, head, core.WIDTH // 2 - 320, y, SMALL, (181, 134, 237))
        y += 22
        for line in wrap_text(body, SMALL, 640):
            text(core.screen, line, core.WIDTH // 2 - 320, y, SMALL)
            y += 20
        y += 6
    back = draw_button("Back to Menu", (core.WIDTH // 2 - 115, core.HEIGHT - 92, 230, 40))
    return back

def find_button(rects, pos):
    for label, rect in rects.items():
        if rect.collidepoint(pos):
            return label
    return None

def difficulty_values():
    return {
        "Story": (1.05, 0.45, 2.8),
        "Normal": (1.0, 0.70, 5.5),
        "Nightmare": (0.78, 1.05, 7.2)
    }.get(
        core.settings.get("difficulty", "Normal"),
        (1.0, 0.7, 5.5)
    )

def draw_hub(title="THE MANOR'S SIDE STORIES"):
    draw_menu_background()
    panel(core.screen,(core.WIDTH//2-350,42,700,core.HEIGHT-84),245)
    text(core.screen,title,core.WIDTH//2,78,TITLE,center=True)
    cards = [
        ("Flower Memory", "Match six pairs. Restore a memory of the kindest soul."),
        ("Ghost Signal", "Repeat the ghost's growing sequence of lights."),
        ("Candle Order", "Light five candles in the order hidden in the rhyme."),
        ("Quest Board", "Review your main objective and optional tasks."),
        ("Story Chapters", "Read four hidden stories from the manor's past."),
        ("Theme Gallery", "Switch between Haunted, Halloween, Christmas and snow."),
        ("Back to Title", "Return to the mansion gates.")
    ]
    rects={}
    for i,(name,desc) in enumerate(cards):
        col=i%2; row=i//2
        x=core.WIDTH//2-315+col*325; y=118+row*112
        r=pygame.Rect(x,y,300,94)
        pygame.draw.rect(core.screen,(27,18,43),r,border_radius=12)
        pygame.draw.rect(core.screen,(157,103,178) if i<3 else (174,137,102),r,2,border_radius=12)
        text(core.screen,name,r.centerx,r.y+22,SMALL,(245,215,237),center=True)
        for j,line in enumerate(wrap_text(desc,TINY,260)[:2]): text(core.screen,line,r.centerx,r.y+47+j*16,TINY,(198,184,211),center=True)
        rects[name]=r
    return rects

def draw_story_gallery():
    draw_menu_background()
    draw_seasonal_effects()
    panel(core.screen, (core.WIDTH//2-365, 42, 730, core.HEIGHT-84), 246)
    text(core.screen, "THE MANOR'S LOST CHAPTERS", core.WIDTH//2, 77, TITLE, center=True)
    text(core.screen, "Choose a memory. Every story changes how the house feels.", core.WIDTH//2, 111, SMALL, (205,184,220), center=True)
    cards = [("The Portrait That Blinked", "story_portrait"), ("The Christmas Room", "story_christmas"),
             ("The Last Train at Midnight", "story_train"), ("The Family Secret", "story_secret")]
    rects = {}
    for i, (label, key) in enumerate(cards):
        col, row = i % 2, i // 2
        r = pygame.Rect(core.WIDTH//2-330+col*340, 150+row*145, 315, 116)
        pygame.draw.rect(core.screen, (24,16,37), r, border_radius=12)
        pygame.draw.rect(core.screen, SEASON_THEMES.get(core.active_theme, SEASON_THEMES["Haunted"])["accent"], r, 2, border_radius=12)
        # little animated painting thumbnail
        pygame.draw.rect(core.screen, (100,65,52), (r.x+14,r.y+17,55,72), 4)
        pygame.draw.ellipse(core.screen, (168,140,145), (r.x+29,r.y+31,25,29))
        pygame.draw.ellipse(core.screen, (25,19,31), (r.x+22,r.y+57,39,27))
        text(core.screen, label, r.centerx+28, r.y+35, SMALL, (246,220,240), center=True)
        text(core.screen, "Read this chapter", r.centerx+28, r.y+66, TINY, (197,178,212), center=True)
        rects[label] = (r, key)
    back = draw_button("Back to Side Stories", (core.WIDTH//2-135, core.HEIGHT-76, 270, 38))
    rects["Back to Side Stories"] = (back, "back")
    return rects

def draw_theme_gallery():
    draw_menu_background()
    draw_seasonal_effects()
    panel(core.screen, (core.WIDTH//2-365, 42, 730, core.HEIGHT-84), 246)
    text(core.screen, "SEASONAL REALMS", core.WIDTH//2, 78, TITLE, center=True)
    text(core.screen, "Pick a visual mood. Press T during gameplay to cycle themes.", core.WIDTH//2, 112, SMALL, (205,184,220), center=True)
    descriptions = {
        "Haunted": "Will-o'-wisps and watchful portraits", "Halloween": "Bats, ember leaves and pumpkin glow",
        "Christmas": "Snowfall and twinkling fairy lights", "Winter Snow": "Quiet blue frost and drifting snow",
        "Blood Moon": "Crimson motes beneath a cursed sky"
    }
    rects = {}
    for i, (name, info) in enumerate(descriptions.items()):
        col, row = i%2, i//2
        r = pygame.Rect(core.WIDTH//2-325+col*335, 150+row*100, 310, 78)
        accent = SEASON_THEMES[name]["accent"]
        pygame.draw.rect(core.screen, (23,16,36), r, border_radius=11)
        pygame.draw.rect(core.screen, accent, r, 3 if name == core.active_theme else 1, border_radius=11)
        # seasonal preview orb
        pygame.draw.circle(core.screen, accent, (r.x+34,r.centery), 15)
        pygame.draw.circle(core.screen, (245,235,255), (r.x+29,r.centery-5), 5)
        text(core.screen, name + ("  ✓" if name == core.active_theme else ""), r.x+62, r.y+18, SMALL, (248,225,245))
        text(core.screen, info, r.x+62, r.y+45, TINY, (196,181,210))
        rects[name] = r
    back = draw_button("Back to Side Stories", (core.WIDTH//2-135, core.HEIGHT-75, 270, 38))
    rects["Back to Side Stories"] = back
    return rects

def draw_quest_board():
    draw_menu_background()
    panel(core.screen,(core.WIDTH//2-370,45,740,core.HEIGHT-90),245)
    text(core.screen,"QUEST BOARD",core.WIDTH//2,78,TITLE,center=True)
    y=140
    for kind,title,desc in QUESTS:
        done = (title=="Break the three cipher seals" and len(core.clues_found)==len(LEVELS)) or \
               (title=="The kindest soul" and "flower_memory" in quest_flags) or \
               (title=="A song without a singer" and "ghost_signal" in quest_flags) or \
               (title=="Five lights, one truth" and "candle_order" in quest_flags) or \
               (title=="Collector of forgotten things" and "flower_memory" in quest_flags)
        pygame.draw.circle(core.screen,(123,238,168) if done else (218,168,225),(core.WIDTH//2-315,y+8),6)
        text(core.screen,("✓ " if done else "◇ ")+title,core.WIDTH//2-294,y,SMALL,(143,245,181) if done else (231,207,239))
        for j,line in enumerate(wrap_text(desc,TINY,580)[:2]): text(core.screen,line,core.WIDTH//2-294,y+24+j*18,TINY,(193,181,207))
        y+=78
    back=draw_button("Back to Side Stories",(core.WIDTH//2-135,core.HEIGHT-94,270,42))
    return back

def start_minigame(name):
    mini_game_state.update({"name":name,"cards":[],"revealed":[],"matched":set(),"sequence":[],"player_sequence":[],"phase":"ready","timer":0.0,"round":1,"candles":[0,0,0,0,0],"feedback":""})
    if name=="Flower Memory":
        deck=["ROSE","ROSE","LILY","LILY","IRIS","IRIS","VIOLET","VIOLET","DAISY","DAISY","LOTUS","LOTUS"]
        random.shuffle(deck); mini_game_state["cards"]=deck
    elif name=="Ghost Signal":
        mini_game_state["sequence"]=[random.randrange(4)]
        mini_game_state["phase"]="show"; mini_game_state["timer"]=1.05
    elif name=="Candle Order":
        mini_game_state["sequence"]=[0,1,2,3,4]
    set_game_mode("minigame_play")

def draw_minigame():
    draw_menu_background()
    name=mini_game_state["name"]
    panel(core.screen,(core.WIDTH//2-360,35,720,core.HEIGHT-70),245)
    text(core.screen,name.upper(),core.WIDTH//2,70,TITLE,center=True)
    rects={}
    if name=="Flower Memory":
        text(core.screen,"Find all six flower pairs. A match restores one memory.",core.WIDTH//2,110,SMALL,center=True)
        card_w,card_h=92,78; gap=12; total=6*card_w+5*gap; sx=core.WIDTH//2-total//2; sy=160
        for i,sym in enumerate(mini_game_state["cards"]):
            row,col=divmod(i,6); r=pygame.Rect(sx+col*(card_w+gap),sy+row*(card_h+gap),card_w,card_h)
            visible=i in mini_game_state["revealed"] or i in mini_game_state["matched"]
            pygame.draw.rect(core.screen,(81,36,75) if visible else (35,24,55),r,border_radius=10)
            pygame.draw.rect(core.screen,(232,161,207) if visible else (136,93,165),r,2,border_radius=10)
            text(core.screen,sym if visible else "✦",r.centerx,r.centery,SMALL,(255,220,237),center=True)
            rects[str(i)]=r
        if len(mini_game_state["matched"])==12:
            mini_game_state["feedback"]="Memory restored! The Witness remembers the garden."
            quest_flags.add("flower_memory"); persist_save()
            text(core.screen,"MEMORY RESTORED!",core.WIDTH//2,core.HEIGHT-125,FONT,(144,255,190),center=True)
        else: text(core.screen,mini_game_state["feedback"] or f"Pairs found: {len(mini_game_state['matched'])//2} / 6",core.WIDTH//2,core.HEIGHT-125,SMALL,(226,196,231),center=True)
    elif name=="Ghost Signal":
        text(core.screen,"Watch the sequence, then repeat it using the four sigils.",core.WIDTH//2,116,SMALL,center=True)
        colors=[(202,91,135),(109,185,213),(208,177,104),(156,118,211)]
        active=-1
        if mini_game_state["phase"]=="show":
            mini_game_state["timer"]-=1/60
            total=len(mini_game_state["sequence"])*0.55+0.5
            elapsed=total-mini_game_state["timer"]
            idx=int(elapsed/0.55)
            active=mini_game_state["sequence"][idx] if idx < len(mini_game_state["sequence"]) and elapsed % 0.55 < 0.36 else -1
            if mini_game_state["timer"]<=0: mini_game_state["phase"]="input"; mini_game_state["player_sequence"]=[]
            text(core.screen,"MEMORIZE THE LIGHTS",core.WIDTH//2,155,SMALL,(238,207,245),center=True)
        for i in range(4):
            r=pygame.Rect(core.WIDTH//2-210+(i%2)*230,205+(i//2)*145,180,110)
            c=colors[i] if i==active else tuple(int(v*.45) for v in colors[i])
            pygame.draw.rect(core.screen,c,r,border_radius=18); pygame.draw.rect(core.screen,(245,222,247),r,2,border_radius=18)
            text(core.screen,["ROSE","MOON","FLAME","EYE"][i],r.centerx,r.centery,SMALL,(255,247,255),center=True); rects[str(i)]=r
        text(core.screen,mini_game_state["feedback"] or f"Sequence length: {len(mini_game_state['sequence'])}",core.WIDTH//2,core.HEIGHT-100,SMALL,(226,196,231),center=True)
    elif name=="Candle Order":
        text(core.screen,"The nursery rhyme says: Flame, Rose, Star, Moon, Thorn.",core.WIDTH//2,118,SMALL,center=True)
        colors=[(211,178,103),(194,83,128),(144,163,228),(161,132,201),(98,160,115)]
        labels=["FLAME","ROSE","STAR","MOON","THORN"]
        for i in range(5):
            x=core.WIDTH//2-270+i*110; y=215
            glow=mini_game_state["candles"][i]
            pygame.draw.ellipse(core.screen,(colors[i] if glow else (48,37,56)),(x,y,64,90))
            pygame.draw.rect(core.screen,(106,83,113),(x+24,y+53,16,67),border_radius=4)
            if glow:
                pygame.draw.circle(core.screen,(*colors[i],100),(x+32,y+12),28)
                pygame.draw.ellipse(core.screen,(255,229,166),(x+24,y-3,16,35))
            text(core.screen,labels[i],x+32,y+135,TINY,(239,217,242),center=True)
            rects[str(i)]=pygame.Rect(x-8,y-8,80,145)
        text(core.screen,"Click candles in the correct order. Clicked candles stay lit.",core.WIDTH//2,420,SMALL,center=True)
        text(core.screen,mini_game_state["feedback"] or f"Candles lit: {sum(mini_game_state['candles'])}/5",core.WIDTH//2,core.HEIGHT-100,SMALL,(226,196,231),center=True)
    back=draw_button("Back to Side Stories",(core.WIDTH//2-135,core.HEIGHT-70,270,38))
    rects["Back to Side Stories"]=back
    return rects

def handle_minigame_click(key):
    st=mini_game_state
    if st["name"]=="Flower Memory":
        i=int(key)
        if i in st["matched"] or i in st["revealed"]: return
        st["revealed"].append(i)
        if len(st["revealed"])==2:
            a,b=st["revealed"]
            if st["cards"][a]==st["cards"][b]:
                st["matched"].update((a,b)); st["revealed"]=[]; play_sound(sound_success)
            else:
                st["feedback"]="Not a pair. Keep their positions in mind."
                # Cards remain visible until next click; the next click hides the mismatch.
                st["phase"]="hide_next"
        elif st["phase"]=="hide_next":
            st["revealed"]=[i]; st["phase"]="ready"
    elif st["name"]=="Ghost Signal" and st["phase"]=="input":
        val=int(key); st["player_sequence"].append(val)
        if st["player_sequence"][-1]!=st["sequence"][len(st["player_sequence"])-1]:
            st["feedback"]="The signal broke. Try the sequence again."
            st["player_sequence"]=[]; st["phase"]="show"; st["timer"]=1.0
        elif len(st["player_sequence"])==len(st["sequence"]):
            if len(st["sequence"])>=5:
                st["feedback"]="Signal restored! A hidden melody returns."
                quest_flags.add("ghost_signal"); persist_save()
            else:
                st["sequence"].append(random.randrange(4)); st["phase"]="show"; st["timer"]=1.0; st["round"]+=1
                st["feedback"]="Correct. The ghost adds another note..."
    elif st["name"]=="Candle Order":
        i=int(key); expected=st["sequence"][sum(st["candles"])]
        if i==expected:
            st["candles"][i]=1; play_sound(sound_success)
            if sum(st["candles"])==5:
                st["feedback"]="The passage opens. The candle task is complete."
                quest_flags.add("candle_order"); persist_save()
        else:
            st["candles"]=[0,0,0,0,0]; st["feedback"]="A candle gutters out. Read the rhyme and try again."
            play_sound(sound_warning)
