"""Creates the email banners in banners/.

Run from the project folder (needs Windows fonts and Pillow: pip install pillow):

    python tools/make-banners.py

To change the wording or add a style, edit TITLE, EYEBROW or THEMES below.

Banners are cached for a year and already-sent emails keep loading them, so never
overwrite a banner that has been used. Give the new version a new theme name and
add it to BANNERS in index.html.
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TITLE = 'Танд баяр хүргэе!'
EYEBROW = 'JCI MONGOLIA  ·  ХӨГЖЛИЙН ЗӨВЛӨЛ'

WIDTH, HEIGHT = 1120, 448   # shown at 560px wide in the email, so sharp on phones
SCALE = 2                   # drawn larger, then shrunk, for smooth edges
FRAMES = 30
FRAME_MS = 70
PIECES = 34
COLORS = 64

FONT_DIR = Path('C:/Windows/Fonts')
TITLE_FONT = FONT_DIR / 'segoeuib.ttf'
EYEBROW_FONT = FONT_DIR / 'seguisb.ttf'

THEMES = {
    'blue':  {'bg': '#0A7CC2', 'title': '#FFFFFF', 'eyebrow': '#D9EEFB', 'confetti': ['#FFFFFF', '#8CCBF2']},
    'dark':  {'bg': '#15171C', 'title': '#FFFFFF', 'eyebrow': '#A4A8B0', 'confetti': ['#4AA8EA', '#F5F5F7']},
    'light': {'bg': '#F3F4F6', 'title': '#16181D', 'eyebrow': '#5F6368', 'confetti': ['#0A7CC2', '#B4BAC4']},
    'gold':  {'bg': '#0B2545', 'title': '#F2C14E', 'eyebrow': '#C9D3E0', 'confetti': ['#F2C14E', '#FFFFFF']},
}


def make_pieces(colors):
    """Every piece moves a whole number of cycles per loop, so the GIF repeats without a jump."""
    rng = random.Random(2027)
    pieces = []
    for i in range(PIECES):
        # Only at the sides, so the confetti never touches the text.
        x = rng.choice((rng.uniform(0.02, 0.16), rng.uniform(0.84, 0.98)))
        pieces.append({
            'x': x * WIDTH,
            'y': rng.uniform(0, 1),
            'sway': rng.uniform(5, 14),
            'phase': rng.uniform(0, math.tau),
            'turns': rng.choice((1, 2)),
            'size': rng.uniform(9, 15),
            'round': rng.random() < 0.3,
            'color': colors[i % len(colors)],
        })
    return pieces


def draw_piece(draw, piece, t):
    margin = 24
    span = HEIGHT + margin * 2
    y = (piece['y'] + t) % 1 * span - margin
    x = piece['x'] + math.sin(t * math.tau + piece['phase']) * piece['sway']
    size = piece['size'] * SCALE
    cx, cy = x * SCALE, y * SCALE
    if piece['round']:
        r = size * 0.45
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=piece['color'])
        return
    angle = piece['phase'] + t * math.tau * piece['turns']
    flip = 0.35 + 0.65 * abs(math.cos(t * math.tau * piece['turns'] + piece['phase']))
    half_w, half_h = size * 0.6, size * 0.38 * flip
    corners = []
    for dx, dy in ((-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h)):
        corners.append((cx + dx * math.cos(angle) - dy * math.sin(angle),
                        cy + dx * math.sin(angle) + dy * math.cos(angle)))
    draw.polygon(corners, fill=piece['color'])


def text_layer(theme):
    layer = Image.new('RGBA', (WIDTH * SCALE, HEIGHT * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    center = WIDTH * SCALE / 2

    title_size = 104 * SCALE
    title_font = ImageFont.truetype(str(TITLE_FONT), title_size)
    while draw.textlength(TITLE, font=title_font) > WIDTH * SCALE * 0.62:
        title_size -= 2
        title_font = ImageFont.truetype(str(TITLE_FONT), title_size)
    eyebrow_font = ImageFont.truetype(str(EYEBROW_FONT), 22 * SCALE)

    draw.text((center, HEIGHT * SCALE * 0.335), EYEBROW, font=eyebrow_font, fill=theme['eyebrow'], anchor='mm')
    draw.text((center, HEIGHT * SCALE * 0.545), TITLE, font=title_font, fill=theme['title'], anchor='mm')
    return layer.resize((WIDTH, HEIGHT), Image.LANCZOS)


def make_banner(name, theme, out_dir):
    pieces = make_pieces(theme['confetti'])
    text = text_layer(theme)
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        big = Image.new('RGB', (WIDTH * SCALE, HEIGHT * SCALE), theme['bg'])
        draw = ImageDraw.Draw(big)
        for piece in pieces:
            draw_piece(draw, piece, t)
        frame = big.resize((WIDTH, HEIGHT), Image.LANCZOS)
        frame.paste(text, (0, 0), text)
        frames.append(frame)

    # One palette for all frames, so colors do not flicker between frames.
    palette = frames[0].quantize(COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    path = out_dir / f'{name}.gif'
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=FRAME_MS, loop=0, disposal=1)
    print(f'{path.name}: {path.stat().st_size // 1024} KB')


def main():
    out_dir = Path(__file__).resolve().parent.parent / 'banners'
    out_dir.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        make_banner(name, theme, out_dir)


if __name__ == '__main__':
    main()
