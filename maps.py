import pygame
import math
import random

W = 1280
H = 720

# HUD = 56px. Playfield: TOP=60 -> BOT=H-6 -> ~654px vertical play.
TOP = 60
BOT = H - 6


def _plat(x, y, w, h=10):
    """Thinner platforms to reduce visual bulk."""
    return pygame.Rect(x, y, w, h)


class MapBase:
    name          = "Base"
    subtitle      = ""
    gravity       = 600
    bg_color      = (8, 6, 18)
    platform_col  = (60, 50, 120)
    platform_glow = (100, 80, 200)
    grid_color    = (20, 16, 40)
    accent        = (100, 80, 200)
    secret_hint   = ""

    def __init__(self):
        self.platforms         = self._build_platforms()
        self.time              = 0.0
        self.particles         = []
        self.secret_timer      = 0.0
        self.secret_cooldown   = 30.0
        self._secret_triggered = False
        self.announcement      = ""      # shown big on screen for a moment
        self.announcement_t    = 0.0

    def _build_platforms(self): return []

    def announce(self, text, duration=2.5):
        self.announcement   = text
        self.announcement_t = duration

    def update(self, dt, players):
        self.time         += dt
        self._tick_particles(dt)
        self.secret_timer += dt
        if self.announcement_t > 0:
            self.announcement_t -= dt
        if self.secret_timer >= self.secret_cooldown and not self._secret_triggered:
            self._trigger_secret(players)
            self._secret_triggered = True
            self.secret_timer      = 0.0
        elif self.secret_timer < self.secret_cooldown:
            self._secret_triggered = False

    def _trigger_secret(self, players): pass

    # ── Drawing ───────────────────────────────────────────────────────────────
    def draw_bg(self, surface):
        surface.fill(self.bg_color)
        self._draw_grid(surface)

    def draw_platforms(self, surface):
        for plat in self.platforms:
            self._draw_platform(surface, plat)

    def draw_foreground(self, surface):
        self._draw_particles(surface)

    def draw_announcement(self, surface, font):
        if self.announcement_t > 0:
            alpha = min(255, int(255 * self.announcement_t))
            s     = font.render(self.announcement, True, (*self.accent,))
            surface.blit(s, (W // 2 - s.get_width() // 2, H // 2 - 30))

    def draw_secret_hint(self, surface, font):
        if not self.secret_hint:
            return
        progress  = self.secret_timer / self.secret_cooldown
        flash     = abs(math.sin(self.time * (1.5 + progress * 3)))
        col_alpha = int(80 + 175 * flash) if progress > 0.8 else int(60 + 60 * flash)
        col       = tuple(min(255, int(c * (0.5 + 0.5 * flash))) for c in self.accent)
        s         = font.render(f"✦  {self.secret_hint}  ✦", True, col)
        surface.blit(s, (W // 2 - s.get_width() // 2, H - 26))

    def _draw_grid(self, surface):
        for x in range(0, W, 80):
            pygame.draw.line(surface, self.grid_color, (x, 0), (x, H), 1)
        for y in range(TOP, H, 60):
            pygame.draw.line(surface, self.grid_color, (0, y), (W, y), 1)

    def _draw_platform(self, surface, plat, color=None, glow=None):
        col  = color or self.platform_col
        glw  = glow  or self.platform_glow
        gr   = plat.inflate(10, 10)
        gs   = pygame.Surface((max(1, gr.width), max(1, gr.height)), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*glw, 55), gs.get_rect(), border_radius=5)
        surface.blit(gs, gr.topleft)
        pygame.draw.rect(surface, col, plat, border_radius=4)
        hl = pygame.Rect(plat.x + 3, plat.y + 1, max(4, plat.width - 6), 3)
        pygame.draw.rect(surface, glw, hl, border_radius=2)

    def _spawn_particle(self, x, y, vx, vy, life, color):
        self.particles.append([float(x), float(y), vx, vy, life, life, color])

    def _tick_particles(self, dt):
        self.particles = [p for p in self.particles if p[4] > 0]
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[4] -= dt

    def _draw_particles(self, surface):
        for p in self.particles:
            ratio = max(0.0, p[4] / p[5])
            alpha = int(255 * ratio)
            r     = max(1, int(5 * ratio))
            s     = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p[6], alpha), (r + 1, r + 1), r)
            surface.blit(s, (int(p[0]) - r - 1, int(p[1]) - r - 1))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAP 1 — NEON CITY
#  Unique: animated scan-lines, pulsing platform glow, GLITCH STORM secret
#  (blasts all players with random impulses + screen flicker)
# ═══════════════════════════════════════════════════════════════════════════════

class NeonCityMap(MapBase):
    name           = "NEON CITY"
    subtitle       = "The Grid Never Sleeps"
    gravity        = 600
    bg_color       = (6, 4, 18)
    platform_col   = (55, 30, 110)
    platform_glow  = (180, 60, 255)
    grid_color     = (18, 10, 38)
    accent         = (180, 60, 255)
    secret_hint    = "Grid glitch incoming..."
    secret_cooldown = 22.0

    NEON_PINK   = (255, 50, 180)
    NEON_PURPLE = (180, 60, 255)
    NEON_CYAN   = (0, 230, 255)

    def __init__(self):
        super().__init__()
        self.glitch_flash = 0.0   # white flash when glitch fires

    def _build_platforms(self):
        return [
            _plat(0,            BOT,        W,    8),    # floor
            _plat(30,           BOT-110,    220),        # low-left
            _plat(W-250,        BOT-110,    220),        # low-right
            _plat(W//2-130,     BOT-200,    260),        # center-low
            _plat(80,           BOT-300,    180),        # mid-left
            _plat(W-260,        BOT-300,    180),        # mid-right
            _plat(W//2-90,      BOT-390,    180),        # center-mid
            _plat(20,           BOT-490,    160),        # upper-left
            _plat(W-180,        BOT-490,    160),        # upper-right
            _plat(W//2-70,      BOT-580,    140),        # apex
        ]

    def _trigger_secret(self, players):
        self.glitch_flash = 0.35
        self.announce("⚡  GRID GLITCH!", 2.5)
        for player in players:
            player.velocity.x = random.choice([-1, 1]) * random.uniform(350, 650)
            player.velocity.y = -random.uniform(250, 500)
            player.take_damage(12)
        for _ in range(80):
            x = random.randint(0, W)
            y = random.randint(TOP, H)
            self._spawn_particle(x, y,
                                 random.uniform(-150, 150),
                                 random.uniform(-100, 100),
                                 random.uniform(0.4, 1.4),
                                 random.choice([self.NEON_PINK, self.NEON_PURPLE, self.NEON_CYAN]))

    def update(self, dt, players):
        super().update(dt, players)
        if self.glitch_flash > 0:
            self.glitch_flash -= dt

    def draw_bg(self, surface):
        surface.fill(self.bg_color)
        # Scan lines
        for y in range(TOP, H, 4):
            a = int(12 + 6 * math.sin(y * 0.05 + self.time * 2))
            s = pygame.Surface((W, 1), pygame.SRCALPHA)
            s.fill((0, 0, 0, a))
            surface.blit(s, (0, y))
        self._draw_grid(surface)
        # Horizon neon glow
        for i in range(24):
            a = max(0, 36 - i * 2)
            s = pygame.Surface((W, 2), pygame.SRCALPHA)
            s.fill((*self.NEON_PURPLE, a))
            surface.blit(s, (0, H // 2 + 60 + i * 4))
        # Glitch white flash
        if self.glitch_flash > 0:
            fa = int(200 * self.glitch_flash / 0.35)
            fl = pygame.Surface((W, H), pygame.SRCALPHA)
            fl.fill((255, 255, 255, fa))
            surface.blit(fl, (0, 0))

    def draw_platforms(self, surface):
        for plat in self.platforms:
            pulse = abs(math.sin(self.time * 1.8 + plat.x * 0.01))
            glow  = tuple(min(255, int(c * (0.7 + 0.5 * pulse))) for c in self.platform_glow)
            self._draw_platform(surface, plat, glow=glow)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAP 2 — LAVA DUNGEON
#  Unique: lava floor damages players, bubbling animation, LAVA SURGE secret
#  (floor rises rapidly — players caught by lava take heavy damage)
# ═══════════════════════════════════════════════════════════════════════════════

class LavaDungeonMap(MapBase):
    name           = "LAVA DUNGEON"
    subtitle       = "Mind the Floor"
    gravity        = 700
    bg_color       = (14, 4, 2)
    platform_col   = (110, 35, 12)
    platform_glow  = (255, 100, 20)
    grid_color     = (30, 10, 5)
    accent         = (255, 80, 0)
    secret_hint    = "Lava surge incoming..."
    secret_cooldown = 18.0

    LAVA_RED    = (255, 50, 0)
    LAVA_ORANGE = (255, 140, 0)
    LAVA_YELLOW = (255, 220, 0)

    def __init__(self):
        super().__init__()
        self.lava_y      = float(BOT)
        self.lava_target = float(BOT)
        self.lava_rise   = False
        self.lava_bubbles = [
            {"x": random.randint(0, W),
             "phase": random.uniform(0, math.pi * 2),
             "speed": random.uniform(0.8, 2.2),
             "size":  random.randint(5, 16)}
            for _ in range(14)
        ]

    def _build_platforms(self):
        return [
            _plat(0,            BOT,        W,    8),    # floor (lava base)
            _plat(40,           BOT-100,    200),        # low-left
            _plat(W-240,        BOT-100,    200),        # low-right
            _plat(W//2-90,      BOT-180,    180),        # center-low
            _plat(60,           BOT-275,    200),        # mid-left
            _plat(W-260,        BOT-275,    200),        # mid-right
            _plat(W//2-100,     BOT-360,    200),        # center-mid
            _plat(100,          BOT-455,    170),        # upper-left
            _plat(W-270,        BOT-455,    170),        # upper-right
            _plat(W//2-60,      BOT-540,    120),        # high-center
            _plat(W//2-50,      BOT-620,    100),        # apex
        ]

    def _trigger_secret(self, players):
        self.lava_rise   = True
        self.lava_target = BOT - 200
        self.announce("🌋  LAVA SURGE!", 2.5)
        for _ in range(50):
            x = random.randint(0, W)
            self._spawn_particle(x, self.lava_y,
                                 random.uniform(-80, 80),
                                 random.uniform(-350, -80),
                                 random.uniform(0.5, 1.6),
                                 random.choice([self.LAVA_RED, self.LAVA_ORANGE, self.LAVA_YELLOW]))

    def update(self, dt, players):
        super().update(dt, players)
        # Move lava
        if self.lava_rise:
            self.lava_y += (self.lava_target - self.lava_y) * 4 * dt
            if abs(self.lava_y - self.lava_target) < 3:
                self.lava_rise   = False
                self.lava_target = float(BOT)
        else:
            self.lava_y += (self.lava_target - self.lava_y) * 1.8 * dt

        # Sync floor platform
        self.platforms[0].y      = int(self.lava_y)
        self.platforms[0].height = H - int(self.lava_y) + 4

        # Damage players touching lava surface
        for p in players:
            if p.pos.y + p.display_radius() >= self.lava_y - 4:
                p.take_damage(35 * dt)

        # Bubble particles
        for b in self.lava_bubbles:
            if random.random() < 0.025:
                self._spawn_particle(
                    b["x"] + random.randint(-25, 25), self.lava_y,
                    random.uniform(-40, 40), random.uniform(-100, -25),
                    random.uniform(0.3, 1.1),
                    random.choice([self.LAVA_RED, self.LAVA_ORANGE]))

    def draw_bg(self, surface):
        surface.fill(self.bg_color)
        # Fiery glow at lava surface
        for i in range(50):
            a = max(0, 90 - i * 2)
            s = pygame.Surface((W, 3), pygame.SRCALPHA)
            s.fill((255, max(0, 90 - i * 4), 0, a))
            surface.blit(s, (0, int(self.lava_y) - 8 + i * 3))
        self._draw_grid(surface)

    def draw_platforms(self, surface):
        for i, plat in enumerate(self.platforms):
            if i == 0:
                # Lava pool
                r = pygame.Rect(0, int(self.lava_y), W, H - int(self.lava_y) + 4)
                pygame.draw.rect(surface, self.LAVA_RED, r)
                # Bubbles
                for b in self.lava_bubbles:
                    bob = math.sin(self.time * b["speed"] + b["phase"]) * 5
                    pygame.draw.circle(surface, self.LAVA_ORANGE,
                                       (b["x"], int(self.lava_y + bob)),
                                       b["size"])
                pygame.draw.rect(surface, self.LAVA_YELLOW,
                                 pygame.Rect(0, int(self.lava_y), W, 4))
            else:
                # Stone shelves with orange-glow edges
                self._draw_platform(surface, plat)
                # Embers glowing on top edge
                for ex in range(plat.x + 10, plat.right - 10, 40):
                    a = int(120 + 80 * abs(math.sin(self.time * 2 + ex * 0.05)))
                    pygame.draw.circle(surface, (*self.LAVA_ORANGE, a),
                                       (ex, plat.y), 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAP 3 — ICE FORTRESS
#  Unique: slippery ground (very low friction), falling icicle hazards,
#  aurora background, BLIZZARD secret (strong leftward wind + damage)
# ═══════════════════════════════════════════════════════════════════════════════

class IceFortressMap(MapBase):
    name           = "ICE FORTRESS"
    subtitle       = "Slippery When Frozen"
    gravity        = 560
    bg_color       = (4, 10, 28)
    platform_col   = (28, 78, 160)
    platform_glow  = (100, 200, 255)
    grid_color     = (10, 20, 50)
    accent         = (100, 200, 255)
    secret_hint    = "The blizzard stirs..."
    secret_cooldown = 20.0

    ICE_WHITE = (210, 235, 255)
    ICE_BLUE  = (80, 160, 255)

    def __init__(self):
        super().__init__()
        self.snow = [
            {"x": random.uniform(0, W),
             "y": random.uniform(0, H),
             "vx": random.uniform(-15, 5),
             "vy": random.uniform(30, 80),
             "sz": random.randint(2, 5),
             "a":  random.randint(80, 200)}
            for _ in range(90)
        ]
        self.blizzard_active = False
        self.blizzard_timer  = 0.0

        # Icicles — hang from under certain platforms
        self.icicles = []   # {x, y, vy, active, plat_idx}
        self._reset_icicles()

    def _reset_icicles(self):
        self.icicles = []
        plats = self._build_platforms()
        for pi in range(1, min(6, len(plats))):
            plat = plats[pi]
            for _ in range(2):
                x = random.randint(plat.x + 10, plat.right - 10)
                self.icicles.append({
                    "x": x, "y": float(plat.bottom + 6),
                    "vy": 0.0, "dropped": False,
                    "plat_x": plat.x, "plat_right": plat.right,
                    "drop_y": plat.bottom + 6,
                })

    def _build_platforms(self):
        return [
            _plat(0,            BOT,        W,    8),    # floor (ice)
            _plat(0,            BOT-120,    240),        # left-low
            _plat(W-240,        BOT-120,    240),        # right-low
            _plat(W//2-100,     BOT-210,    200),        # center-low
            _plat(80,           BOT-310,    200),        # mid-left
            _plat(W-280,        BOT-310,    200),        # mid-right
            _plat(W//2-80,      BOT-400,    160),        # center-mid
            _plat(20,           BOT-490,    170),        # upper-left
            _plat(W-190,        BOT-490,    170),        # upper-right
            _plat(W//2-60,      BOT-575,    120),        # apex
        ]

    def _trigger_secret(self, players):
        self.blizzard_active = True
        self.blizzard_timer  = 4.5
        self.announce("❄  BLIZZARD!", 2.5)
        for p in players:
            p.velocity.x -= 600

    def update(self, dt, players):
        super().update(dt, players)

        # Snow movement
        wind = -220.0 if self.blizzard_active else -18.0
        for s in self.snow:
            s["x"] += (wind + s["vx"]) * dt
            s["y"] += s["vy"] * dt
            if s["y"] > H:
                s["y"] = -8
                s["x"] = random.uniform(0, W)
            if s["x"] < -10:
                s["x"] = W + 10

        # Blizzard
        if self.blizzard_active:
            self.blizzard_timer -= dt
            for p in players:
                p.velocity.x -= 700 * dt          # persistent push
                p.take_damage(8 * dt)             # frostbite damage
            if self.blizzard_timer <= 0:
                self.blizzard_active = False

        # Ice friction — VERY slippery (key mechanic)
        for p in players:
            if p.on_ground and not p.has_buff("grip"):
                p.velocity.x *= 0.975             # almost no deceleration

        # Icicle physics
        for ic in self.icicles:
            if not ic["dropped"]:
                # Drop if a player is directly below
                for p in players:
                    if ic["plat_x"] <= p.pos.x <= ic["plat_right"]:
                        if abs(p.pos.x - ic["x"]) < 50 and p.pos.y > ic["y"]:
                            ic["dropped"] = True
                            ic["vy"]      = 20.0
            else:
                ic["vy"] += self.gravity * dt
                ic["y"]  += ic["vy"] * dt
                # Hit a player?
                for p in players:
                    if abs(p.pos.x - ic["x"]) < 18 and abs(p.pos.y - ic["y"]) < 18:
                        p.take_damage(22)
                        ic["y"] = ic["drop_y"]
                        ic["vy"]      = 0.0
                        ic["dropped"] = False
                # Reset if off-screen
                if ic["y"] > H + 40:
                    ic["y"]      = ic["drop_y"]
                    ic["vy"]     = 0.0
                    ic["dropped"] = False

    def draw_bg(self, surface):
        surface.fill(self.bg_color)
        # Aurora bands
        for i in range(36):
            a    = max(0, 48 - i * 2)
            wave = math.sin(self.time * 0.4 + i * 0.35) * 28
            s    = pygame.Surface((W, 5), pygame.SRCALPHA)
            g    = (40 + i * 3) % 90
            s.fill((0, 140 + g, 200, a))
            surface.blit(s, (int(wave), TOP + i * 6))
        self._draw_grid(surface)
        # Blizzard overlay
        if self.blizzard_active:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((200, 230, 255, int(30 * (self.blizzard_timer / 4.5))))
            surface.blit(ov, (0, 0))

    def draw_platforms(self, surface):
        for plat in self.platforms:
            self._draw_platform(surface, plat,
                                color=self.platform_col, glow=self.platform_glow)
            # Ice shine stripe
            shine = pygame.Rect(plat.x + 5, plat.y + 1, plat.width // 3, 3)
            pygame.draw.rect(surface, self.ICE_WHITE, shine, border_radius=2)

    def draw_foreground(self, surface):
        super().draw_foreground(surface)
        # Snow flakes
        for s in self.snow:
            a   = min(255, s["a"] + (120 if self.blizzard_active else 0))
            srf = pygame.Surface((s["sz"] * 2, s["sz"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(srf, (210, 235, 255, a), (s["sz"], s["sz"]), s["sz"])
            surface.blit(srf, (int(s["x"]) - s["sz"], int(s["y"]) - s["sz"]))
        # Icicles
        for ic in self.icicles:
            x, y = int(ic["x"]), int(ic["y"])
            # Icicle shape: triangle pointing down
            pts = [(x - 5, y), (x + 5, y), (x, y + 22)]
            pygame.draw.polygon(surface, self.ICE_WHITE, pts)
            pygame.draw.polygon(surface, self.ICE_BLUE, pts, 1)
            # Shine
            pygame.draw.line(surface, (255, 255, 255), (x - 2, y + 2), (x, y + 14), 1)


ALL_MAPS = [NeonCityMap, LavaDungeonMap, IceFortressMap]