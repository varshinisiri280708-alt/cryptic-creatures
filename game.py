"""PART 4 - Main game loop: input handling, player/enemy updates, game states.

Run the game with:  python main.py
Imports shared state from core.py as `core.<name>`.
"""
import math
import os
import random
import sys

import pygame

import core
from core import *
from rendering import *
from screens import *

def main():
    set_game_mode("menu")

    while core.is_running:
        dt = min(0.04, clock.tick(60) / 1000.0)
        core.ambient_time += dt
        core.message_timer = max(0.0, core.message_timer - dt)
        if core.mode == "minigame_play" and mini_game_state.get("name") == "Flower Memory" and mini_game_state.get("phase") == "hide_next":
            mini_game_state["timer"] += dt
            if mini_game_state["timer"] >= 0.7:
                mini_game_state["revealed"] = []
                mini_game_state["phase"] = "ready"
                mini_game_state["timer"] = 0.0
        if core.mode == "wrong_answer":
            core.wrong_answer_timer = max(0.0, core.wrong_answer_timer - dt)
            if core.wrong_answer_timer <= 0:
                core.clues_found.clear()
                core.puzzle_input = ""
                core.puzzle_feedback = ""
                reset_level(0)
                set_message("A new attempt begins. Decode the first seal!", 4.0)
                set_game_mode("menu")
        core.damage_cooldown = max(0.0, core.damage_cooldown - dt)
        core.screen_flash = max(0.0, core.screen_flash - dt * 2.5)
        if core.enemy_stunned > 0:
            core.enemy_stunned = max(0.0, core.enemy_stunned - dt)

        # Passive oil regeneration
        core.lantern_oil = min(100.0, core.lantern_oil + dt * 4.0)

        mouse_delta = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                persist_save()
                persist_settings()
                core.is_running = False

            elif event.type == pygame.VIDEORESIZE:
                core.WIDTH, core.HEIGHT = max(800, event.w), max(500, event.h)
                core.screen = pygame.display.set_mode((core.WIDTH, core.HEIGHT), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if core.mode == "dialogue" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if core.dialogue_index < len(core.dialogue_lines) - 1:
                        core.dialogue_index += 1
                    else:
                        choose_dialogue(0)
                elif core.mode == "dialogue" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    if core.dialogue_index >= len(core.dialogue_lines) - 1:
                        choose_dialogue(event.key - pygame.K_1)
                elif event.key == pygame.K_ESCAPE:
                    if core.mode == "game":
                        set_game_mode("pause")
                    elif core.mode in ("puzzle", "dialogue", "journal"):
                        set_game_mode("game")
                    elif core.mode == "settings":
                        set_game_mode(settings_return_mode)
                    elif core.mode in ("customize", "instructions", "minigames", "quest_board", "story_gallery", "theme_gallery"):
                        set_game_mode("menu" if core.mode in ("customize", "instructions") else "minigames")
                    elif core.mode == "minigame_play":
                        set_game_mode("minigames")
                    elif core.mode == "pause":
                        set_game_mode("game")
                    elif core.mode in ("victory", "failure", "level_complete", "wrong_answer"):
                        set_game_mode("menu")
                elif core.mode == "game" and event.key == pygame.K_e:
                    interact()
                elif core.mode == "game" and event.key == pygame.K_j:
                    set_game_mode("journal")
                elif core.mode == "journal" and event.key == pygame.K_j:
                    set_game_mode("game")
                elif core.mode == "game" and event.key == pygame.K_m:
                    core.settings["minimap"] = not core.settings.get("minimap", True)
                    persist_settings()
                elif core.mode == "game" and event.key == pygame.K_SPACE:
                    trigger_lantern_flash()
                elif core.mode == "puzzle":
                    if event.key == pygame.K_RETURN:
                        submit_puzzle()
                    elif event.key == pygame.K_BACKSPACE:
                        core.puzzle_input = core.puzzle_input[:-1]
                    elif event.key == pygame.K_j:
                        set_game_mode("journal")
                    elif event.unicode and event.unicode.isprintable() and len(core.puzzle_input) < 65:
                        core.puzzle_input += event.unicode.upper()
                elif core.mode == "game" and event.key == pygame.K_l:
                    if math.hypot(current_level()["friend"][0]-core.player_x, current_level()["friend"][1]-core.player_y) < 4.0:
                        start_dialogue("mirror")
                    else:
                        set_message("The lantern catches a face in the stonework. It is yours.", 2.5)
                elif core.mode == "game" and event.key == pygame.K_q:
                    set_game_mode("quest_board")
                elif core.mode == "game" and event.key == pygame.K_t:
                    names = list(SEASON_THEMES)
                    core.active_theme = names[(names.index(core.active_theme) + 1) % len(names)] if core.active_theme in names else names[0]
                    core.settings["active_theme"] = core.active_theme
                    persist_settings()
                    set_message("Seasonal realm changed: " + core.active_theme, 2.5)

            elif event.type == pygame.MOUSEMOTION and core.mode == "game":
                if pygame.mouse.get_focused():
                    mouse_delta += event.rel[0]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if core.mode == "game" and event.button == 3:  # Right Click
                    trigger_lantern_flash()
                elif core.mode == "journal":
                    back = draw_journal()
                    if back.collidepoint(event.pos):
                        set_game_mode("game")
                elif core.mode == "minigames":
                    clicked = find_button(draw_hub(), event.pos)
                    if clicked in ("Flower Memory", "Ghost Signal", "Candle Order"):
                        start_minigame(clicked)
                    elif clicked == "Quest Board":
                        set_game_mode("quest_board")
                    elif clicked == "Story Chapters":
                        set_game_mode("story_gallery")
                    elif clicked == "Theme Gallery":
                        set_game_mode("theme_gallery")
                    elif clicked == "Back to Title":
                        set_game_mode("menu")
                elif core.mode == "story_gallery":
                    rects = draw_story_gallery()
                    for label, item in rects.items():
                        r, key = item
                        if r.collidepoint(event.pos):
                            if key == "back":
                                set_game_mode("minigames")
                            else:
                                start_dialogue(key)
                            break
                elif core.mode == "theme_gallery":
                    rects = draw_theme_gallery()
                    clicked = find_button(rects, event.pos)
                    if clicked in SEASON_THEMES:
                        core.active_theme = clicked
                        core.settings["active_theme"] = core.active_theme
                        persist_settings()
                    elif clicked == "Back to Side Stories":
                        set_game_mode("minigames")
                elif core.mode == "quest_board":
                    back = draw_quest_board()
                    if back.collidepoint(event.pos):
                        set_game_mode("minigames")
                elif core.mode == "minigame_play":
                    rects = draw_minigame()
                    clicked = find_button(rects, event.pos)
                    if clicked == "Back to Side Stories":
                        set_game_mode("minigames")
                    elif clicked is not None:
                        handle_minigame_click(clicked)
                elif core.mode == "settings":
                    sliders, rects = draw_settings()
                    for key, r, lo, hi in sliders:
                        if r.inflate(0, 18).collidepoint(event.pos):
                            core.slider_drag = (key, r, lo, hi)
                            break
                    if core.slider_drag is None:
                        clicked = find_button(rects, event.pos)
                        if clicked == "theme":
                            core.settings["dark_mode"] = not core.settings.get("dark_mode", True)
                            persist_settings()
                            play_sound(sound_click)
                        elif clicked == "radar":
                            core.settings["minimap"] = not core.settings.get("minimap", True)
                            persist_settings() 
                        elif clicked == "bob":
                            core.settings["head_bob"] = not core.settings.get("head_bob", True)
                            persist_settings()
                        elif clicked == "reset":
                            core.settings = DEFAULT_SETTINGS.copy()
                            persist_settings()
                        elif clicked == "back":
                            set_game_mode(settings_return_mode)
                        elif clicked in ("Story", "Normal", "Nightmare"):
                            core.settings["difficulty"] = clicked
                            persist_settings()

                elif core.mode == "menu":
                    rects = draw_3d_title_menu()
                    clicked = find_button(rects, event.pos)
                    play_sound(sound_click)
                    if clicked == "New Game":
                        core.clues_found.clear()
                        core.puzzle_input = ""
                        core.puzzle_feedback = ""
                        core.wrong_answer_timer = 0.0
                        reset_level(0)
                        start_dialogue("intro")
                    elif clicked == "Continue":
                        saved = load_json(SAVE_FILE, {"level": 0, "health": 100, "clues": [], "won": False})
                        core.clues_found = set(saved.get("clues", []))
                        reset_level(max(0, min(int(saved.get("level", 0)), len(LEVELS) - 1)))
                        core.health = max(1, min(100, int(saved.get("health", 100))))
                        set_game_mode("game")
                    elif clicked == "Mini Games & Tasks":
                        set_game_mode("minigames")
                    elif clicked == "Customize Character":
                        set_game_mode("customize")
                    elif clicked == "Settings":
                        settings_return_mode = "menu"
                        set_game_mode("settings")
                    elif clicked == "How to Play":
                        set_game_mode("instructions")
                    elif clicked == "Quit":
                        core.is_running = False

                elif core.mode == "pause":
                    rects = draw_overlay("PAUSED", "The manor is silent... for now.",
                                         ["Resume", "Journal", "Save Game", "Settings", "How to Play", "Main Menu"])
                    clicked = find_button(rects, event.pos)
                    if clicked == "Resume":
                        set_game_mode("game")
                    elif clicked == "Journal":
                        set_game_mode("journal")
                    elif clicked == "Save Game":
                        persist_save()
                        set_message("Progress saved.", 2)
                    elif clicked == "Settings":
                        settings_return_mode = "pause"
                        set_game_mode("settings")
                    elif clicked == "How to Play":
                        set_game_mode("instructions")
                    elif clicked == "Main Menu":
                        persist_save()
                        set_game_mode("menu")

                elif core.mode == "customize":
                    left, right, back = draw_customize()
                    if left.collidepoint(event.pos):
                        core.settings["character_type"] = (core.settings.get("character_type", 0) - 1) % 4
                    elif right.collidepoint(event.pos):
                        core.settings["character_type"] = (core.settings.get("character_type", 0) + 1) % 4
                    elif back.collidepoint(event.pos):
                        persist_settings()
                        set_game_mode("menu")

                elif core.mode == "dialogue":
                    # Forgiving clicks prevent getting stuck in a dialogue.
                    box = pygame.Rect(core.WIDTH // 2 - 390, core.HEIGHT - 260, 780, 230)
                    if core.dialogue_index < len(core.dialogue_lines) - 1:
                        core.dialogue_index += 1
                    else:
                        choice_hit = None
                        for i in range(len(core.dialogue_choices)):
                            r = pygame.Rect(box.x + 135 + (i % 2) * 300,
                                            box.y + 142 + (i // 2) * 43, 280, 35)
                            if r.collidepoint(event.pos):
                                choice_hit = i
                                break
                        if choice_hit is not None:
                            choose_dialogue(choice_hit)
                        elif box.collidepoint(event.pos) and core.dialogue_choices:
                            # If the click misses a button (e.g. after resizing),
                            # choose the first visible option rather than trapping the player.
                            choose_dialogue(0)

                elif core.mode == "instructions":
                    r = draw_instructions()
                    if r.collidepoint(event.pos):
                        set_game_mode("menu")

                elif core.mode == "level_complete":
                    rects = draw_overlay(
                        "LEVEL COMPLETE!",
                        "Congratulations! You broke the seal. Ready to explore the next level?",
                        ["Continue to Next Level", "Main Menu", "Quit"]
                    )
                    clicked = find_button(rects, event.pos)
                    if clicked == "Continue to Next Level":
                        if core.level_index < len(LEVELS) - 1:
                            reset_level(core.level_index + 1)
                            core.puzzle_input = ""
                            core.puzzle_feedback = ""
                            set_message("Welcome to " + current_level()["name"] + "!", 4.0)
                            play_sound(sound_success)
                            start_dialogue("intro")
                        else:
                            persist_save(won=True)
                            set_game_mode("victory")
                    elif clicked == "Main Menu":
                        set_game_mode("menu")
                    elif clicked == "Quit":
                        persist_save()
                        persist_settings()
                        core.is_running = False

                elif core.mode in ("victory", "failure"):
                    if core.mode == "victory":
                        title = "CURSE LIFTED!"
                        subtitle = "You solved every cipher and freed the Cursed Manor! You are the hero!"
                    else:
                        title = "THE MANOR CLAIMS YOU"
                        subtitle = "The Hollow has caught you. Try another path."
                    rects = draw_overlay(title, subtitle, ["Play Again", "Main Menu", "Quit"])
                    clicked = find_button(rects, event.pos)
                    if clicked == "Play Again":
                        core.clues_found.clear()
                        core.puzzle_input = ""
                        core.puzzle_feedback = ""
                        core.wrong_answer_timer = 0.0
                        reset_level(0)
                        start_dialogue("intro")
                    elif clicked == "Main Menu":
                        persist_save()
                        set_game_mode("menu")
                    elif clicked == "Quit":
                        persist_save()
                        persist_settings()
                        core.is_running = False
        if core.mode == "game":
            keys = pygame.key.get_pressed()

            # Sprinting and stamina
            sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and core.stamina > 5.0
            base_speed = 2.45
            if sprinting:
                base_speed *= 1.65
                core.stamina = max(0.0, core.stamina - dt * 28.0)
            else:
                core.stamina = min(100.0, core.stamina + dt * 18.0)

            move_speed = base_speed * dt
            forward = (1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0) - (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0)
            strafe = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
            is_moving = forward != 0 or strafe != 0

            # Footstep and head-bobbing
            if is_moving:
                step_rate = 11.0 if sprinting else 7.0
                core.step_cycle += dt * step_rate
                core.bob_offset = math.sin(core.step_cycle) * (6.0 if sprinting else 3.5)
                core.footstep_timer += dt
                if core.footstep_timer > (0.28 if sprinting else 0.44):
                    core.footstep_timer = 0.0
                    play_sound(sound_footstep)
            else:
                core.bob_offset = 0.0
                core.footstep_timer = 0.0

            dx = (math.cos(core.player_angle) * forward - math.sin(core.player_angle) * strafe) * move_speed
            dy = (math.sin(core.player_angle) * forward + math.cos(core.player_angle) * strafe) * move_speed
            if can_move(core.player_x + dx, core.player_y):
                core.player_x += dx
            if can_move(core.player_x, core.player_y + dy):
                core.player_y += dy

            if pygame.mouse.get_focused():
                core.player_angle += mouse_delta * core.settings["sensitivity"]
            if keys[pygame.K_LEFT]:
                core.player_angle -= 1.8 * dt
            if keys[pygame.K_RIGHT]:
                core.player_angle += 1.8 * dt

            # AI & Monster Behavior
            damage_factor, enemy_speed, alert_range = difficulty_values()
            dist = math.hypot(core.enemy_x - core.player_x, core.enemy_y - core.player_y)

            # Heartbeat tension sound
            if dist < 4.5:
                core.heartbeat_timer += dt
                interval = max(0.32, dist * 0.18)
                if core.heartbeat_timer >= interval:
                    core.heartbeat_timer = 0.0
                    play_sound(sound_heartbeat)

            if dist < alert_range:
                core.enemy_alert = True

            if core.enemy_alert and core.enemy_stunned <= 0:
                if dist > 0.68:
                    vx, vy = core.player_x - core.enemy_x, core.player_y - core.enemy_y
                    length = max(0.001, math.hypot(vx, vy))
                    speed = enemy_speed * dt
                    nx, ny = core.enemy_x + (vx / length) * speed, core.enemy_y + (vy / length) * speed
                    if can_move(nx, core.enemy_y):
                        core.enemy_x = nx
                    if can_move(core.enemy_x, ny):
                        core.enemy_y = ny
                elif dist <= 0.68 and core.damage_cooldown <= 0:
                    damage = {"Story": 8, "Normal": 15, "Nightmare": 24}.get(core.settings.get("difficulty", "Normal"), 15)
                    core.health -= damage
                    core.damage_cooldown = 1.2 if core.settings.get("difficulty") != "Nightmare" else 0.95
                    play_sound(sound_warning)
                    set_message("THE HOLLOW STRUCK YOU! RUN OR FLASH YOUR LANTERN!", 2.2)
                    if core.health <= 0:
                        core.health = 0
                        persist_save()
                        set_game_mode("failure")

            if dist < 2.5 and random.random() < 0.008:
                play_sound(sound_whisper)

        # Rendering by mode
        if core.mode == "game":
            draw_world()
        elif core.mode == "journal":
            draw_journal()
        elif core.mode == "puzzle":
            draw_puzzle()
        elif core.mode == "dialogue":
            draw_dialogue()
        elif core.mode == "menu":
            draw_3d_title_menu()
        elif core.mode == "minigames":
            draw_hub()
        elif core.mode == "quest_board":
            draw_quest_board()
        elif core.mode == "story_gallery":
            draw_story_gallery()
        elif core.mode == "theme_gallery":
            draw_theme_gallery()
        elif core.mode == "minigame_play":
            draw_minigame()
        elif core.mode == "settings":
            draw_settings()
        elif core.mode == "customize":
            draw_customize()
        elif core.mode == "instructions":
            draw_instructions()
        elif core.mode == "pause":
            draw_overlay("PAUSED", "The manor is silent... for now.",
                         ["Resume", "Journal", "Save Game", "Settings", "How to Play", "Main Menu"])
        elif core.mode == "level_complete":
            draw_overlay("LEVEL COMPLETE!", "Congratulations! You broke the seal. Ready to explore the next level?",
                         ["Continue to Next Level", "Main Menu", "Quit"])
        elif core.mode == "wrong_answer":
            draw_overlay("INCORRECT CIPHER!", "That answer was wrong. Returning to the beginning shortly.",
                         ["Please Wait"])
        elif core.mode == "victory":
            draw_overlay("CURSE LIFTED!", "You solved every cipher and freed the Cursed Manor! You are the hero!",
                         ["Play Again", "Main Menu", "Quit"])
        elif core.mode == "failure":
            draw_overlay("THE MANOR CLAIMS YOU", "The Hollow has caught you. Try another path.",
                         ["Play Again", "Main Menu", "Quit"])

        pygame.display.flip()

    persist_save()
    persist_settings()
    pygame.quit()
    sys.exit()
