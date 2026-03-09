import random

BUFF_DEFS = [
    {"id": "speed",      "label": "SPEED BOOST",  "icon": "⚡", "color": (255, 220, 0),   "duration": 6.0, "weight": 10},
    {"id": "super_jump", "label": "SUPER JUMP",   "icon": "🚀", "color": (0, 230, 255),   "duration": 6.0, "weight": 10},
    {"id": "tiny",       "label": "TINY",          "icon": "🔬", "color": (50, 255, 120),  "duration": 7.0, "weight": 8},
    {"id": "shield",     "label": "SHIELD",        "icon": "🛡", "color": (180, 50, 255),  "duration": 4.0, "weight": 6},
    {"id": "ghost",      "label": "GHOST",         "icon": "👻", "color": (180, 180, 255), "duration": 5.0, "weight": 5},
    {"id": "low_grav",   "label": "LOW GRAVITY",  "icon": "🌙", "color": (100, 200, 255), "duration": 6.0, "weight": 8},
    {"id": "giant",      "label": "GIANT",         "icon": "💪", "color": (255, 100, 50),  "duration": 5.0, "weight": 5},
    {"id": "slow",       "label": "SLOW CURSE",   "icon": "🐌", "color": (180, 120, 40),  "duration": 5.0, "weight": 4},
    {"id": "magnet",     "label": "MAGNET",        "icon": "🧲", "color": (255, 80, 80),   "duration": 5.0, "weight": 6},
]

_POOL = []
for b in BUFF_DEFS:
    _POOL.extend([b["id"]] * b["weight"])

BUFF_BY_ID = {b["id"]: b for b in BUFF_DEFS}

def random_buff_id():
    return random.choice(_POOL)