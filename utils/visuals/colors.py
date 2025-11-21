import random

# Monika-themed color palette (hex values)
MONIKA_COLORS = [
    0xFFB3B3,  # Soft peach/pink
    0xFF7F7F,  # Coral
    0xFF9999,  # Light coral
    0xFFCCCB,  # Light pink
    0xFFD6E0,  # Pastel pink
    0xFFE4EC,  # Very light pink
    0xFF8DAA,  # Pinkish
    0xFFB6C1,  # Light pink
    0xDC143C,  # Crimson
    0xFF6347,  # Tomato
    0x98FB98,  # Pale green (Monika's eyes)
    0xF0E68C,  # Khaki (warm accent)
    0xFFDAB9,  # Peach puff
    0xFFEFD5,  # Papaya whip
]

#━━━━━━━━━━━━━━━━━━━━━
#   🎨 Monika Color Utilities 🎨
#━━━━━━━━━━━━━━━━━━━━━
def get_random_monika_color():
    """
    Returns a random Monika-themed color (as an integer for Discord embeds).
    """
    return random.choice(MONIKA_COLORS)
