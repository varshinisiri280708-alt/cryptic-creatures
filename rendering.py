"""PART 2 - Rendering & visuals (ray-casting world, minimap, monsters, title-menu art).

Imports shared state from core.py as `core.<name>` (e.g. core.health, core.player_x).
"""
import math
import random

import pygame

import core
from core import *  # constants, fonts, textures, helper functions (read-only values)

def draw_seasonal_effects():
    """Lightweight animated seasonal particles; all art is drawn with Pygame primitives."""
    theme = SEASON_THEMES.get(core.active_theme, SEASON_THEMES["Haunted"])
    accent = theme["accent"]
    for i, particle in enumerate(season_particles):
        x = int((particle["x"] * core.WIDTH + math.sin(core.ambient_time * 1.3 + particle["phase"]) * 20) % core.WIDTH)
        particle["y"] += particle["speed"] * (0.55 if core.active_theme == "Halloween" else 1.0) / 60.0
        if particle["y"] > 1.02:
            particle["y"] = -0.02
            particle["x"] = random.random()
        y = int(particle["y"] * core.HEIGHT)
        size = particle["size"]
        if core.active_theme in ("Christmas", "Winter Snow"):
            pygame.draw.circle(core.screen, theme["particle"], (x, y), max(1, size-1))
            if size >= 3:
                pygame.draw.line(core.screen, (255,255,255), (x-size-1,y), (x+size+1,y), 1)
        elif core.active_theme == "Halloween":
            pygame.draw.ellipse(core.screen, theme["particle"], (x, y, size*2+2, size+2))
            pygame.draw.line(core.screen, theme["particle"], (x+size,y+size), (x+size+3,y+size+4), 1)
        elif core.active_theme == "Blood Moon":
            pygame.draw.circle(core.screen, theme["particle"], (x,y), max(1,size//2))
        else:
            pygame.draw.ellipse(core.screen, theme["particle"], (x,y,size*2+1,max(2,size)))
    if core.active_theme == "Halloween":
        # Tiny bats drift across the upper edge.
        for i in range(5):
            bx = int((i * core.WIDTH / 5 + core.ambient_time * (18 + i*3)) % core.WIDTH)
            by = int(core.HEIGHT * .12 + math.sin(core.ambient_time*1.7+i)*12)
            flap = int(3 + abs(math.sin(core.ambient_time*8+i))*5)
            pygame.draw.polygon(core.screen, (30, 15, 36), [(bx,by+3),(bx-9,by-flap),(bx-7,by+5),(bx,by+2),(bx+7,by-flap),(bx+9,by+4)])
    elif core.active_theme == "Christmas":
        # Warm fairy lights along the top frame.
        for i in range(16):
            lx = int((i + .5) * core.WIDTH / 16)
            ly = 12 + int(math.sin(i*.8)*4)
            glow = int(150 + 90*(.5+.5*math.sin(core.ambient_time*3+i)))
            pygame.draw.circle(core.screen, (glow, min(255,glow), 100), (lx,ly), 3)
    elif core.active_theme == "Haunted":
        # Wandering will-o'-wisps.
        for i in range(3):
            wx = int(core.WIDTH*(.18 + i*.31) + math.sin(core.ambient_time*.55+i*2)*28)
            wy = int(core.HEIGHT*(.34 + .08*math.sin(core.ambient_time+i)))
            r = 4 + int(2*(.5+.5*math.sin(core.ambient_time*4+i)))
            pygame.draw.circle(core.screen, (120, 225, 205), (wx,wy), r+5, 1)
            pygame.draw.circle(core.screen, (177,255,231), (wx,wy), r)

def draw_wall_paintings():
    """Animated gothic portraits on the near wall edges, with blinking eyes and shifting frames."""
    for side in (0, 1):
        w = max(70, int(core.WIDTH * .095)); h = max(100, int(core.HEIGHT * .23))
        x = 18 if side == 0 else core.WIDTH - w - 18
        y = int(core.HEIGHT * (.24 + .012 * math.sin(core.ambient_time * .6 + side)))
        frame = SEASON_THEMES.get(core.active_theme, SEASON_THEMES["Haunted"])["accent"]
        pygame.draw.rect(core.screen, (14, 9, 19), (x-5,y-5,w+10,h+10), border_radius=3)
        pygame.draw.rect(core.screen, frame, (x-3,y-3,w+6,h+6), 3, border_radius=3)
        pygame.draw.rect(core.screen, (48, 32, 43), (x,y,w,h))
        # Silhouette and candlelit face
        cx, cy = x+w//2, y+int(h*.43)
        pygame.draw.ellipse(core.screen, (21, 18, 29), (cx-w*.28, y+h*.53, w*.56, h*.42))
        pygame.draw.ellipse(core.screen, (139, 116, 118), (cx-w*.17, cy-h*.20, w*.34, h*.39))
        pygame.draw.arc(core.screen, (205, 180, 174), (cx-w*.18,cy-h*.22,w*.36,h*.42), math.pi, 2*math.pi, 2)
        blink = (int(core.ambient_time*1.7 + side*2.4) % 9) == 0
        eye_y = cy-int(h*.02)
        if not blink:
            pygame.draw.circle(core.screen, (239, 70, 94), (cx-int(w*.07),eye_y), max(2,int(w*.018)))
            pygame.draw.circle(core.screen, (239, 70, 94), (cx+int(w*.07),eye_y), max(2,int(w*.018)))
        else:
            pygame.draw.line(core.screen, (35,15,24), (cx-int(w*.12),eye_y),(cx-int(w*.03),eye_y),2)
            pygame.draw.line(core.screen, (35,15,24), (cx+int(w*.03),eye_y),(cx+int(w*.12),eye_y),2)
        # Gilded plaque beneath each portrait
        pygame.draw.rect(core.screen, (90, 61, 48), (x+w*.18,y+h*.83,w*.64,max(9,h*.08)))
        if side == 0:
            text(core.screen, "THE LOST", cx, y+h*.87, TINY, (238,204,157), center=True)
        else:
            text(core.screen, "THE UNNAMED", cx, y+h*.87, TINY, (238,204,157), center=True)

def draw_menu_background():
    dark = core.settings.get("dark_mode", True)
    core.screen.fill((5, 6, 19) if dark else (224, 219, 239))
    moon = (225, 222, 255) if dark else (255, 250, 218)
    pygame.draw.circle(core.screen, moon, (int(core.WIDTH * 0.78), int(core.HEIGHT * 0.20)), 46)
    pygame.draw.circle(core.screen, (9, 10, 29) if dark else (224, 219, 239),
                       (int(core.WIDTH * 0.805), int(core.HEIGHT * 0.17)), 41)
    for i in range(55):
        x = (i * 97 + 23) % core.WIDTH
        y = (i * 47 + 13) % int(core.HEIGHT * 0.55)
        pygame.draw.circle(core.screen, (145, 129, 188) if dark else (125, 112, 151), (x, y), 1)
    ground = int(core.HEIGHT * 0.70)
    for i in range(14):
        x = int(i * core.WIDTH / 13)
        h = 105 + (i * 47 % 150)
        color = (16, 13, 38) if dark else (82, 72, 111)
        pygame.draw.rect(core.screen, color, (x, ground - h, 72, h + 130))
        pygame.draw.polygon(core.screen, (26, 18, 49) if dark else (103, 87, 132),
                            [(x - 9, ground - h), (x + 36, ground - h - 48), (x + 81, ground - h)])
        for wy in range(ground - h + 18, ground - 10, 29):
            pygame.draw.arc(core.screen, (101, 66, 128), (x + 22, wy, 22, 27), 0, math.pi, 2)
    for i in range(7):
        y = int(core.HEIGHT * 0.72 + i * 21)
        pygame.draw.line(core.screen, (55, 42, 83) if dark else (181, 168, 206), (0, y), (core.WIDTH, y - 20), 2)

def trigger_lantern_flash():
    """Unleashes a blinding radiant flash stunning The Hollow and pushing it back."""
    if core.lantern_oil < 30.0:
        set_message("Lantern oil too low! Rest to replenish.", 2.0)
        play_sound(sound_warning)
        return
    core.lantern_oil -= 30.0
    core.screen_flash = 1.0
    core.enemy_stunned = 3.5
    play_sound(sound_flash)
    dx, dy = core.enemy_x - core.player_x, core.enemy_y - core.player_y
    dist = max(0.1, math.hypot(dx, dy))
    push_x = core.enemy_x + (dx / dist) * 2.0
    push_y = core.enemy_y + (dy / dist) * 2.0
    if can_move(push_x, core.enemy_y):
        core.enemy_x = push_x
    if can_move(core.enemy_x, push_y):
        core.enemy_y = push_y
    set_message("RADIANT FLASH! The Hollow is blinded and repelled!", 3.0)

def draw_gothic_monster(cx, cy, size, phase=0, stunned=False):
    s = max(12, int(size))
    pygame.draw.ellipse(core.screen, (2, 2, 8), (int(cx - s * 0.42), int(cy + s * 0.30), int(s * 0.84), int(s * 0.20)))
    pts = [(cx - s * 0.30, cy - s * 0.18), (cx - s * 0.42, cy + s * 0.32), (cx - s * 0.20, cy + s * 0.22),
           (cx - s * 0.08, cy + s * 0.42), (cx + s * 0.02, cy + s * 0.23), (cx + s * 0.19, cy + s * 0.38),
           (cx + s * 0.39, cy + s * 0.26), (cx + s * 0.28, cy - s * 0.20)]
    body_color = (25, 20, 40) if not stunned else (60, 45, 90)
    pygame.draw.polygon(core.screen, body_color, pts)
    pygame.draw.ellipse(core.screen, (34, 19, 47), (int(cx - s * 0.30), int(cy - s * 0.40), int(s * 0.60), int(s * 0.64)))
    pygame.draw.arc(core.screen, (89, 44, 103), (int(cx - s * 0.29), int(cy - s * 0.35), int(s * 0.58), int(s * 0.64)), 0.2, 2.8, max(1, s // 35))
    pygame.draw.ellipse(core.screen, (4, 3, 12), (int(cx - s * 0.20), int(cy - s * 0.20), int(s * 0.40), int(s * 0.32)))
    eye_y = int(cy - s * 0.04)
    eye_r = max(2, int(s * 0.045))
    flicker = 210 + int(35 * math.sin(phase * 8))
    eye = (140, 180, 255) if stunned else (255, max(25, flicker // 5), max(35, flicker // 4))
    pygame.draw.circle(core.screen, eye, (int(cx - s * 0.09), eye_y), eye_r)
    pygame.draw.circle(core.screen, eye, (int(cx + s * 0.09), eye_y), eye_r)
    pygame.draw.circle(core.screen, (255, 210, 218), (int(cx - s * 0.09), eye_y), max(1, eye_r // 2))
    pygame.draw.circle(core.screen, (255, 210, 218), (int(cx + s * 0.09), eye_y), max(1, eye_r // 2))
    pygame.draw.line(core.screen, (49, 27, 62), (int(cx - s * 0.15), int(cy - s * 0.27)), (int(cx - s * 0.30), int(cy - s * 0.53)), max(2, s // 22))
    pygame.draw.line(core.screen, (49, 27, 62), (int(cx - s * 0.30), int(cy - s * 0.53)), (int(cx - s * 0.34), int(cy - s * 0.62)), max(1, s // 30))
    pygame.draw.line(core.screen, (49, 27, 62), (int(cx + s * 0.15), int(cy - s * 0.27)), (int(cx + s * 0.29), int(cy - s * 0.50)), max(2, s // 22))
    pygame.draw.line(core.screen, (49, 27, 62), (int(cx + s * 0.29), int(cy - s * 0.50)), (int(cx + s * 0.36), int(cy - s * 0.58)), max(1, s // 30))
    if stunned:
        text(core.screen, "BLINDED", cx, cy - s * 0.55, TINY, (180, 220, 255), center=True)

def draw_friendly_spirit(cx, cy, size, phase):
    s = max(12, int(size))
    aura = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
    pygame.draw.circle(aura, (65, 200, 255, 35), (s, s), int(s * 0.75))
    core.screen.blit(aura, (int(cx - s), int(cy - s)))
    pygame.draw.ellipse(core.screen, (65, 204, 235), (int(cx - s * 0.28), int(cy - s * 0.25 + math.sin(phase * 3) * 3), int(s * 0.56), int(s * 0.62)))
    pygame.draw.circle(core.screen, (203, 252, 255), (int(cx - s * 0.10), int(cy - s * 0.02)), max(2, int(s * 0.05)))
    pygame.draw.circle(core.screen, (203, 252, 255), (int(cx + s * 0.10), int(cy - s * 0.02)), max(2, int(s * 0.05)))
    pygame.draw.arc(core.screen, (20, 104, 145), (int(cx - s * 0.11), int(cy + s * 0.04), int(s * 0.22), int(s * 0.13)), math.pi, 2 * math.pi, 2)

def draw_minimap():
    if not core.settings.get("minimap", True):
        return
    lev = current_level()
    mw, mh = len(lev["map"][0]), len(lev["map"])
    tile_size = 9
    map_w, map_h = mw * tile_size, mh * tile_size
    pad = 16
    rect = (core.WIDTH - map_w - pad - 12, pad, map_w + 12, map_h + 30)
    panel(core.screen, rect, 205)
    text(core.screen, "RADAR (M)", rect[0] + rect[2] // 2, rect[1] + 10, TINY, (180, 160, 210), center=True)

    ox, oy = rect[0] + 6, rect[1] + 22
    for my in range(mh):
        for mx in range(mw):
            c = lev["map"][my][mx]
            r = pygame.Rect(ox + mx * tile_size, oy + my * tile_size, tile_size - 1, tile_size - 1)
            if c == "1":
                pygame.draw.rect(core.screen, (48, 36, 68), r, border_radius=2)
            else:
                pygame.draw.rect(core.screen, (16, 12, 28), r, border_radius=2)

    def to_map(wx, wy):
        return int(ox + wx * tile_size), int(oy + wy * tile_size)

    # Clue sigil
    if core.level_index not in core.clues_found:
        cx, cy = to_map(*lev["clue"])
        pygame.draw.circle(core.screen, (32, 195, 232), (cx, cy), 3)

    # Exit
    ex, ey = to_map(*lev["exit"])
    pygame.draw.circle(core.screen, (255, 210, 80), (ex, ey), 3)

    # Witness
    fx, fy = to_map(*lev["friend"])
    pygame.draw.circle(core.screen, (90, 220, 255), (fx, fy), 3)

    # Monster (blinks if close or alert)
    if core.enemy_alert or math.hypot(core.enemy_x - core.player_x, core.enemy_y - core.player_y) < 5.5:
        mx, my = to_map(core.enemy_x, core.enemy_y)
        flicker_color = (255, 40, 80) if int(core.ambient_time * 8) % 2 == 0 else (180, 20, 40)
        pygame.draw.circle(core.screen, flicker_color, (mx, my), 4)

    # Player dot and sight cone line
    px, py = to_map(core.player_x, core.player_y)
    pygame.draw.circle(core.screen, (240, 230, 255), (px, py), 3)
    dir_x = px + int(math.cos(core.player_angle) * 8)
    dir_y = py + int(math.sin(core.player_angle) * 8)
    pygame.draw.line(core.screen, (160, 110, 255), (px, py), (dir_x, dir_y), 2)

def draw_world():
    level = current_level()
    horizon = (core.HEIGHT // 2) + int(core.bob_offset if core.settings.get("head_bob", True) else 0)
    
    dark = core.settings.get("dark_mode", True)

# Select a room theme automatically for each level
    if core.level_index == 0:
    # Level 1: Haunted Mansion - warm, spooky brown
        ceiling_color = (24, 12, 12)
        floor_color = (45, 25, 20)
        wall_tint = (0.68, 0.42, 0.28)
        glow_color = (220, 100, 45, 28)

    elif core.level_index == 1:
    # Level 2: Whispering Library - eerie green
        ceiling_color = (7, 22, 17)
        floor_color = (15, 39, 28)
        wall_tint = (0.32, 0.58, 0.42)
        glow_color = (55, 220, 125, 25)

    else:
    # Level 3: Moonlit Crypt - cold blue
        ceiling_color = (7, 10, 30)
        floor_color = (15, 22, 48)
        wall_tint = (0.32, 0.42, 0.72)
        glow_color = (70, 110, 255, 28)

    core.screen.fill((5, 5, 15) if dark else (184, 177, 199))
    # Perspective-projected repeating ceiling/floor tiles.  The source images are
    # tiled many times across each scanline so they behave like surface materials,
    # not one giant picture stretched over the whole screen.
    pygame.draw.rect(core.screen, ceiling_color if dark else (219, 213, 230), (0, 0, core.WIDTH, horizon))
    pygame.draw.rect(core.screen, floor_color if dark else (117, 105, 131), (0, horizon, core.WIDTH, core.HEIGHT - horizon))
    if dark and horizon > 2:
        tw, th = CEILING_TEXTURE.get_size()
        fw, fh = FLOOR_TEXTURE.get_size()
        tile_step = 3
        tint_rgb = (int(255 * wall_tint[0]), int(255 * wall_tint[1]), int(255 * wall_tint[2]))

        # Ceiling: small repeating tiles near the horizon, larger toward the top.
        for sy in range(0, max(1, horizon - 1), tile_step):
            depth = max(0.10, (horizon - sy) / max(1, core.HEIGHT * 0.62))
            tile_w = max(18, min(260, int(34 + depth * 115)))
            tile_h = max(8, min(th, int(18 + depth * 90)))
            tile = pygame.transform.smoothscale(CEILING_TEXTURE, (tile_w, tile_h))
            tile.fill(tint_rgb, special_flags=pygame.BLEND_RGB_MULT)
            row = tile.subsurface((0, min(tile_h - 1, tile_h // 2), tile_w, 1))
            offset = int((core.player_angle * 32 + core.player_x * 17) % tile_w)
            for sx in range(-tile_w + offset, core.WIDTH, tile_w):
                core.screen.blit(row, (sx, sy))

        # Floor: repeating wooden geometry, with larger tiles toward the camera.
        for sy in range(horizon + 1, core.HEIGHT, tile_step):
            depth = max(0.08, (sy - horizon) / max(1, core.HEIGHT - horizon))
            tile_w = max(16, min(320, int(20 + depth * 210)))
            tile_h = max(8, min(fh, int(12 + depth * 120)))
            tile = pygame.transform.smoothscale(FLOOR_TEXTURE, (tile_w, tile_h))
            tile.fill(tint_rgb, special_flags=pygame.BLEND_RGB_MULT)
            row = tile.subsurface((0, min(tile_h - 1, tile_h // 2), tile_w, 1))
            offset = int((core.player_angle * 48 + core.player_x * 23) % tile_w)
            for sx in range(-tile_w + offset, core.WIDTH, tile_w):
                core.screen.blit(row, (sx, sy))

    # Raycast the world and texture each wall column with the supplied artwork.
    # The hit coordinate selects a horizontal strip of the room image; distance
    # shading preserves depth and keeps the result consistent with the 3D maze.
    fov = math.pi / 3
    ray_count = max(180, core.WIDTH // 4)
    col_w = core.WIDTH / ray_count
    core.depth_buffer = [99.0] * ray_count
    room_texture = ROOM_TEXTURES[core.level_index % len(ROOM_TEXTURES)]
    tex_w, tex_h = room_texture.get_size()

    for ray in range(ray_count):
        ray_angle = core.player_angle - fov / 2 + fov * ray / ray_count
        sin_a, cos_a = math.sin(ray_angle), math.cos(ray_angle)
        depth = 0.05
        rx, ry = core.player_x, core.player_y
        while depth < 16:
            rx, ry = core.player_x + cos_a * depth, core.player_y + sin_a * depth
            if map_cell(rx, ry):
                break
            depth += 0.04
        corrected = max(0.05, depth * math.cos(ray_angle - core.player_angle))
        core.depth_buffer[ray] = corrected
        wall_h = max(1, min(int(core.HEIGHT * 1.5), int(core.HEIGHT / (corrected + 0.12))))
        x = int(ray * col_w)
        y = int(horizon - wall_h / 2)

        # Use the fractional hit position as the texture's U coordinate.
        fx, fy = rx - math.floor(rx), ry - math.floor(ry)
        u = fy if abs(cos_a) > abs(sin_a) else fx
        tex_x = max(0, min(tex_w - 1, int(u * (tex_w - 1))))
        strip = room_texture.subsurface((tex_x, 0, 1, tex_h))
        wall_column = pygame.transform.scale(strip, (max(1, int(col_w) + 1), wall_h))

        # Distance-based darkness plus the chapter's color palette.
        shade = max(0.18, min(0.86, 1.0 / (1.0 + corrected * 0.18)))
        tint = wall_tint if dark else (0.88, 0.82, 0.92)
        wall_column.fill((int(255 * shade * tint[0]),
                          int(255 * shade * tint[1]),
                          int(255 * shade * tint[2])), special_flags=pygame.BLEND_RGB_MULT)
        core.screen.blit(wall_column, (x, y))

    # Ambient Torchlight Glow
    glow = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
    flicker_r = int(core.WIDTH * 0.5 + math.sin(core.ambient_time * 6) * 10)
    
    pygame.draw.ellipse(
        glow,
        glow_color if dark else (255, 230, 190, 22),

        (core.WIDTH * 0.25, core.HEIGHT * 0.40, flicker_r, int(core.HEIGHT * 0.72)))
    core.screen.blit(glow, (0, 0))

    # Sprites Depth Checking
    def project(wx, wy, kind, label):
        dx, dy = wx - core.player_x, wy - core.player_y
        dist = math.hypot(dx, dy)
        if dist < 0.15:
            return
        rel = (math.atan2(dy, dx) - core.player_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(rel) > fov * 0.6:
            return

        ray_idx = int(((rel + fov / 2) / fov) * ray_count)
        if 0 <= ray_idx < ray_count and dist > core.depth_buffer[ray_idx] + 0.35:
            return

        sx = core.WIDTH / 2 + (rel / (fov / 2)) * (core.WIDTH / 2)
        size = min(core.HEIGHT * 0.82, core.HEIGHT / (dist + 0.15) * 0.36)
        sy = horizon + core.HEIGHT / (dist + 0.3) * 0.22

        if kind == "enemy":
            draw_gothic_monster(sx, sy, size * 1.7, core.ambient_time, core.enemy_stunned > 0)
        elif kind == "friend":
            draw_friendly_spirit(sx, sy, size * 1.2, core.ambient_time)
        elif kind == "clue":
            pulse = 1 + 0.10 * math.sin(core.ambient_time * 4)
            r = max(4, int(size * 0.22 * pulse))
            pygame.draw.circle(core.screen, (32, 195, 232), (int(sx), int(sy)), r + 5, 2)
            pygame.draw.circle(core.screen, (104, 240, 255), (int(sx), int(sy)), r)
            pygame.draw.circle(core.screen, (230, 255, 255), (int(sx), int(sy)), max(2, r // 3))
        else:
            pygame.draw.circle(core.screen, (255, 181, 80), (int(sx), int(sy)), max(5, int(size * 0.25)))
            pygame.draw.circle(core.screen, (255, 240, 183), (int(sx), int(sy)), max(2, int(size * 0.12)))

        if dist < 3.4:
            label_color = (232, 215, 255) if dark else (45, 28, 59)
            text(core.screen, label, sx, sy + size * 0.52, TINY, label_color, center=True)

    sprites = [
        (*level["friend"], "friend", "THE WITNESS"),
        (*level["exit"], "exit", "MOON DOOR"),
        (core.enemy_x, core.enemy_y, "enemy", "THE HOLLOW")
    ]
    if core.level_index not in core.clues_found:
        sprites.append((*level["clue"], "clue", "CRYPT"))

    sprites.sort(key=lambda s: math.hypot(s[0] - core.player_x, s[1] - core.player_y), reverse=True)
    for sp in sprites:
        project(*sp)

    # Flash effect overlay
    if core.screen_flash > 0:
        flash_surf = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
        alpha = int(core.screen_flash * 200)
        flash_surf.fill((255, 250, 220, alpha))
        core.screen.blit(flash_surf, (0, 0))

    # Heartbeat vignette when threat is close
    dist_to_enemy = math.hypot(core.enemy_x - core.player_x, core.enemy_y - core.player_y)
    if dist_to_enemy < 4.0:
        vignette = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
        threat_alpha = int((1.0 - dist_to_enemy / 4.0) * 90 * (0.6 + 0.4 * math.sin(core.ambient_time * 9)))
        vignette.fill((160, 20, 40, threat_alpha))
        core.screen.blit(vignette, (0, 0))

    # Animated paintings and seasonal atmosphere
    draw_wall_paintings()
    draw_seasonal_effects()

    # HUD Panels
    panel(core.screen, (16, 14, 310, 132), 205)
    text(core.screen, level["name"], 30, 22, SMALL)

    # Health bar
    text(core.screen, f"HP   {core.health:03d}", 30, 46, TINY, (255, 120, 150))
    pygame.draw.rect(core.screen, (55, 30, 54), (95, 48, 195, 10), border_radius=4)
    pygame.draw.rect(core.screen, (232, 65, 112), (95, 48, int(195 * core.health / 100), 10), border_radius=4)

    # Stamina bar
    text(core.screen, f"STM  {int(core.stamina):03d}", 30, 68, TINY, (120, 230, 160))
    pygame.draw.rect(core.screen, (30, 55, 40), (95, 70, 195, 10), border_radius=4)
    pygame.draw.rect(core.screen, (60, 210, 130), (95, 70, int(195 * core.stamina / 100), 10), border_radius=4)

    # Lantern Oil bar
    text(core.screen, f"OIL  {int(core.lantern_oil):03d}", 30, 90, TINY, (245, 200, 100))
    pygame.draw.rect(core.screen, (55, 50, 30), (95, 92, 195, 10), border_radius=4)
    pygame.draw.rect(core.screen, (245, 190, 70), (95, 92, int(195 * core.lantern_oil / 100), 10), border_radius=4)

    text(core.screen, f"DIFF: {core.settings.get('difficulty','Normal').upper()}", 30, 116, TINY, (199, 170, 238))

    # Controls hints
    text(core.screen, "WASD: Move  •  SHIFT: Sprint  •  SPACE/RMB: Lantern Stun  •  J: Journal  •  Q: Quests  •  M: Radar  •  E: Interact",
         core.WIDTH // 2, core.HEIGHT - 22, TINY, (230, 220, 245), center=True)

    draw_minimap()

    if core.message_timer > 0:
        panel(core.screen, (core.WIDTH // 2 - 320, 91, 640, 45), 215)
        text(core.screen, core.message, core.WIDTH // 2, 113, SMALL, center=True)

def draw_3d_title_menu():
    """Animated pseudo-3D gothic title screen, rendered with native Pygame shapes."""
    t = core.ambient_time
    core.screen.fill((5, 5, 18))
    # Deep night gradient
    for y in range(0, core.HEIGHT, 4):
        k = y / max(1, core.HEIGHT)
        col = (int(7 + 10*k), int(7 + 2*k), int(22 + 18*k))
        pygame.draw.rect(core.screen, col, (0, y, core.WIDTH, 4))
    # Moon and slow halo
    mx, my = int(core.WIDTH*.78 + math.sin(t*.16)*12), int(core.HEIGHT*.20)
    for radius, alpha in ((86, 18), (68, 24), (54, 35)):
        glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (170, 135, 225, alpha), (radius, radius), radius)
        core.screen.blit(glow, (mx-radius, my-radius))
    pygame.draw.circle(core.screen, (235, 225, 255), (mx, my), 39)
    pygame.draw.circle(core.screen, (17, 12, 35), (mx+15, my-10), 35)
    # Distant 3D silhouettes and perspective fog
    ground = int(core.HEIGHT*.70)
    for layer in range(4):
        col = (13+layer*3, 10+layer*2, 30+layer*5)
        ybase = ground + layer*14
        for i in range(11):
            x = int(i*core.WIDTH/10 - 45 + math.sin(t*.12+layer)*8)
            w = 85 + layer*14
            h = 110 + ((i*53+layer*37) % 130) + layer*15
            pygame.draw.rect(core.screen, col, (x, ybase-h, w, h+120))
            pygame.draw.polygon(core.screen, col, [(x-10,ybase-h),(x+w//2,ybase-h-55-layer*5),(x+w+10,ybase-h)])
            for wy in range(ybase-h+22, ybase-12, 32):
                pygame.draw.arc(core.screen, (76, 44, 91), (x+w//2-10,wy,20,27), 0, math.pi, 2)
    # A framed glimpse of the candlelit dining hall introduces the manor's
    # lost banquet and uses the fourth supplied image in the title scene.
    try:
        card_w, card_h = int(core.WIDTH * 0.27), int(core.HEIGHT * 0.29)
        dining_card = pygame.transform.smoothscale(DINING_TEXTURE, (card_w, card_h))
        card_x, card_y = int(core.WIDTH * 0.055), int(core.HEIGHT * 0.34)
        pygame.draw.rect(core.screen, (105, 73, 43), (card_x - 7, card_y - 7, card_w + 14, card_h + 14), border_radius=5)
        pygame.draw.rect(core.screen, (222, 177, 102), (card_x - 4, card_y - 4, card_w + 8, card_h + 8), 2, border_radius=4)
        core.screen.blit(dining_card, (card_x, card_y))
        shade = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        shade.fill((8, 5, 18, 55))
        core.screen.blit(shade, (card_x, card_y))
    except pygame.error:
        pass

    # Central mansion, faux perspective walls, tower roofs
    cx = int(core.WIDTH*.72); base = int(core.HEIGHT*.78); mansion_w = int(min(core.WIDTH*.42, 460))
    left, right = cx-mansion_w//2, cx+mansion_w//2
    wall_top = int(core.HEIGHT*.31 + math.sin(t*.6)*2)
    pygame.draw.polygon(core.screen, (35, 22, 48), [(left,base),(left+40,wall_top+35),(right-35,wall_top),(right,base)])
    pygame.draw.polygon(core.screen, (18, 13, 30), [(left,base),(left+40,wall_top+35),(left+40,base-100)])
    pygame.draw.polygon(core.screen, (52, 29, 59), [(left+40,wall_top+35),(cx,wall_top-75),(right-35,wall_top)])
    pygame.draw.polygon(core.screen, (25, 17, 39), [(cx-48,wall_top+18),(cx,wall_top-100),(cx+48,wall_top+18)])
    pygame.draw.polygon(core.screen, (12, 10, 24), [(cx-30,base),(cx-30,base-112),(cx,base-145),(cx+30,base-112),(cx+30,base)])
    pygame.draw.arc(core.screen, (181, 115, 202), (cx-30,base-145,cx+30-(cx-30),90), 0, math.pi, 2)
    # Windows breathe with supernatural light
    for wx, wy in [(left+82,wall_top+90),(left+145,wall_top+110),(right-150,wall_top+82),(right-88,wall_top+100),(cx-82,wall_top+38),(cx+56,wall_top+38)]:
        pulse = int(28 + 25*(.5+.5*math.sin(t*2.0+wx)))
        pygame.draw.rect(core.screen, (pulse+35, 45, pulse+70), (wx,wy,22,36), border_radius=8)
        pygame.draw.line(core.screen, (120,84,145), (wx+11,wy),(wx+11,wy+36),1)
    # Perspective path towards the entrance
    pygame.draw.polygon(core.screen, (24, 18, 35), [(cx-34,base),(cx+34,base),(core.WIDTH*.93,core.HEIGHT),(core.WIDTH*.48,core.HEIGHT)])
    for i in range(1,8):
        yy = base + (core.HEIGHT-base)*(i/8)**1.8
        pygame.draw.line(core.screen, (73, 48, 82), (cx-34-(i*10),yy),(cx+34+(i*10),yy),1)
    # Floating rose petals with looping trajectories
    for i, seed in enumerate(menu_petal_seed):
        x = int((seed*core.WIDTH + math.sin(t*.65+i)*28) % core.WIDTH)
        y = int((seed*core.HEIGHT + t*(18+(i%5)*7)) % core.HEIGHT)
        r = 2 + (i%3)
        pygame.draw.ellipse(core.screen, (125+(i%3)*22, 48, 91+(i%4)*20), (x,y,r*2,r), 0)
    draw_seasonal_effects()
    # Vignette edges and cinematic title plaque
    vignette = pygame.Surface((core.WIDTH, core.HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (0,0,0,80), (0,0,core.WIDTH,core.HEIGHT), 24)
    core.screen.blit(vignette, (0,0))
    plaque = pygame.Rect(int(core.WIDTH*.055), int(core.HEIGHT*.12), int(core.WIDTH*.43), int(core.HEIGHT*.74))
    panel(core.screen, plaque, 238)
    # gold inner frame
    pygame.draw.rect(core.screen, (174,128,91), plaque.inflate(-14,-14), 1, border_radius=12)
    title_y = plaque.y + 48
    title_shadow = BIG.render("CRYPTIC ESCAPE", True, (65, 30, 72))
    title_front = BIG.render("CRYPTIC ESCAPE", True, (246, 222, 239))
    title_shadow_rect = title_shadow.get_rect(center=(plaque.centerx+3,title_y+4))
    title_front_rect = title_front.get_rect(center=(plaque.centerx,title_y))
    core.screen.blit(title_shadow,title_shadow_rect)
    core.screen.blit(title_front,title_front_rect)
    text(core.screen, "THE CURSED MANOR", plaque.centerx, title_y+45, FONT, (221,170,202), center=True)
    text(core.screen, "A 3D GOTHIC PUZZLE ADVENTURE", plaque.centerx, title_y+72, TINY, (187,170,210), center=True)
    labels = ["New Game", "Continue", "Mini Games & Tasks", "Customize Character", "Settings", "How to Play", "Quit"]
    rects = {}
    if core.HEIGHT < 620:
        start_y = plaque.y + 174
        for i,label in enumerate(labels):
            col, row = i % 2, i // 2
            r = pygame.Rect(plaque.centerx-172+col*180, start_y+row*43, 166, 35)
            rects[label] = draw_button(label, r, active=(i==0 and int(t*1.4)%5==0))
        text(core.screen, "WASD TO EXPLORE  •  E TO INTERACT  •  J FOR JOURNAL", plaque.centerx, plaque.bottom-12, TINY, (177,160,197), center=True)
    else:
        start_y = plaque.y + 145
        gap = min(51, max(38, (plaque.height - 190) // 6))
        for i,label in enumerate(labels):
            r = pygame.Rect(plaque.centerx-145, start_y+i*gap, 290, 38)
            rects[label] = draw_button(label, r, active=(i==0 and int(t*1.4)%5==0))
        text(core.screen, "WASD TO EXPLORE  •  E TO INTERACT  •  J FOR JOURNAL", plaque.centerx, plaque.bottom-26, TINY, (177,160,197), center=True)
    text(core.screen, SEASON_THEMES.get(core.active_theme, SEASON_THEMES["Haunted"])["subtitle"], int(core.WIDTH*.74), int(core.HEIGHT*.91), SMALL, (229,190,215), center=True)
    return rects
