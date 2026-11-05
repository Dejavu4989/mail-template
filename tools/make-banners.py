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

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

TITLE = 'Танд баяр хүргэе!'
EYEBROW = 'JCI MONGOLIA  ·  ХӨГЖЛИЙН ЗӨВЛӨЛ'

WIDTH, HEIGHT = 1080, 486   # same shape as hero.gif, so banners swap without moving the email
SCALE = 2                   # drawn larger, then shrunk, for smooth edges
FRAMES = 24
FRAME_MS = 100
PIECES = 44
COLORS = 192

FONT_DIR = Path('C:/Windows/Fonts')
TITLE_FONT = FONT_DIR / 'palab.ttf'       # has the Mongolian letters; Georgia does not
EYEBROW_FONT = FONT_DIR / 'seguisb.ttf'

STRIP = ['#FFD166', '#06D6A0', '#2EB6F0', '#D6335A']   # thin band along the bottom, like hero.gif

# Where confetti may not go, as (left, top, right, bottom) in parts of the banner.
KEEP_CLEAR = [
    (0.17, 0.05, 0.83, 0.23),   # label
    (0.38, 0.20, 0.62, 0.62),   # party popper
    (0.07, 0.58, 0.93, 0.92),   # title
    (0.00, 0.94, 1.00, 1.00),   # bottom strip
]

THEMES = {
    'ocean': {
        'from': '#0B4FA8', 'to': '#17A3E3', 'title': '#FFD166', 'label': '#FFFFFF',
        'shadow': '#062A63', 'stripes': (255, 255, 255, 12), 'glow': (255, 255, 255, 46),
        'confetti': ['#FFD166', '#FFFFFF', '#06D6A0', '#FF6B8B', '#8FE3FF'],
    },
    'night': {
        'from': '#07142E', 'to': '#163B7A', 'title': '#FFD166', 'label': '#DCE8F7',
        'shadow': '#02060F', 'stripes': (255, 255, 255, 8), 'glow': (90, 170, 255, 46),
        'confetti': ['#FFD166', '#FFFFFF', '#2EB6F0', '#FF6B8B', '#06D6A0'],
    },
    'berry': {
        'from': '#6E1240', 'to': '#D6335A', 'title': '#FFFFFF', 'label': '#FFE3EA',
        'shadow': '#3F0824', 'stripes': (255, 255, 255, 12), 'glow': (255, 214, 170, 50),
        'confetti': ['#FFD166', '#FFFFFF', '#FFB3C4', '#8FE3FF', '#06D6A0'],
    },
    'sky': {
        'from': '#E4F3FC', 'to': '#B5E0F7', 'title': '#0B4FA8', 'label': '#0B4FA8',
        'shadow': None, 'stripes': (255, 255, 255, 26), 'glow': (255, 255, 255, 0),
        'confetti': ['#0A7CC2', '#D6335A', '#E0A100', '#06B58A', '#FFFFFF'],
    },
}


def diagonal_gradient(start, end):
    size = WIDTH * 2
    mask = Image.linear_gradient('L').resize((size, size)).rotate(62, Image.BICUBIC)
    left, top = (size - WIDTH) // 2, (size - HEIGHT) // 2
    mask = mask.crop((left, top, left + WIDTH, top + HEIGHT))
    return Image.composite(Image.new('RGB', mask.size, end), Image.new('RGB', mask.size, start), mask)


def stripes_layer(color):
    layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for x in range(-HEIGHT, WIDTH, 150):
        draw.polygon([(x, HEIGHT), (x + 62, HEIGHT), (x + 62 + HEIGHT, 0), (x + HEIGHT, 0)], fill=color)
    return layer


def glow_layer(color):
    layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((WIDTH * 0.2, HEIGHT * 0.08, WIDTH * 0.8, HEIGHT * 0.88), fill=color)
    return layer.filter(ImageFilter.GaussianBlur(70))


def spaced_text(draw, center, y, text, font, fill, spacing):
    widths = [draw.textlength(ch, font=font) for ch in text]
    x = center - (sum(widths) + spacing * (len(text) - 1)) / 2
    for ch, width in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill, anchor='lm')
        x += width + spacing


def label_layer(theme):
    s = SCALE
    layer = Image.new('RGBA', (WIDTH * s, HEIGHT * s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype(str(EYEBROW_FONT), 19 * s)
    spacing = 2.4 * s
    text_width = sum(draw.textlength(ch, font=font) for ch in EYEBROW) + spacing * (len(EYEBROW) - 1)
    center, y = WIDTH * s / 2, HEIGHT * s * 0.135
    half_w, half_h = text_width / 2 + 26 * s, 22 * s
    r, g, b = Image.new('RGB', (1, 1), theme['label']).getpixel((0, 0))
    draw.rounded_rectangle((center - half_w, y - half_h, center + half_w, y + half_h), radius=half_h,
                           fill=(r, g, b, 28), outline=(r, g, b, 150), width=2 * s)
    spaced_text(draw, center, y, EYEBROW, font, theme['label'], spacing)
    return layer.resize((WIDTH, HEIGHT), Image.LANCZOS)


def title_layer(theme):
    s = SCALE
    size = 92 * s
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    font = ImageFont.truetype(str(TITLE_FONT), size)
    while probe.textlength(TITLE, font=font) > WIDTH * s * 0.8:
        size -= 2
        font = ImageFont.truetype(str(TITLE_FONT), size)
    position = (WIDTH * s / 2, HEIGHT * s * 0.745)

    text = Image.new('RGBA', (WIDTH * s, HEIGHT * s), (0, 0, 0, 0))
    ImageDraw.Draw(text).text(position, TITLE, font=font, fill=theme['title'], anchor='mm')
    if theme['shadow']:
        shadow = Image.new('RGBA', (WIDTH * s, HEIGHT * s), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text((position[0], position[1] + 5 * s), TITLE, font=font, fill=theme['shadow'], anchor='mm')
        text = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7 * s)), text)
    return text.resize((WIDTH, HEIGHT), Image.LANCZOS)


def popper_layer():
    """A party popper drawn from shapes, so all banners share one that matches hero.gif."""
    size = 900
    art = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(art)

    # Streamers fly out of the open end of the cone.
    for offset, color, reach in ((-120, '#D6335A', 300), (-40, '#2EB6F0', 345), (45, '#06D6A0', 330), (125, '#FF8FA8', 285)):
        points = []
        for i in range(40):
            p = i / 39
            points.append((450 + offset * (0.35 + p) + math.sin(p * math.tau * 1.3) * 26, 395 - p * reach))
        draw.line(points, fill=color, width=20, joint='curve')
    for x, y, color in ((245, 180, '#FFD166'), (660, 150, '#FFFFFF'), (455, 40, '#FFD166'), (345, 95, '#FFFFFF'), (575, 75, '#FF8FA8')):
        draw.ellipse((x - 19, y - 19, x + 19, y + 19), fill=color)

    # Cone, with diagonal stripes kept inside its outline.
    cone_shape = [(450, 860), (290, 400), (610, 400)]
    cone = Image.new('RGBA', (size, size), '#FFC233')
    stripes = ImageDraw.Draw(cone)
    for y in range(330, 900, 130):
        stripes.polygon([(150, y + 90), (750, y - 60), (750, y + 2), (150, y + 152)], fill='#E8475F')
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).polygon(cone_shape, fill=255)
    art.paste(cone, (0, 0), mask)
    draw.ellipse((290, 362, 610, 438), fill='#7A1F3D')
    draw.arc((290, 362, 610, 438), 0, 360, fill='#FFE29A', width=12)

    art = art.rotate(-32, Image.BICUBIC)
    art = art.resize((int(HEIGHT * 0.48), int(HEIGHT * 0.48)), Image.LANCZOS)
    shadow = Image.new('RGBA', art.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 70), (0, 0), art.getchannel('A'))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))

    layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    place = ((WIDTH - art.width) // 2 - 4, int(HEIGHT * 0.195))
    layer.alpha_composite(shadow, (place[0] + 2, place[1] + 4))
    layer.alpha_composite(art, place)
    return layer


def bottom_strip():
    layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    width = WIDTH / len(STRIP)
    for i, color in enumerate(STRIP):
        draw.rectangle((i * width, HEIGHT - 9, (i + 1) * width, HEIGHT), fill=color)
    return layer


def static_art(theme):
    """Everything that does not move."""
    art = diagonal_gradient(theme['from'], theme['to']).convert('RGBA')
    for layer in (stripes_layer(theme['stripes']), glow_layer(theme['glow']), label_layer(theme),
                  popper_layer(), title_layer(theme), bottom_strip()):
        art.alpha_composite(layer)
    return art.convert('RGB')


def blocked(x, y, margin):
    for left, top, right, bottom in KEEP_CLEAR:
        if left * WIDTH - margin < x < right * WIDTH + margin and top * HEIGHT - margin < y < bottom * HEIGHT + margin:
            return True
    return False


def make_pieces(colors):
    """Confetti floats around the edges. Each piece moves a whole number of cycles per loop, so the GIF repeats without a jump."""
    rng = random.Random(2027)
    pieces = []
    while len(pieces) < PIECES:
        x, y = rng.uniform(14, WIDTH - 14), rng.uniform(12, HEIGHT - 20)
        size = rng.uniform(7, 15)
        if blocked(x, y, size + 13):
            continue
        if any(math.hypot(x - p['x'], y - p['y']) < 34 for p in pieces):
            continue
        pieces.append({
            'x': x, 'y': y, 'size': size,
            'bob': rng.uniform(5, 11),
            'phase': rng.uniform(0, math.tau),
            'turns': rng.choice((-1, 1)),
            'kind': rng.choice(('rect', 'rect', 'rect', 'dot', 'triangle', 'spark', 'spark')),
            'color': colors[len(pieces) % len(colors)],
        })
    return pieces


def polygon_at(cx, cy, angle, points):
    cos, sin = math.cos(angle), math.sin(angle)
    return [(cx + x * cos - y * sin, cy + x * sin + y * cos) for x, y in points]


def draw_piece(draw, piece, t):
    wave = t * math.tau + piece['phase']
    cx = piece['x'] * SCALE
    cy = (piece['y'] + math.sin(wave) * piece['bob']) * SCALE
    size = piece['size'] * SCALE
    angle = piece['phase'] + t * math.tau * piece['turns']
    kind = piece['kind']
    if kind == 'dot':
        r = size * 0.42
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=piece['color'])
    elif kind == 'triangle':
        r = size * 0.72
        draw.polygon(polygon_at(cx, cy, angle, [(0, -r), (r * 0.87, r * 0.5), (-r * 0.87, r * 0.5)]), fill=piece['color'])
    elif kind == 'spark':
        r = size * (0.75 + 0.5 * (0.5 + 0.5 * math.sin(wave * 2)))   # twinkles
        k = r * 0.2
        draw.polygon(polygon_at(cx, cy, 0, [(0, -r), (k, -k), (r, 0), (k, k), (0, r), (-k, k), (-r, 0), (-k, -k)]), fill=piece['color'])
    else:
        flip = 0.4 + 0.6 * abs(math.cos(wave))
        w, h = size * 0.72, size * 0.42 * flip
        draw.polygon(polygon_at(cx, cy, angle, [(-w, -h), (w, -h), (w, h), (-w, h)]), fill=piece['color'])


def confetti_layer(pieces, t):
    layer = Image.new('RGBA', (WIDTH * SCALE, HEIGHT * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for piece in pieces:
        draw_piece(draw, piece, t)
    return layer.resize((WIDTH, HEIGHT), Image.LANCZOS)


def with_confetti(background, pieces, t):
    frame = background.convert('RGBA')
    frame.alpha_composite(confetti_layer(pieces, t))
    return frame.convert('RGB')


def make_banner(name, theme, out_dir):
    pieces = make_pieces(theme['confetti'])
    art = static_art(theme)

    # One palette for all frames. The extra bars make sure the confetti and strip colors are in it.
    sample = Image.new('RGB', (WIDTH, HEIGHT + 80))
    sample.paste(with_confetti(art, pieces, 0), (0, 0))
    swatches = theme['confetti'] + STRIP
    bar = WIDTH / len(swatches)
    bars = ImageDraw.Draw(sample)
    for i, color in enumerate(swatches):
        bars.rectangle((i * bar, HEIGHT, (i + 1) * bar, HEIGHT + 80), fill=color)
    palette = sample.quantize(COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    # Dither the still parts once. Those pixels then stay identical in every frame,
    # so only the confetti adds to the file size and the gradient does not shimmer.
    still = art.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG).convert('RGB')
    frames = [with_confetti(still, pieces, i / FRAMES).quantize(palette=palette, dither=Image.Dither.NONE)
              for i in range(FRAMES)]

    path = out_dir / f'{name}.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=FRAME_MS, loop=0, disposal=1)
    print(f'{path.name}: {path.stat().st_size // 1024} KB')


def main():
    out_dir = Path(__file__).resolve().parent.parent / 'banners'
    out_dir.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        make_banner(name, theme, out_dir)


if __name__ == '__main__':
    main()
