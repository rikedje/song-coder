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


def dawnclock(cfg, rng):
    """Dawn sky with light rays and a large clock face; `hour`/`minute` set the hands."""
    p = {"sky": ["#2b1a4f", "#c94b8a", "#ff9e6b", "#ffe2a0"], "rays": "#fff2c8",
         "clock": "#fff8ec", **cfg.get("palette", {})}
    sky = _vgradient([(0, p["sky"][0]), (0.4, p["sky"][1]), (0.75, p["sky"][2]), (1, p["sky"][3])])
    img = Image.fromarray(sky.astype(np.uint8))
    # soft rays from below the frame
    rays = Image.new("RGB", (SIZE, SIZE))
    dr = ImageDraw.Draw(rays)
    rc = tuple(int(v * 0.22) for v in _hex(p["rays"]))
    ox, oy = SIZE // 2, SIZE + 200
    for a in np.linspace(-1.2, 1.2, 15):
        w = 0.035
        pts = [(ox, oy)] + [(ox + 3000 * np.sin(a + s), oy - 3000 * np.cos(a + s)) for s in (-w, w)]
        dr.polygon(pts, fill=rc)
    # rays are light, so they are added to the sky rather than painted over it
    soft = np.asarray(rays.filter(ImageFilter.GaussianBlur(18)), dtype=float)
    img = Image.fromarray(np.clip(sky + soft, 0, 255).astype(np.uint8))
    # clock
    layer = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(layer)
    cc = tuple(int(v) for v in _hex(p["clock"]))
    cx, cy, r = SIZE // 2, int(SIZE * 0.6), 380
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cc, width=10)
    for k in range(12):
        a = k / 12 * 2 * np.pi
        r0 = r - (60 if k % 3 == 0 else 35)
        d.line([(cx + r0 * np.sin(a), cy - r0 * np.cos(a)),
                (cx + (r - 18) * np.sin(a), cy - (r - 18) * np.cos(a))], fill=cc, width=10 if k % 3 == 0 else 5)
    hour, minute = cfg.get("hour", 5), cfg.get("minute", 0)
    for frac, length, width in (((hour % 12 + minute / 60) / 12, r * 0.52, 18), (minute / 60, r * 0.8, 10)):
        a = frac * 2 * np.pi
        d.line([(cx, cy), (cx + length * np.sin(a), cy - length * np.cos(a))], fill=cc, width=width)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=cc)
    return _glow(img, layer, 22, 0.5)


def nocturne(cfg, rng):
    """Sleepless night: blurred moon behind drifting mist bands, a few faint stars."""
    p = {"sky": ["#04050f", "#0d1433", "#1d2552", "#2b2f5e"], "moon": "#e9e6ff",
         "mist": "#8e8fd6", **cfg.get("palette", {})}
    sky = _vgradient([(0, p["sky"][0]), (0.4, p["sky"][1]), (0.8, p["sky"][2]), (1, p["sky"][3])])
    _stars(sky, rng, 180, SIZE)
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    cx, cy, r = int(SIZE * 0.66), int(SIZE * 0.5), 210
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    moon = _hex(p["moon"])
    disc = np.clip((r - dist) / 4, 0, 1)
    shadow = np.clip((np.sqrt((xx - cx + 90) ** 2 + (yy - cy + 40) ** 2) - r * 0.95) / 6, 0, 1)
    halo = np.exp(-np.maximum(dist - r, 0) / 160) * 0.35
    a = sky + (disc * (0.15 + 0.85 * shadow))[..., None] * moon * 0.9 + halo[..., None] * moon * 0.4
    mist = np.zeros(SIZE)
    for _ in range(6):
        y0, w = rng.uniform(0.45, 0.95) * SIZE, rng.uniform(25, 70)
        mist += np.exp(-((np.arange(SIZE) - y0) / w) ** 2) * rng.uniform(0.08, 0.18)
    a = a + mist[:, None, None] * _hex(p["mist"])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img.filter(ImageFilter.GaussianBlur(1.5))


def circuit(cfg, rng):
    """Circuit board: random right-angle traces with pads, and a house traced in light."""
    p = {"board": ["#04140f", "#0a2a20"], "trace": "#1f6b52", "light": "#7dffcf", **cfg.get("palette", {})}
    img = Image.fromarray(_vgradient([(0, p["board"][0]), (1, p["board"][1])]).astype(np.uint8))
    d = ImageDraw.Draw(img)
    tc = tuple(int(v) for v in _hex(p["trace"]))
    grid = 50
    for _ in range(120):
        x, y = (int(v) for v in rng.integers(0, SIZE // grid, 2) * grid)
        pts = [(x, y)]
        for _ in range(int(rng.integers(2, 6))):
            if rng.random() < 0.5:
                x += int(rng.integers(-6, 7)) * grid
            else:
                y += int(rng.integers(-6, 7)) * grid
            pts.append((x, y))
        d.line(pts, fill=tc, width=5, joint="curve")
        for px, py in (pts[0], pts[-1]):
            d.ellipse([px - 11, py - 11, px + 11, py + 11], outline=tc, width=5)
    # the house: walls, roof, door and a window, drawn as lit traces
    layer = Image.new("RGB", (SIZE, SIZE))
    dl = ImageDraw.Draw(layer)
    lc = tuple(int(v) for v in _hex(p["light"]))
    cx, base, w, h = SIZE // 2, int(SIZE * 0.86), 520, 380
    wall = [(cx - w // 2, base), (cx - w // 2, base - h), (cx, base - h - 260),
            (cx + w // 2, base - h), (cx + w // 2, base), (cx - w // 2, base)]
    dl.line(wall, fill=lc, width=10, joint="curve")
    dl.rectangle([cx - 60, base - 200, cx + 60, base], outline=lc, width=8)
    dl.rectangle([cx + 120, base - 300, cx + 220, base - 200], outline=lc, width=8)
    dl.rectangle([cx - 220, base - 300, cx - 120, base - 200], fill=lc)
    for px, py in wall[:5]:
        dl.ellipse([px - 18, py - 18, px + 18, py + 18], fill=lc)
    return _glow(img, layer, 18, 0.9)


def rainwindow(cfg, rng):
    """Looking out through a wet window at blurred warm lights."""
    p = {"sky": ["#1b2a33", "#24394a", "#3a4a52"], "bokeh": ["#ffb35c", "#ffd9a0", "#6fc3c9"],
         **cfg.get("palette", {})}
    base = Image.fromarray(_vgradient([(0, p["sky"][0]), (0.6, p["sky"][1]), (1, p["sky"][2])]).astype(np.uint8))
    bokeh = Image.new("RGB", (SIZE, SIZE))
    db_ = ImageDraw.Draw(bokeh)
    for _ in range(70):
        x, y = rng.uniform(0, SIZE), rng.uniform(SIZE * 0.35, SIZE)
        r = rng.uniform(30, 110)
        c = _hex(p["bokeh"][int(rng.integers(0, len(p["bokeh"])))]) * rng.uniform(0.25, 0.6)
        db_.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v) for v in c))
    bokeh = bokeh.filter(ImageFilter.GaussianBlur(28))
    a = np.asarray(base, dtype=float) + np.asarray(bokeh, dtype=float)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # droplets and streaks on the glass
    glass = Image.new("RGB", (SIZE, SIZE))
    dg = ImageDraw.Draw(glass)
    for _ in range(420):
        x, y = rng.uniform(0, SIZE), rng.uniform(0, SIZE)
        r = rng.uniform(3, 13)
        dg.ellipse([x - r, y - r, x + r, y + r], outline=(150, 170, 180), width=2)
        dg.ellipse([x - r * 0.3, y - r * 0.6, x + r * 0.1, y - r * 0.2], fill=(220, 230, 235))
    for _ in range(22):
        x, y0 = rng.uniform(0, SIZE), rng.uniform(0, SIZE * 0.7)
        y1 = y0 + rng.uniform(120, 420)
        pts = [(x + 6 * np.sin(k / 3) * rng.random(), y0 + (y1 - y0) * k / 20) for k in range(21)]
        dg.line(pts, fill=(120, 140, 150), width=4)
    a = np.asarray(img, dtype=float) + np.asarray(glass.filter(ImageFilter.GaussianBlur(1)), dtype=float) * 0.6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def hyperspace(cfg, rng):
    """Stars stretched into streaks rushing out from a bright vanishing point."""
    p = {"space": ["#02030a", "#0a0f2a"], "streak": ["#9fd8ff", "#ffffff", "#c9a6ff"], "core": "#bfe6ff",
         **cfg.get("palette", {})}
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    cx, cy = SIZE * 0.5, SIZE * 0.58
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / SIZE
    base = _hex(p["space"][1]) * np.exp(-r * 3)[..., None] + _hex(p["space"][0])
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    layer = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(layer)
    for _ in range(520):
        a = rng.uniform(0, 2 * np.pi)
        r0 = rng.uniform(40, 700) ** 1.0
        length = r0 * rng.uniform(0.2, 0.9)
        c = _hex(p["streak"][int(rng.integers(0, len(p["streak"])))]) * rng.uniform(0.3, 1.0)
        x0, y0 = cx + r0 * np.cos(a), cy + r0 * np.sin(a)
        x1, y1 = cx + (r0 + length) * np.cos(a), cy + (r0 + length) * np.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=tuple(int(v) for v in c), width=max(1, int(r0 / 160)))
    core = Image.new("RGB", (SIZE, SIZE))
    ImageDraw.Draw(core).ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=tuple(int(v) for v in _hex(p["core"])))
    a = (np.asarray(img, dtype=float) + np.asarray(layer.filter(ImageFilter.GaussianBlur(1.2)), dtype=float)
         + np.asarray(layer.filter(ImageFilter.GaussianBlur(8)), dtype=float) * 0.8
         + np.asarray(core.filter(ImageFilter.GaussianBlur(60)), dtype=float) * 2.0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def geometric(cfg, rng):
    """Early-80s print look: flat colour blocks, bars and circles, and a coiled phone cord."""
    p = {"paper": "#efe8d8", "colors": ["#c8102e", "#141414", "#1d6e7a", "#e8b100"], **cfg.get("palette", {})}
    img = Image.new("RGB", (SIZE, SIZE), tuple(int(v) for v in _hex(p["paper"])))
    d = ImageDraw.Draw(img)
    cols = [tuple(int(v) for v in _hex(c)) for c in p["colors"]]
    d.rectangle([0, int(SIZE * 0.62), SIZE, SIZE], fill=cols[1])
    d.ellipse([820, 430, 1340, 950], fill=cols[0])
    for k in range(6):
        y = 470 + k * 70
        d.rectangle([120, y, 700 - k * 60, y + 34], fill=cols[2] if k % 2 else cols[1])
    d.polygon([(1100, 1500), (1500, 1100), (1500, 1500)], fill=cols[3])
    # coiled telephone cord running across the dark band
    t = np.linspace(0, 1, 2000)
    xs = 80 + t * 1340 + 26 * np.cos(t * 2 * np.pi * 28)
    ys = SIZE * 0.78 + 60 * np.sin(t * 2 * np.pi * 1.2) + 26 * np.sin(t * 2 * np.pi * 28)
    d.line(list(zip(xs, ys)), fill=tuple(int(v) for v in _hex(p["paper"])), width=7)
    return img


def _gear(d, cx, cy, r, teeth, fill, hole):
    pts = []
    for k in range(teeth * 4):
        a = k / (teeth * 4) * 2 * np.pi
        rr = r if (k // 2) % 2 == 0 else r * 0.82
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    d.polygon(pts, fill=fill)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=hole)


def gears(cfg, rng):
    """Interlocking gear silhouettes on a hard two-colour ground."""
    p = {"ground": "#b3121b", "gear": "#0d0d0d", "accent": "#e9e4da", **cfg.get("palette", {})}
    g = tuple(int(v) for v in _hex(p["ground"]))
    img = Image.new("RGB", (SIZE, SIZE), g)
    d = ImageDraw.Draw(img)
    a = tuple(int(v) for v in _hex(p["accent"]))
    for i in range(4):
        d.rectangle([0, 360 + i * 44, SIZE, 368 + i * 44], fill=a)
    # three gears placed so their teeth mesh instead of overlapping
    k = tuple(int(v) for v in _hex(p["gear"]))
    big, mid, small = (470, 1060, 390, 14), None, None
    ang1, ang2 = np.radians(-40), np.radians(55)
    d1 = (390 + 270) * 0.9
    mid = (big[0] + d1 * np.cos(ang1), big[1] + d1 * np.sin(ang1), 270, 10)
    d2 = (270 + 170) * 0.9
    small = (mid[0] + d2 * np.cos(ang2), mid[1] + d2 * np.sin(ang2), 170, 7)
    for cx, cy, r, teeth in (big, mid, small):
        _gear(d, cx, cy, r, teeth, k, g)
    return img


STYLES = {"gears": gears, "geometric": geometric, "hyperspace": hyperspace, "rainwindow": rainwindow, "sunset": sunset, "nightcity": nightcity, "dawnclock": dawnclock, "nocturne": nocturne,
          "circuit": circuit}


def _wrap(d, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = f"{cur} {word}".strip()
        if cur and d.textlength(t, font=font) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = t
    return lines + [cur]


def _text(img, title, subtitle, color, footer=None):
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(str(FONT), 124)
    big.set_variation_by_name("Bold")
    small = ImageFont.truetype(str(FONT), 42)
    small.set_variation_by_name("Medium")
    lines = _wrap(d, title.upper(), big, SIZE - 180)
    items = [((90, 100 + 140 * k), line, big) for k, line in enumerate(lines)]
    items = [(xy, txt, font, color) for xy, txt, font in items]
    items += [((96, 250 + 140 * (len(lines) - 1)), subtitle, small, color),
              ((96, SIZE - 110), "song-coder", small, footer or color)]
    for xy, txt, font, col in items:
        if _hex(col).mean() > 128:  # a drop shadow only helps light text
            d.text((xy[0] + 3, xy[1] + 4), txt, font=font, fill=(0, 0, 0))
        d.text(xy, txt, font=font, fill=col)


def make_cover(song, rng, path):
    cfg = song.get("cover", {})
    img = STYLES[cfg.get("style", "nightcity")](cfg, rng)
    sub = cfg.get("subtitle", f"{song.get('genre', '')} · {song['bpm']} BPM · {song.get('key', '')}")
    _text(img, song["title"], sub, cfg.get("text", "#f4f0ff"), cfg.get("footer"))
    img.save(path, "JPEG", quality=92)
    return path
