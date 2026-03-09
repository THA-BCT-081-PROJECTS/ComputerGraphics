import pygame
import math
import random

from models import Player
from maps   import ALL_MAPS, NeonCityMap, LavaDungeonMap, IceFortressMap
from buffs  import BUFF_DEFS, BUFF_BY_ID, random_buff_id

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🏆  TROPHY TAG")
clock  = pygame.time.Clock()

try:
    from pygame import mixer
    mixer.music.load("assets/background.wav")
    mixer.music.play(-1)
except:
    pass

# ── Constants ─────────────────────────────────────────────────────────────────
RADIUS         = 13           # Character Radius
WIN_SCORE      = 10
STEAL_CD       = 1.8
BUFF_INTERVAL  = 9.0
MAX_BUFFS      = 3
TROPHY_BOB     = 2.5
HUD_H          = 56           # compact HUD

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_SM  = pygame.font.SysFont("consolas", 13, bold=True)
F_MD  = pygame.font.SysFont("consolas", 16, bold=True)
F_LG  = pygame.font.SysFont("consolas", 22, bold=True)
F_XL  = pygame.font.SysFont("consolas", 42, bold=True)
F_XXL = pygame.font.SysFont("consolas", 64, bold=True)
try:
    F_EMO    = pygame.font.SysFont("segoe ui emoji", 20)
    F_EMO_LG = pygame.font.SysFont("segoe ui emoji", 30)
except:
    F_EMO = F_MD; F_EMO_LG = F_LG

# ── Palette ───────────────────────────────────────────────────────────────────
P_COLORS   = [(255, 50, 180), (0, 230, 255), (255, 220, 0)]
P_NAMES    = ["P1", "P2", "P3"]
P_CONTROLS = ["WASD", "ARROWS", "NUM 8/4/6"]
GOLD       = (255, 200, 40)
WHITE      = (230, 230, 240)
DIM        = (120, 110, 150)
HP_GREEN   = (60, 220, 80)
HP_YELLOW  = (240, 200, 0)
HP_RED     = (255, 50, 40)

# ── Game states ───────────────────────────────────────────────────────────────
S_COUNT   = "count"
S_MAP     = "map"
S_PLAY    = "play"
S_WIN     = "win"


# ═══════════════════════════════════════════════════════════════════════════════
#  DRAWING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def glow(surface, color, pos, radius, alpha=70):
    r   = max(1, int(radius))
    buf = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
    for gr in range(r * 3, r, -2):
        a = int(alpha * (1.0 - gr / (r * 3)))
        pygame.draw.circle(buf, (*color, a), (r * 3, r * 3), gr)
    surface.blit(buf, (int(pos[0]) - r * 3, int(pos[1]) - r * 3))


def centered(surface, text, font, color, y, shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surface.blit(s, (W // 2 - s.get_width() // 2 + 2, y + 2))
    t = font.render(text, True, color)
    surface.blit(t, (W // 2 - t.get_width() // 2, y))
    return t.get_height()


def draw_hp_bar(surface, x, y, w, hp, max_hp):
    ratio = max(0.0, hp / max_hp)
    bg    = pygame.Rect(x, y, w, 7)
    fg    = pygame.Rect(x, y, int(w * ratio), 7)
    pygame.draw.rect(surface, (30, 20, 40), bg, border_radius=3)
    col   = HP_GREEN if ratio > 0.5 else (HP_YELLOW if ratio > 0.25 else HP_RED)
    if fg.width > 0:
        pygame.draw.rect(surface, col, fg, border_radius=3)
    pygame.draw.rect(surface, (80, 70, 100), bg, 1, border_radius=3)


def draw_trophy(surface, x, y, scale=1.0, time=0.0):
    bob  = math.sin(time * TROPHY_BOB) * 5
    y    = int(y + bob)
    s    = scale
    col  = GOLD
    dark = (160, 110, 0)
    shne = (255, 245, 150)

    glow(surface, GOLD, (x, y), int(28 * s), alpha=85)

    # Cup body (trapezoid)
    cup = [
        (x - int(18 * s), y - int(22 * s)),
        (x + int(18 * s), y - int(22 * s)),
        (x + int(13 * s), y + int(7 * s)),
        (x - int(13 * s), y + int(7 * s)),
    ]
    pygame.draw.polygon(surface, col,  cup)
    pygame.draw.polygon(surface, dark, cup, 2)

    # Handles
    hl = pygame.Rect(x - int(27 * s), y - int(16 * s), int(13 * s), int(18 * s))
    hr = pygame.Rect(x + int(14 * s), y - int(16 * s), int(13 * s), int(18 * s))
    for r in [hl, hr]:
        pygame.draw.arc(surface, col,  r, math.pi * 0.2, math.pi * 1.8, max(1, int(5 * s)))
        pygame.draw.arc(surface, dark, r, math.pi * 0.2, math.pi * 1.8, max(1, int(3 * s)))

    # Stem
    st = pygame.Rect(x - int(5 * s), y + int(6 * s), int(10 * s), int(11 * s))
    pygame.draw.rect(surface, col,  st)
    pygame.draw.rect(surface, dark, st, 1)

    # Base
    bs = pygame.Rect(x - int(15 * s), y + int(17 * s), int(30 * s), int(7 * s))
    pygame.draw.rect(surface, col,  bs, border_radius=3)
    pygame.draw.rect(surface, dark, bs, 1)

    # Shine
    pygame.draw.circle(surface, shne, (x - int(5 * s), y - int(14 * s)), max(1, int(4 * s)))


def draw_buff_pickup(surface, item, time):
    bx, by = int(item["x"]), int(item["y"])
    col    = item["color"]
    pulse  = abs(math.sin(time * 3)) * 8
    r      = int(20 + pulse)
    glow(surface, col, (bx, by), r, alpha=65)
    pygame.draw.circle(surface, col, (bx, by), r, 3)
    ico = F_EMO.render(item["icon"], True, WHITE)
    surface.blit(ico, (bx - ico.get_width() // 2, by - ico.get_height() // 2))
    lbl = F_SM.render(item["label"], True, col)
    surface.blit(lbl, (bx - lbl.get_width() // 2, by + r + 4))


def draw_avatar(surface, player, base_color, label, has_trophy, time, num_players):
    dr   = player.display_radius()
    x, y = int(player.pos.x), int(player.pos.y)

    body_alpha = 140 if player.is_ghost() else 255

    # Invincibility flash
    if player.invincible > 0 and int(player.invincible * 10) % 2 == 0:
        body_alpha = max(40, body_alpha - 160)

    dw, dh = player.get_draw_wh()

    # Auras
    if player.has_buff("shield"):
        glow(surface, (180, 50, 255), (x, y), dr + 14, alpha=55)
        pygame.draw.circle(surface, (180, 50, 255), (x, y), dr + 14, 2)
    if has_trophy:
        glow(surface, GOLD, (x, y), dr + 10, alpha=60)
        pygame.draw.circle(surface, GOLD, (x, y), dr + 10, 2)

    # Blend body color toward active buff colors
    color = base_color
    for bid in player.buffs:
        if bid in BUFF_BY_ID:
            bc    = BUFF_BY_ID[bid]["color"]
            color = tuple(int((c * 2 + bc[i]) // 3) for i, c in enumerate(color))

    # Body ellipse surface
    sw, sh = dw + 6, dh + 6
    surf   = pygame.Surface((sw, sh), pygame.SRCALPHA)
    cx, cy = sw // 2, sh // 2

    # Glow halo
    glow(surf, color, (cx, cy), dr, alpha=50)

    # Main ellipse
    pygame.draw.ellipse(surf, (*color, body_alpha),
                        pygame.Rect(3, 3, dw, dh))

    # Shine highlight (top-left quadrant)
    shine_col = tuple(min(255, c + 90) for c in color)
    shine_x   = cx - max(2, dw // 5)
    shine_y   = cy - max(2, dh // 5)
    shine_r   = max(2, min(dw, dh) // 4)
    pygame.draw.circle(surf, (*shine_col, body_alpha), (shine_x, shine_y), shine_r)

    # Eyes — positioned in upper half of ellipse, scale with size
    blink   = int(time * 2.6) % 24 != 0
    eye_col = (15, 8, 28)
    eo      = max(4, dw // 5)           # eye offset from center
    ey      = cy - max(2, dh // 6)     # eye Y — upper portion
    er      = max(2, min(dw, dh) // 7) # eye radius

    if blink:
        pygame.draw.circle(surf, eye_col, (cx - eo, ey), er)
        pygame.draw.circle(surf, eye_col, (cx + eo, ey), er)
        # Whites
        pygame.draw.circle(surf, (255, 255, 255, 255), (cx - eo + 1, ey - 1), max(1, er // 2))
        pygame.draw.circle(surf, (255, 255, 255, 255), (cx + eo + 1, ey - 1), max(1, er // 2))
    else:
        # Closed eyes (blink)
        pygame.draw.line(surf, eye_col, (cx - eo - er, ey), (cx - eo + er, ey), 2)
        pygame.draw.line(surf, eye_col, (cx + eo - er, ey), (cx + eo + er, ey), 2)

    # Mouth — excited if holding trophy, flat/frown otherwise
    my  = cy + max(2, dh // 5)
    mw  = max(8, dw // 3)
    mr  = pygame.Rect(cx - mw // 2, my, mw, max(5, dh // 6))
    if has_trophy:
        pygame.draw.arc(surf, eye_col, mr, 0, math.pi, 2)       # big smile
    elif player.hp < 30:
        pygame.draw.arc(surf, eye_col, mr, math.pi, 2 * math.pi, 2)  # frown
    else:
        mouth_y = my + mr.height // 2
        pygame.draw.line(surf, eye_col, (cx - mw // 2, mouth_y),
                         (cx + mw // 2, mouth_y), 2)             # flat

    surface.blit(surf, (x - sw // 2, y - sh // 2))

    # Label above avatar (tight — only show when not too cramped)
    lbl_col = GOLD if has_trophy else base_color
    lbl_str = f"🏆{label}" if has_trophy else label
    lbl_s   = F_SM.render(lbl_str, True, lbl_col)
    lbl_y   = y - dh // 2 - lbl_s.get_height() - 2
    surface.blit(lbl_s, (x - lbl_s.get_width() // 2, lbl_y))

    # Buff icons row above label (only if there's room)
    icons = [BUFF_BY_ID[bid]["icon"] for bid in player.buffs if bid in BUFF_BY_ID][:4]
    if icons:
        ico_s = F_SM.render(" ".join(icons), True, (200, 200, 255))
        surface.blit(ico_s, (x - ico_s.get_width() // 2, lbl_y - ico_s.get_height() - 1))

    # HP bar directly below avatar
    bar_w = max(28, dw + 6)
    draw_hp_bar(surface, x - bar_w // 2, y + dh // 2 + 3, bar_w, player.hp, player.MAX_HP)


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud(surface, players, scores, map_obj, time_elapsed, num_players):
    # Compact bar: 56px total
    bar = pygame.Surface((W, HUD_H), pygame.SRCALPHA)
    bar.fill((6, 4, 20, 225))
    surface.blit(bar, (0, 0))
    # Bottom separator line
    pygame.draw.line(surface, (*map_obj.accent, 120), (0, HUD_H), (W, HUD_H), 1)

    # Reserve right edge for timer/map (120px)
    panel_w = (W - 120) // num_players

    for i in range(num_players):
        xo  = i * panel_w + 10
        col = P_COLORS[i]
        p   = players[i]

        # Trophy holder highlight
        if p.has_trophy:
            hl = pygame.Surface((panel_w - 4, HUD_H - 2), pygame.SRCALPHA)
            pygame.draw.rect(hl, (*GOLD, 25), hl.get_rect(), border_radius=5)
            surface.blit(hl, (xo - 2, 1))

        # Row 1 (y=4): name + score pips
        name_str = f"{'🏆' if p.has_trophy else '  '}P{i+1}"
        ns = F_SM.render(name_str, True, GOLD if p.has_trophy else col)
        surface.blit(ns, (xo, 4))

        # Score pips — compact, 12px each
        pip_x0 = xo + 46
        for pip in range(WIN_SCORE):
            filled = pip < scores[i]
            pygame.draw.circle(surface, col if filled else (40, 35, 60),
                               (pip_x0 + pip * 13, 11), 5, 0 if filled else 1)

        # Row 2 (y=22): HP bar full width of panel
        draw_hp_bar(surface, xo, 22, panel_w - 16, p.hp, p.MAX_HP)

        # Row 3 (y=34): controls + buff icons
        ctrl = F_SM.render(P_CONTROLS[i], True, (80, 75, 110))
        surface.blit(ctrl, (xo, 34))
        icons = [BUFF_BY_ID[bid]["icon"] for bid in p.buffs if bid in BUFF_BY_ID][:3]
        if icons:
            ico_s = F_SM.render(" ".join(icons), True, (180, 180, 255))
            surface.blit(ico_s, (xo + 70, 34))

        # Separator between panels
        if i < num_players - 1:
            pygame.draw.line(surface, (50, 44, 80),
                             (xo + panel_w - 6, 4),
                             (xo + panel_w - 6, HUD_H - 4), 1)

    # Right edge: timer + map name
    rx = W - 115
    mins = int(time_elapsed) // 60
    secs = int(time_elapsed) % 60
    ts   = F_MD.render(f"{mins:02}:{secs:02}", True, WHITE)
    surface.blit(ts, (rx, 6))
    mn = F_SM.render(map_obj.name, True, map_obj.accent)
    surface.blit(mn, (rx, 28))
    hint_t = F_SM.render("ESC=menu", True, (60, 55, 90))
    surface.blit(hint_t, (rx, 42))

    map_obj.draw_secret_hint(surface, F_SM)


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREEN: PLAYER COUNT SELECT
# ═══════════════════════════════════════════════════════════════════════════════

def draw_count_select(surface, selected, time):
    surface.fill((6, 4, 20))

    # Animated title glow
    pulse = abs(math.sin(time * 1.8)) * 30
    centered(surface, "🏆  TROPHY TAG", F_XXL, (255, int(200 + pulse), 40), 60)
    centered(surface, "Steal the trophy  •  First to 10 steals wins!", F_MD, DIM, 148)
    centered(surface, "HOW MANY PLAYERS?", F_LG, WHITE, 200)

    options = [
        ("2  PLAYERS", "Two rivals, one trophy"),
        ("3  PLAYERS", "Three players, maximum chaos"),
    ]

    card_w, card_h = 340, 180
    gap = 60
    total = card_w * 2 + gap
    sx   = (W - total) // 2
    y0   = 250

    for i, (title, sub) in enumerate(options):
        x      = sx + i * (card_w + gap)
        is_sel = (i + 2 == selected)   # selected=2 or 3
        accent = (255, 200, 40) if is_sel else (60, 50, 90)

        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        if is_sel:
            pygame.draw.rect(card, (255, 200, 40, 35), card.get_rect(), border_radius=14)
            pygame.draw.rect(card, (255, 200, 40, 200), card.get_rect(), 3, border_radius=14)
        else:
            pygame.draw.rect(card, (20, 16, 40, 180), card.get_rect(), border_radius=14)
            pygame.draw.rect(card, (60, 50, 90, 140), card.get_rect(), 2, border_radius=14)
        surface.blit(card, (x, y0))

        # Big number
        num_s = F_XXL.render(str(i + 2), True, GOLD if is_sel else DIM)
        surface.blit(num_s, (x + card_w // 2 - num_s.get_width() // 2, y0 + 20))

        # Title
        ts = F_LG.render(title, True, WHITE if is_sel else DIM)
        surface.blit(ts, (x + card_w // 2 - ts.get_width() // 2, y0 + 100))

        # Sub
        ss = F_SM.render(sub, True, DIM)
        surface.blit(ss, (x + card_w // 2 - ss.get_width() // 2, y0 + 130))

        if is_sel:
            bob = int(abs(math.sin(time * 3)) * 6)
            ar  = F_LG.render("▼  SELECT", True, GOLD)
            surface.blit(ar, (x + card_w // 2 - ar.get_width() // 2, y0 + card_h + 10 + bob))

    # Controls
    centered(surface, "← →  choose     ENTER  confirm     ESC  quit", F_MD, DIM, H - 44)

    # Preview avatars
    for i in range(max(selected, 2)):
        px    = W // 2 + (i - (max(selected, 2) - 1) / 2.0) * 100
        py    = 490
        col   = P_COLORS[i]
        r     = 26
        glow(surface, col, (int(px), int(py)), r, alpha=60)
        pygame.draw.circle(surface, col, (int(px), int(py)), r)
        shine = tuple(min(255, c + 90) for c in col)
        pygame.draw.circle(surface, shine, (int(px) - 7, int(py) - 8), 9)
        eye_y = int(py) - 6
        pygame.draw.circle(surface, (15, 8, 28), (int(px) - 8, eye_y), 4)
        pygame.draw.circle(surface, (15, 8, 28), (int(px) + 8, eye_y), 4)
        label = F_SM.render(P_NAMES[i], True, col)
        surface.blit(label, (int(px) - label.get_width() // 2, int(py) + r + 6))


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREEN: MAP SELECT
# ═══════════════════════════════════════════════════════════════════════════════

MAP_INFO = [
    {
        "cls":     NeonCityMap,
        "name":    "NEON CITY",
        "sub":     "The Grid Never Sleeps",
        "lines":   ["Normal gravity", "Platforms pulse with neon glow", "Scan-lines fill the sky"],
        "secret":  "⚡ Grid Glitch: random impulse blasts + damage",
        "accent":  (180, 60, 255),
        "icon":    "🌆",
    },
    {
        "cls":     LavaDungeonMap,
        "name":    "LAVA DUNGEON",
        "sub":     "Mind the Floor",
        "lines":   ["High gravity", "Lava floor deals constant damage", "Embers glow on platforms"],
        "secret":  "🌋 Lava Surge: floor rises, instant damage",
        "accent":  (255, 80, 0),
        "icon":    "🌋",
    },
    {
        "cls":     IceFortressMap,
        "name":    "ICE FORTRESS",
        "sub":     "Slippery When Frozen",
        "lines":   ["Low gravity", "Ice floors = almost no friction", "Icicles fall if you linger"],
        "secret":  "❄ Blizzard: leftward wind + frostbite damage",
        "accent":  (100, 200, 255),
        "icon":    "🏔",
    },
]


def draw_map_select(surface, selected, time):
    surface.fill((6, 4, 20))
    centered(surface, "SELECT ARENA", F_XL, GOLD, 26)
    centered(surface, "Each map has unique physics, hazards and a SECRET event!", F_MD, DIM, 90)

    card_w, card_h = 360, 380
    gap   = 26
    total = card_w * 3 + gap * 2
    sx    = (W - total) // 2
    y0    = 125

    for i, mi in enumerate(MAP_INFO):
        x      = sx + i * (card_w + gap)
        is_sel = (i == selected)
        accent = mi["accent"]

        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        if is_sel:
            pygame.draw.rect(card, (*accent, 35), card.get_rect(), border_radius=14)
            pygame.draw.rect(card, (*accent, 210), card.get_rect(), 3, border_radius=14)
        else:
            pygame.draw.rect(card, (18, 14, 36, 180), card.get_rect(), border_radius=14)
            pygame.draw.rect(card, (55, 45, 90, 140), card.get_rect(), 2, border_radius=14)
        surface.blit(card, (x, y0))

        # Icon
        ico = F_EMO_LG.render(mi["icon"], True, WHITE)
        surface.blit(ico, (x + card_w // 2 - ico.get_width() // 2, y0 + 14))

        # Name
        ns = F_LG.render(mi["name"], True, accent if is_sel else WHITE)
        surface.blit(ns, (x + card_w // 2 - ns.get_width() // 2, y0 + 66))

        # Subtitle
        ss = F_SM.render(mi["sub"], True, DIM)
        surface.blit(ss, (x + card_w // 2 - ss.get_width() // 2, y0 + 96))

        # Feature lines
        for li, line in enumerate(mi["lines"]):
            ls = F_SM.render(f"• {line}", True, (170, 160, 205))
            surface.blit(ls, (x + 18, y0 + 126 + li * 22))

        # Secret
        sec = F_SM.render(mi["secret"], True, accent if is_sel else DIM)
        surface.blit(sec, (x + card_w // 2 - sec.get_width() // 2, y0 + 260))

        # Selected tick
        if is_sel:
            bob = int(abs(math.sin(time * 3)) * 5)
            sel = F_LG.render("▶ SELECTED ◀", True, accent)
            surface.blit(sel, (x + card_w // 2 - sel.get_width() // 2, y0 + 312 + bob))

    centered(surface, "← →  choose map     ENTER  start     ESC  back", F_MD, DIM, H - 34)


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREEN: WIN
# ═══════════════════════════════════════════════════════════════════════════════

def spawn_confetti(n=140):
    pts = []
    for _ in range(n):
        col = random.choice(P_COLORS + [(255, 200, 40), (255, 255, 255)])
        pts.append([
            random.uniform(0, W), random.uniform(-60, H // 2),
            random.uniform(-90, 90), random.uniform(70, 240),
            random.uniform(2.5, 5.0), 5.0, col,
        ])
    return pts


def tick_particles(pts, dt):
    alive = []
    for p in pts:
        p[0] += p[2] * dt
        p[1] += p[3] * dt
        p[4] -= dt
        if p[4] > 0:
            alive.append(p)
    return alive


def draw_particles(surface, pts):
    for p in pts:
        ratio = max(0, p[4] / p[5])
        alpha = int(255 * ratio)
        r     = max(1, int(6 * ratio))
        s     = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p[6], alpha), (r + 1, r + 1), r)
        surface.blit(s, (int(p[0]) - r - 1, int(p[1]) - r - 1))


def draw_win(surface, winner_idx, scores, time, confetti, num_players):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 185))
    surface.blit(ov, (0, 0))
    draw_particles(surface, confetti)

    col  = P_COLORS[winner_idx]
    name = f"PLAYER {winner_idx + 1}"
    pulse = abs(math.sin(time * 2.5)) * 8

    draw_trophy(surface, W // 2, H // 2 - 120, scale=2.2, time=time)
    centered(surface, f"🎉  {name}  WINS!  🎉", F_XXL, col, H // 2 + 20 + int(pulse))
    centered(surface, f"Trophy steals: {scores[winner_idx]}", F_LG, GOLD, H // 2 + 92)

    for i in range(num_players):
        sc = F_MD.render(f"P{i+1}: {scores[i]} steals", True, P_COLORS[i])
        surface.blit(sc, (W // 2 - sc.get_width() // 2, H // 2 + 130 + i * 28))

    centered(surface, "SPACE — replay same map     M — map select     ESC — quit",
             F_MD, DIM, H - 40)


# ═══════════════════════════════════════════════════════════════════════════════
#  GAME HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def make_players(num):
    xpos = [W * 0.2, W * 0.5, W * 0.8]
    if num == 2:
        xpos = [W * 0.25, W * 0.75]
    players = []
    for i in range(num):
        p = Player(xpos[i], H * 0.5, RADIUS, P_COLORS[i], player_id=i)
        players.append(p)
    return players


def spawn_buff(platforms):
    bid  = random_buff_id()
    bdef = BUFF_BY_ID[bid]
    plat = random.choice(platforms[1:])
    x    = random.randint(plat.x + 24, max(plat.x + 25, plat.right - 24))
    y    = plat.y - 30
    return {"x": x, "y": y, "id": bid,
            "color": bdef["color"], "icon": bdef["icon"],
            "label": bdef["label"], "duration": bdef["duration"]}


def burst(pts, pos, color, n=24):
    for _ in range(n):
        a = random.uniform(0, math.pi * 2)
        spd = random.uniform(90, 260)
        life = random.uniform(0.4, 0.9)
        pts.append([pos.x, pos.y, math.cos(a) * spd, math.sin(a) * spd, life, life, color])


def check_steal(players, holder_idx, steal_timer, dt):
    steal_timer -= dt
    if steal_timer > 0:
        return holder_idx, steal_timer
    holder = players[holder_idx]
    if holder.has_buff("shield"):
        return holder_idx, steal_timer
    for i, p in enumerate(players):
        if i == holder_idx:
            continue
        dist = holder.pos.distance_to(p.pos)
        sr   = holder.display_radius() + p.display_radius() + 6
        if dist < sr:
            return i, STEAL_CD
    return holder_idx, steal_timer


def handle_magnet(players, holder_idx, dt):
    holder = players[holder_idx]
    for i, p in enumerate(players):
        if i == holder_idx or not p.has_buff("magnet"):
            continue
        diff  = p.pos - holder.pos
        dist  = max(1.0, diff.length())
        force = min(320.0, 28000.0 / (dist * dist + 1))
        holder.velocity += diff.normalize() * force * dt


def start_game(map_cls, num_players):
    current_map  = map_cls()
    players      = make_players(num_players)
    scores       = [0] * num_players
    holder_idx   = 0
    players[0].has_trophy = True
    steal_timer  = STEAL_CD
    buff_items   = []
    buff_timer   = BUFF_INTERVAL
    particles    = []
    time_elapsed = 0.0
    return current_map, players, scores, holder_idx, steal_timer, buff_items, buff_timer, particles, time_elapsed


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    state        = S_COUNT
    ui_time      = 0.0
    count_sel    = 2       # 2 or 3 players
    map_sel      = 0
    num_players  = 2

    current_map  = None
    players      = []
    scores       = []
    holder_idx   = 0
    steal_timer  = 0.0
    buff_items   = []
    buff_timer   = BUFF_INTERVAL
    particles    = []
    time_elapsed = 0.0
    winner_idx   = -1
    confetti     = []
    win_time     = 0.0
    dt           = 0.0

    running = True
    while running:
        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                k = event.key

                if k == pygame.K_ESCAPE:
                    if   state == S_PLAY:  state = S_MAP
                    elif state == S_MAP:   state = S_COUNT
                    elif state == S_WIN:   state = S_COUNT
                    else:                  running = False

                # ── Count select ──
                if state == S_COUNT:
                    if k in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                        count_sel = 5 - count_sel   # toggle 2 ↔ 3
                    if k in (pygame.K_RETURN, pygame.K_SPACE):
                        num_players = count_sel
                        state       = S_MAP

                # ── Map select ──
                elif state == S_MAP:
                    if k in (pygame.K_LEFT, pygame.K_a):
                        map_sel = (map_sel - 1) % len(ALL_MAPS)
                    if k in (pygame.K_RIGHT, pygame.K_d):
                        map_sel = (map_sel + 1) % len(ALL_MAPS)
                    if k in (pygame.K_RETURN, pygame.K_SPACE):
                        (current_map, players, scores, holder_idx,
                         steal_timer, buff_items, buff_timer,
                         particles, time_elapsed) = start_game(ALL_MAPS[map_sel], num_players)
                        state = S_PLAY

                # ── Win screen ──
                elif state == S_WIN:
                    if k == pygame.K_SPACE:
                        (current_map, players, scores, holder_idx,
                         steal_timer, buff_items, buff_timer,
                         particles, time_elapsed) = start_game(type(current_map), num_players)
                        state = S_PLAY
                    if k == pygame.K_m:
                        state = S_MAP

        ui_time += dt

        # ══════════════════════════════════════════════════════════════════════
        if state == S_COUNT:
            draw_count_select(screen, count_sel, ui_time)

        # ══════════════════════════════════════════════════════════════════════
        elif state == S_MAP:
            draw_map_select(screen, map_sel, ui_time)

        # ══════════════════════════════════════════════════════════════════════
        elif state == S_PLAY:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:     players[0].jump()
            if keys[pygame.K_a]:     players[0].move_left(dt)
            if keys[pygame.K_d]:     players[0].move_right(dt)
            if num_players >= 2:
                if keys[pygame.K_UP]:    players[1].jump()
                if keys[pygame.K_LEFT]:  players[1].move_left(dt)
                if keys[pygame.K_RIGHT]: players[1].move_right(dt)
            if num_players >= 3:
                if keys[pygame.K_KP8]:   players[2].jump()
                if keys[pygame.K_KP4]:   players[2].move_left(dt)
                if keys[pygame.K_KP6]:   players[2].move_right(dt)

            # Physics
            for p in players:
                p.update(dt, current_map.platforms,
                         current_map.gravity, W, H)
            current_map.update(dt, players)

            # Respawn dead players — score penalty + drop trophy
            for pi, p in enumerate(players):
                if p.is_dead():
                    # -1 score penalty, floor at 0
                    if scores[pi] > 0:
                        scores[pi] -= 1
                    burst(particles, p.pos, P_COLORS[pi], n=30)
                    # Respawn at top
                    p.hp        = p.MAX_HP
                    p.pos.x     = random.uniform(W * 0.25, W * 0.75)
                    p.pos.y     = HUD_H + 50
                    p.velocity  = pygame.Vector2(0, 0)
                    p.invincible = 2.5
                    p.buffs.clear()
                    # Drop trophy to a random live player
                    if p.has_trophy:
                        p.has_trophy = False
                        alive        = [j for j in range(num_players) if j != pi]
                        holder_idx   = random.choice(alive)
                        for pp in players:
                            pp.has_trophy = False
                        players[holder_idx].has_trophy = True
                        steal_timer = STEAL_CD

            handle_magnet(players, holder_idx, dt)

            # Steal
            prev      = holder_idx
            holder_idx, steal_timer = check_steal(players, holder_idx, steal_timer, dt)
            if holder_idx != prev:
                scores[holder_idx] += 1
                players[prev].has_trophy         = False
                players[holder_idx].has_trophy   = True
                burst(particles, players[holder_idx].pos, GOLD, n=32)
                burst(particles, players[holder_idx].pos, P_COLORS[holder_idx], n=20)
                if scores[holder_idx] >= WIN_SCORE:
                    winner_idx = holder_idx
                    confetti   = spawn_confetti(150)
                    win_time   = 0.0
                    state      = S_WIN

            # Buff spawn
            buff_timer -= dt
            if buff_timer <= 0 and len(buff_items) < MAX_BUFFS:
                buff_items.append(spawn_buff(current_map.platforms))
                buff_timer = BUFF_INTERVAL

            # Buff pickup
            for p in players:
                for item in buff_items[:]:
                    if p.pos.distance_to(pygame.Vector2(item["x"], item["y"])) < p.display_radius() + 22:
                        p.apply_buff(item["id"], item["duration"])
                        burst(particles, pygame.Vector2(item["x"], item["y"]), item["color"], n=16)
                        buff_items.remove(item)

            particles = tick_particles(particles, dt)

            # ── Draw ──────────────────────────────────────────────────────────
            current_map.draw_bg(screen)
            current_map.draw_platforms(screen)

            for item in buff_items:
                draw_buff_pickup(screen, item, time_elapsed)

            # Trophy floating above holder
            h_player = players[holder_idx]
            draw_trophy(screen,
                        int(h_player.pos.x),
                        int(h_player.pos.y) - h_player.display_radius() - 52,
                        scale=0.8, time=time_elapsed)

            for i, p in enumerate(players):
                draw_avatar(screen, p, P_COLORS[i], P_NAMES[i],
                            p.has_trophy, time_elapsed, num_players)

            draw_particles(screen, particles)
            current_map.draw_foreground(screen)

            # Map announcement (secret triggered etc.)
            current_map.draw_announcement(screen, F_XL)

            draw_hud(screen, players, scores, current_map, time_elapsed, num_players)

            time_elapsed += dt

        # ══════════════════════════════════════════════════════════════════════
        elif state == S_WIN:
            win_time += dt
            confetti  = tick_particles(confetti, dt)
            if current_map:
                current_map.draw_bg(screen)
                current_map.draw_platforms(screen)
            draw_win(screen, winner_idx, scores, win_time, confetti, num_players)

        tick = clock.tick(60)
        dt   = tick / 1000.0
        pygame.display.flip()

    pygame.quit()


main()