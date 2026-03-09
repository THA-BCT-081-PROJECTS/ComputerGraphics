import pygame
import math


class Player:
    BASE_JUMP  = 430
    BASE_SPEED = 270
    MAX_HP     = 100

    def __init__(self, x, y, radius, color=(255, 255, 255), player_id=0):
        self.pos        = pygame.Vector2(x, y)
        self.velocity   = pygame.Vector2(0, 0)
        self.on_ground  = False
        self.radius     = radius
        self.color      = color
        self.player_id  = player_id
        self.rect       = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.buffs      = {}        # {buff_id: time_remaining}
        self.has_trophy = False

        # Health
        self.hp         = self.MAX_HP
        self.invincible = 0.0       # seconds of invincibility after taking damage

        # Squash/stretch — deviation from 0.
        # dev=0 → perfect circle.  dev>0 → taller.  dev<0 → wider (squashed flat).
        self.squash_dev = 0.0
        self.squash_vel = 0.0

    # ── Buffs ─────────────────────────────────────────────────────────────────
    def apply_buff(self, buff_id, duration):
        self.buffs[buff_id] = duration

    def has_buff(self, buff_id):
        return buff_id in self.buffs

    def tick_buffs(self, dt):
        for k in list(self.buffs):
            self.buffs[k] -= dt
            if self.buffs[k] <= 0:
                del self.buffs[k]

    def effective_speed(self):
        s = self.BASE_SPEED
        if self.has_buff("speed"):      s *= 2.0
        if self.has_buff("slow"):       s *= 0.45
        if self.has_trophy:             s *= 0.84
        return s

    def effective_jump(self):
        j = self.BASE_JUMP
        if self.has_buff("super_jump"): j *= 2.1
        if self.has_buff("low_grav"):   j *= 1.5
        return j

    def display_radius(self):
        r = self.radius
        if self.has_buff("tiny"):  r = max(8, int(r * 0.55))
        if self.has_buff("giant"): r = int(r * 1.6)
        return r

    def is_ghost(self):
        return self.has_buff("ghost")

    # ── Health ────────────────────────────────────────────────────────────────
    def take_damage(self, amount):
        if self.invincible > 0 or self.has_buff("shield"):
            return False
        self.hp = max(0, self.hp - amount)
        self.invincible = 1.2
        return True

    def heal(self, amount):
        self.hp = min(self.MAX_HP, self.hp + amount)

    def is_dead(self):
        return self.hp <= 0

    # ── Movement ──────────────────────────────────────────────────────────────
    def jump(self):
        if self.on_ground:
            self.velocity.y  = -self.effective_jump()
            self.on_ground   = False
            self.squash_vel  = -2.0   # kick upward (stretch tall)

    def move_left(self, dt):
        self.pos.x -= self.effective_speed() * dt

    def move_right(self, dt):
        self.pos.x += self.effective_speed() * dt

    # ── Physics ───────────────────────────────────────────────────────────────
    def update(self, dt, platforms, gravity, width, height):
        g = gravity * (0.45 if self.has_buff("low_grav") else 1.0)

        self.velocity.y += g * dt
        self.pos.y      += self.velocity.y * dt
        self.on_ground   = False
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if not self.is_ghost():
            self._platform_collision(platforms)

        self._vertical_bounds(height)
        self._horizontal_bounds(width)
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Spring model: pulls squash_dev back to 0 (round)
        spring_k         = 20.0
        damping          = 8.0
        accel            = -spring_k * self.squash_dev - damping * self.squash_vel
        self.squash_vel += accel * dt
        self.squash_dev += self.squash_vel * dt
        self.squash_dev  = max(-0.6, min(0.8, self.squash_dev))

        self.tick_buffs(dt)
        if self.invincible > 0:
            self.invincible -= dt

    def _horizontal_bounds(self, width):
        if self.pos.x < -self.radius:
            self.pos.x = width + self.radius
        elif self.pos.x > width + self.radius:
            self.pos.x = -self.radius

    def _vertical_bounds(self, height):
        if self.pos.y >= height - self.radius:
            self.pos.y = height - self.radius
            if self.velocity.y > 0:
                impact           = min(0.6, abs(self.velocity.y) / 1200.0)
                self.squash_dev  = -impact * 1.0   # wide on landing
                self.squash_vel  = impact * 4.0
                self.velocity.y  = 0
                self.on_ground   = True
        if self.pos.y <= self.radius:
            self.pos.y = self.radius
            if self.velocity.y < 0:
                self.velocity.y = 0

    def _platform_collision(self, platforms):
        for plat in platforms:
            if not self.rect.colliderect(plat):
                continue
            if self.velocity.y >= 0:
                if self.rect.bottom - self.velocity.y * 0.016 <= plat.top + 10:
                    self.rect.bottom = plat.top
                    self.pos.y       = self.rect.centery
                    impact           = min(0.6, abs(self.velocity.y) / 1200.0)
                    self.squash_dev  = -impact * 1.0
                    self.squash_vel  = impact * 4.0
                    self.velocity.y  = 0
                    self.on_ground   = True
            elif self.velocity.y < 0:
                if self.rect.top >= plat.bottom - 10:
                    self.rect.top    = plat.bottom
                    self.pos.y       = self.rect.centery
                    self.velocity.y  = 0

    def get_draw_wh(self):
        """Return (w, h) for avatar ellipse. dev=0 → perfect circle."""
        dr  = self.display_radius()
        dev = self.squash_dev
        w   = max(4, int(dr * 2 * (1.0 - dev * 0.55)))
        h   = max(4, int(dr * 2 * (1.0 + dev)))
        return w, h