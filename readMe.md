# 🏆 Trophy Tag

A fast-paced local multiplayer game for 2–3 players. One trophy. Everyone wants it. Nobody keeps it for long.

---

## How to Play

**The goal is simple:** steal the trophy and hold onto it. First player to rack up **10 steals wins**.

But here's the twist — **dying costs you a point**. So yes, the lava, the icicles, and the blizzard actually matter.

### Controls

| Player | Move Left | Move Right | Jump |
|--------|-----------|------------|------|
| P1 | `A` | `D` | `W` |
| P2 | `←` | `→` | `↑` |
| P3 | `Num 4` | `Num 6` | `Num 8` |

`ESC` goes back a screen. `SPACE` confirms / replays.

---

## The Arenas

### 🌆 Neon City
The grid never sleeps. Platforms pulse with neon light and scan-lines flicker across the sky. Every ~22 seconds, a **Grid Glitch** fires — everyone gets blasted in a random direction and takes damage. Don't get caught in the open.

### 🌋 Lava Dungeon
Higher gravity. The floor is lava — literally. Standing on it drains your HP fast. Every ~18 seconds, a **Lava Surge** raises the floor, forcing everyone onto the platforms or taking heavy damage. Stay high.

### 🏔 Ice Fortress
Lower gravity, aurora skies — and almost zero friction on the ground. You slide everywhere. Icicles hang below platforms and drop if you walk underneath them. Every ~20 seconds, a **Blizzard** hits from the left, pushing everyone sideways and dealing frostbite damage over time.

---

## Power-Ups

Buffs spawn on platforms every ~9 seconds. Walk into one to grab it.

| Icon | Name | Effect |
|------|------|--------|
| ⚡ | Speed Boost | Move 2× faster |
| 🚀 | Super Jump | Jump 2× higher |
| 🔬 | Tiny | Shrink — harder to steal from |
| 🛡 | Shield | Can't lose the trophy while active |
| 👻 | Ghost | Phase through platforms |
| 🌙 | Low Gravity | Float longer, fall slower |
| 💪 | Giant | Grow big (easier to steal from though!) |
| 🐌 | Slow Curse | Half speed — try not to grab this one |
| 🧲 | Magnet | Pulls the trophy holder toward you |

---

## Health & Death

Every player has a HP bar shown above their character and in the HUD. When it hits zero:

- You **lose 1 point** from your score
- The trophy **drops** to another player
- You respawn at the top with **2.5 seconds of invincibility**
- All your buffs are cleared

So dying isn't just inconvenient — it actively sets you back.

---

## Tips

- Holding the trophy slows you down slightly. Plan your escape route before stealing.
- The **Shield** buff is the most powerful — grab it when you already have the trophy.
- On Ice Fortress, use the slide to your advantage — build up momentum and it's hard for others to catch you.
- Watch the **secret hint** at the bottom of the screen. When it starts flashing fast, something's about to happen.
- Dying resets your buffs, so don't be reckless just because you have a speed boost.

---

## Setup

1. Make sure you have Python and pygame installed:
   ```
   pip install pygame
   ```
2. Run the game:
   ```
   python main.py
   ```
3. (Optional) Drop a music file named `background.wav` into an `assets/` folder next to `main.py` for background music. Synthwave or chiptune works great.

---

## Files

```
main.py      — game loop, screens, drawing
models.py    — Player class (physics, health, buffs)
maps.py      — the three arenas and their unique mechanics
buffs.py     — power-up definitions
assets/
  background.wav   (optional music)
```

---

*Built with Python + pygame. 1280×720, 60fps, local multiplayer only.*

---
---

# 🛠 How I Built This

> A behind-the-scenes look at the technical side — for anyone curious about how a game like this actually comes together.

---

## The Stack

Just two things: **Python** and **pygame**. No game engine, no framework. Everything — physics, rendering, collision, UI — is written from scratch.

---

## Architecture: 4 Files

The project is split into four focused modules:

**`models.py` — the Player**
Everything a player *is* lives here. Position, velocity, health, buffs, and the physics update loop. The interesting bit is the squash/stretch animation — it uses a spring model. When you land, it kicks a "deviation" variable negative (wide squash), and a spring force pulls it back to zero (perfect circle) over time, with damping to stop it oscillating forever. This is how cartoon characters feel bouncy without any artist drawing every frame.

**`maps.py` — the Arenas**
Each map is a class that inherits from a `MapBase`. The base handles the platform loop, particle system, and the secret event timer. Each subclass overrides `_build_platforms()`, `draw_bg()`, `draw_platforms()`, `draw_foreground()`, and `_trigger_secret()`. This made it clean to add wildly different map mechanics — lava that physically rises and damages players, ice friction that's just one line (`velocity.x *= 0.975` per frame), icicles that track player positions.

**`buffs.py` — power-ups**
A simple data file. Each buff is a dictionary with an id, label, icon, color, duration, and a weight for weighted random selection. The player class reads these at runtime — `effective_speed()`, `effective_jump()`, `display_radius()` all check the buffs dict and scale accordingly.

**`main.py` — everything else**
Game states (`S_COUNT → S_MAP → S_PLAY → S_WIN`), the main loop, all drawing functions, and game logic like steal detection and buff spawning. Steal detection is just a distance check between the trophy holder and every other player each frame. If close enough and the cooldown has expired, ownership transfers.

---

## Physics

There's no physics library — it's all manual. Each frame:

1. Apply gravity to vertical velocity
2. Move the player by velocity × delta-time
3. Check rect collision against each platform
4. If the player's bottom was above the platform top last frame and is now intersecting, snap them to the surface

Delta-time (`dt`) is always in seconds so the game runs the same speed at any framerate.

The lava map changes gravity to 700, the ice map uses 560 — one number swap per map that completely changes how the game feels.

---

## The Health System

HP drains from environmental hazards (lava contact, blizzard, icicles) using `take_damage(amount * dt)` for continuous sources or `take_damage(fixed)` for hits. There's an invincibility timer after each hit to prevent instant death from rapid ticks. Death subtracts a score point — so the health system has real stakes, not just a cosmetic bar.

---

## Rendering

Everything is drawn with `pygame.draw` primitives — no sprites, no images. Characters are ellipses with circles for eyes and arcs for mouths. The squash/stretch system modifies the ellipse width and height each frame. Glow effects are layered transparent circles drawn to an SRCALPHA surface and blitted on top. The lava surface is a `pygame.Rect` whose Y position is updated every frame as it rises and falls.

---

## What I'd Add Next

- Online multiplayer (probably the hardest thing to add)
- A 4th player slot
- More maps
- Per-map music tracks
- A replay system