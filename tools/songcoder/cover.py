"""Procedural cover art (1500x1500 JPEG). Style and colors come from song.yaml `cover:`."""
import numpy as np
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1500
FONT = Path(__file__).resolve().parents[2] / "fonts" / "SpaceGrotesk.ttf"


def _hex(c):
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def _vgradient(stops, h=SIZE, w=SIZE):
    """stops: list of (position 0..1, '#rrggbb'). Returns (h, w, 3) float image."""
    pos = np.array([p for p, _ in stops])
    cols = np.array([_hex(c) for _, c in stops])
    y = np.linspace(0, 1, h)
    rows = np.stack([np.interp(y, pos, cols[:, k]) for k in range(3)], axis=1)
    return np.repeat(rows[:, None, :], w, axis=1)


def _stars(img, rng, count, max_y):
    for _ in range(count):
        x, y = rng.integers(0, SIZE), rng.integers(0, int(max_y))
        img[y, x] = np.maximum(img[y, x], 150 + rng.random() * 105)


def _glow(base, layer, radius, strength=1.0):
    """Paint the non-black pixels of layer over base and add a blurred halo."""
    lay = np.asarray(layer, dtype=float)
    blur = np.asarray(layer.filter(ImageFilter.GaussianBlur(radius)), dtype=float)
    a = np.asarray(base, dtype=float).copy()
    mask = lay.sum(axis=2) > 0
    a[mask] = lay[mask]
    a += blur * strength
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def sunset(cfg, rng):
    """Synthwave: striped sun on the horizon over a neon perspective grid."""
    p = {"sky": ["#0b0221", "#3a0a5e", "#b8336a", "#ff8a3d"], "sun": ["#ffe66d", "#ff3d7f"],
         "grid": "#ff3dd4", "ground": "#0a0014", **cfg.get("palette", {})}
    hz = int(SIZE * 0.62)
    sky = _vgradient([(0, p["sky"][0]), (0.35, p["sky"][1]), (0.55, p["sky"][2]), (0.62, p["sky"][3]),
                      (0.621, p["ground"]), (1, p["ground"])])
    _stars(sky, rng, 400, hz * 0.6)
    img = Image.fromarray(sky.astype(np.uint8))
    # sun
    r, cx, cy = 360, SIZE // 2, hz - 60
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    inside = (xx - cx) ** 2 + (yy - cy) ** 2 < r ** 2
    # v runs 0..1 from the top of the sun down to the horizon
    v = np.clip((yy - (cy - r)) / (hz - (cy - r)), 0, 1)
    sun_col = _hex(p["sun"][0]) * (1 - v[..., None]) + _hex(p["sun"][1]) * v[..., None]
    # classic stripes: gaps in the lower half that widen toward the horizon
    w = np.clip((v - 0.45) / 0.55, 0, 1)
    gap = (v > 0.45) & (((v - 0.45) / 0.075) % 1.0 < 0.12 + 0.55 * w)
    mask = inside & ~gap & (yy < hz)
    layer = np.zeros((SIZE, SIZE, 3))
    layer[mask] = sun_col[mask]
    img = _glow(img, Image.fromarray(layer.astype(np.uint8)), 50, 0.45)
    # grid
    grid = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(grid)
    gc = tuple(int(v) for v in _hex(p["grid"]))
    for i in range(-14, 15):
        d.line([(cx + i * 30, hz), (cx + i * 260, SIZE)], fill=gc, width=3)
    for k in range(1, 14):
        y = hz + (SIZE - hz) * (k / 13) ** 2.2
        d.line([(0, y), (SIZE, y)], fill=gc, width=3)
    return _glow(img, grid, 8, 0.8)


def nightcity(cfg, rng):
    """City skyline at night where windows go dark from left to right."""
    p = {"sky": ["#03040c", "#0b1430", "#2a2f5c", "#5b4a6e"], "window": "#ffcf7a",
         "building": "#05060d", "light": "#ff4a5a", **cfg.get("palette", {})}
    sky = _vgradient([(0, p["sky"][0]), (0.45, p["sky"][1]), (0.72, p["sky"][2]), (0.82, p["sky"][3]),
                      (1, p["sky"][1])])
    _stars(sky, rng, 250, SIZE * 0.5)
    img = Image.fromarray(sky.astype(np.uint8))
    d = ImageDraw.Draw(img)
    lights = Image.new("RGB", (SIZE, SIZE))
    dl = ImageDraw.Draw(lights)
    bc = tuple(int(v) for v in _hex(p["building"]))
    wc = _hex(p["window"])
    ground = int(SIZE * 0.84)
    x = -20
    while x < SIZE:
        w = int(rng.integers(70, 190))
        h = int(rng.integers(180, 720))
        top = ground - h
        d.rectangle([x, top, x + w, ground], fill=bc)
        lit_p = 0.55 * (1 - x / SIZE) ** 1.6  # fewer lights further right
        for wy in range(top + 24, ground - 20, 30):
            for wx in range(x + 14, x + w - 18, 24):
                if rng.random() < lit_p:
                    c = tuple(int(v) for v in wc * (0.6 + 0.4 * rng.random()))
                    dl.rectangle([wx, wy, wx + 10, wy + 14], fill=c)
        x += w + int(rng.integers(-10, 18))
    # the last train: a lit streak leaving on a bridge
    d.rectangle([0, ground, SIZE, SIZE], fill=bc)
    track_y = ground + 60
    for i in range(18):
        x0 = 980 + i * 26
        c = tuple(int(v) for v in wc * (1 - i / 22))
        dl.rectangle([x0, track_y, x0 + 20, track_y + 10], fill=c)
    lc = tuple(int(v) for v in _hex(p["light"]))
    dl.ellipse([1460, track_y - 2, 1476, track_y + 14], fill=lc)
    img = _glow(img, lights, 14, 1.2)
    haze = _vgradient([(0, "#000000"), (0.7, "#000000"), (0.84, "#2a2140"), (1, "#000000")])
    a = np.asarray(img, dtype=float) + haze * 0.6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


STYLES = {"sunset": sunset, "nightcity": nightcity}


def _text(img, title, subtitle, color):
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(str(FONT), 124)
    big.set_variation_by_name("Bold")
    small = ImageFont.truetype(str(FONT), 42)
    small.set_variation_by_name("Medium")
    for xy, txt, font in (((90, 100), title.upper(), big), ((96, 250), subtitle, small),
                          ((96, SIZE - 110), "song-coder", small)):
        d.text((xy[0] + 3, xy[1] + 4), txt, font=font, fill=(0, 0, 0))
        d.text(xy, txt, font=font, fill=color)


def make_cover(song, rng, path):
    cfg = song.get("cover", {})
    img = STYLES[cfg.get("style", "nightcity")](cfg, rng)
    sub = cfg.get("subtitle", f"{song.get('genre', '')} · {song['bpm']} BPM · {song.get('key', '')}")
    _text(img, song["title"], sub, cfg.get("text", "#f4f0ff"))
    img.save(path, "JPEG", quality=92)
    return path
