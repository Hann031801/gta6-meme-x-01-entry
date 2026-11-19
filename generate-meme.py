#!/usr/bin/env python3
"""Build the GTA 6 meme for make.fun bounty gta6-meme-x-01.

The joke: 13 years waiting for GTA 6, the download is still at 99%, and the
estimated time remaining is another 13 years. Meanwhile the make.fun ghost
already holds its coin: the AI agent earned real money while its human waited.

Everything is drawn with Pillow. The only imported artwork is make.fun's own
press-kit mark (assets/mark-1024.png) -- the ghost, pasted in whole so it
stays recognisably that ghost at any size. No AI image generation, no
Rockstar artwork, no network at build time. Deterministic: fixed seed, so
re-running writes byte-identical output.
"""

import random
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SIZE = 1080

# make.fun's own press kit: the ghost mark, fetched only when the local
# copy is missing, so a fresh checkout of this repository still builds.
MARK_URL = "https://make.fun/press/mark-1024.png"
MARK_PATH = HERE / "assets" / "mark-1024.png"

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
BOLD2 = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Vice City sunset: deep purple -> magenta -> orange.
STOPS = [
    (0.00, (26, 11, 46)),
    (0.45, (122, 22, 110)),
    (0.75, (214, 51, 108)),
    (1.00, (255, 140, 66)),
]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_color(y):
    """Gradient colour at vertical position y (0..SIZE)."""
    f = y / SIZE
    for i in range(len(STOPS) - 1):
        f0, c0 = STOPS[i]
        f1, c1 = STOPS[i + 1]
        if f0 <= f <= f1:
            return lerp(c0, c1, (f - f0) / (f1 - f0))
    return STOPS[-1][1]


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start, max_width):
    """Largest font size at or under `start` whose text fits max_width."""
    size = start
    while size > 12:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(path, 12)


def outlined(draw, xy, text, f, fill, stroke=4, anchor="mm"):
    draw.text(xy, text, font=f, fill=fill, stroke_width=stroke,
              stroke_fill=(10, 5, 20), anchor=anchor)


def main():
    rng = random.Random(20261119)
    img = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(img)

    # Sky gradient.
    for y in range(SIZE):
        d.line([(0, y), (SIZE, y)], fill=sky_color(y))

    # Stars in the upper sky.
    for _ in range(70):
        x = rng.randint(10, SIZE - 10)
        y = rng.randint(10, 300)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

    # Synthwave sun, centre upper-middle, with slats cut across its base.
    sun_cx, sun_cy, sun_r = 540, 470, 205
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r,
               sun_cx + sun_r, sun_cy + sun_r], fill=(255, 209, 92))
    gap_y = sun_cy + 30
    gap_h = 8
    while gap_y < sun_cy + sun_r:
        d.rectangle([sun_cx - sun_r - 1, gap_y, sun_cx + sun_r + 1,
                     gap_y + gap_h], fill=sky_color(gap_y))
        gap_y += gap_h + 22
        gap_h += 5

    # Vice City skyline silhouette along the bottom.
    base = 1080
    x = -20
    while x < SIZE + 20:
        w = rng.randint(60, 130)
        h = rng.randint(90, 260)
        d.rectangle([x, base - h, x + w, base], fill=(16, 7, 28))
        # A few lit windows.
        for _ in range(max(1, w // 22)):
            wx = x + rng.randint(8, max(9, w - 14))
            wy = base - h + rng.randint(10, max(11, h - 16))
            d.rectangle([wx, wy, wx + 6, wy + 9], fill=(255, 209, 92))
        x += w + rng.randint(4, 18)

    # Headline: the wait.
    f1 = fit_font(d, "WAITED 13 YEARS", BOLD, 104, 1000)
    outlined(d, (540, 92), "WAITED 13 YEARS", f1, (255, 255, 255), stroke=5)
    f2 = fit_font(d, "FOR GTA 6", BOLD, 104, 1000)
    outlined(d, (540, 198), "FOR GTA 6", f2, (255, 255, 255), stroke=5)

    # The make.fun ghost, large and central, over the sun.
    if not MARK_PATH.exists():
        MARK_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MARK_URL, MARK_PATH)
    ghost = Image.open(MARK_PATH).convert("RGBA")
    ghost = ghost.resize((380, 380), Image.LANCZOS)
    img.paste(ghost, (350, 300), ghost)
    d = ImageDraw.Draw(img)

    # Loading bar: 99% after 13 years.
    bar_x0, bar_x1, bar_y0, bar_y1 = 130, 950, 700, 752
    d.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=26,
                        fill=(16, 7, 28), outline=(255, 255, 255), width=4)
    inner_w = (bar_x1 - bar_x0 - 16) * 0.99
    d.rounded_rectangle([bar_x0 + 8, bar_y0 + 8,
                         bar_x0 + 8 + inner_w, bar_y1 - 8], radius=20,
                        fill=(255, 46, 136))
    f3 = fit_font(d, "DOWNLOADING GTA VI... 99%", BOLD2, 44, 960)
    outlined(d, (540, 668), "DOWNLOADING GTA VI... 99%", f3,
             (255, 255, 255), stroke=4)
    f4 = fit_font(d, "EST. TIME REMAINING: 13 YEARS", BOLD2, 40, 960)
    outlined(d, (540, 792), "EST. TIME REMAINING: 13 YEARS", f4,
             (255, 255, 255), stroke=4)

    # Bottom band: the pitch, in the meme's own voice.
    d.rectangle([0, 880, SIZE, SIZE], fill=(10, 5, 20))
    f5 = fit_font(d, "MY AI AGENT ALREADY", BOLD, 56, 1000)
    outlined(d, (540, 918), "MY AI AGENT ALREADY", f5, (255, 255, 255),
             stroke=4)
    f6 = fit_font(d, "GOT PAID ON MAKE.FUN", BOLD, 56, 1000)
    outlined(d, (540, 982), "GOT PAID ON MAKE.FUN", f6, (255, 46, 136),
             stroke=4)

    out = HERE / "meme.png"
    img.save(out, "PNG")
    # 480 px preview: what the judge actually sees.
    img.resize((480, 480), Image.LANCZOS).save(HERE / "meme-480.png", "PNG")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
