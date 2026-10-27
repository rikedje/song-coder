"""Pitched synth voices. Each render function returns a stereo (2, n) note."""
import numpy as np

from .dsp import SR, adsr, ensemble, osc_pulse, osc_saw, osc_sine, soft_clip, svf


def _cents(c):
    return 2 ** (c / 1200)


def distbass(freq, n_gate, vel, p, cm, rng):
    env = adsr(n_gate, 0.002, p.get("decay", 0.16), p.get("sustain", 0.65), 0.04)
    n = env.shape[0]
    t = np.arange(n) / SR
    f = np.full(n, freq)
    x = osc_saw(f, rng.random()) + 0.7 * osc_saw(f * _cents(9), rng.random())
    x += 0.5 * osc_pulse(f * 0.5, rng.random(), 0.5)
    cutoff = p.get("cutoff", 700) * cm * (1 + p.get("env_amount", 4.0) * np.exp(-t / 0.06))
    x = svf(x, cutoff, p.get("resonance", 1.3), 0)
    x = soft_clip(x, p.get("drive", 3.0))
    x = svf(x, np.full(n, p.get("tone", 3500.0)), 0.707, 0)
    sub_f = freq if freq < 100 else freq / 2
    x += p.get("sub", 0.6) * osc_sine(np.full(n, sub_f), 0.0)
    y = x * env * vel
    return np.stack([y, y])


def pluck(freq, n_gate, vel, p, cm, rng):
    env = adsr(n_gate, 0.001, p.get("decay", 0.18), p.get("sustain", 0.12), 0.1)
    n = env.shape[0]
    t = np.arange(n) / SR
    cutoff = p.get("cutoff", 2500) * cm * (1 + p.get("env_amount", 6.0) * np.exp(-t / 0.05))
    out = []
    for det in (-6, 6):
        f = np.full(n, freq * _cents(det))
        x = osc_saw(f, rng.random()) + 0.6 * osc_pulse(f, rng.random(), 0.3)
        out.append(svf(x, cutoff, p.get("resonance", 2.0), 0) * env * vel)
    return np.stack(out)


def _unison(freq, n, voices, spread, rng, kind="saw"):
    """Detuned unison stack, alternately panned. Returns (2, n)."""
    out = np.zeros((2, n))
    for v in range(voices):
        c = spread * (2 * v / (voices - 1) - 1) if voices > 1 else 0.0
        f = np.full(n, freq * _cents(c))
        x = osc_saw(f, rng.random()) if kind == "saw" else osc_pulse(f, rng.random(), 0.45)
        side = (v % 2) * 2 - 1
        w = 0.5 + 0.35 * side * (abs(c) / spread if spread else 0)
        out[0] += x * (1 - w)
        out[1] += x * w
    return out / np.sqrt(voices)


def superpad(freq, n_gate, vel, p, cm, rng):
    env = adsr(n_gate, p.get("attack", 0.35), 0.8, 0.85, p.get("release", 0.9))
    n = env.shape[0]
    x = _unison(freq, n, p.get("voices", 7), p.get("spread", 18), rng)
    t = np.arange(n) / SR
    lfo = 1 + 0.25 * np.sin(2 * np.pi * 0.15 * t + rng.random() * 6.28)
    cutoff = p.get("cutoff", 1800) * cm * lfo
    x = np.stack([svf(x[c], cutoff, p.get("resonance", 0.9), 0) for c in range(2)])
    return x * env * vel


def superlead(freq, n_gate, vel, p, cm, rng):
    env = adsr(n_gate, 0.006, 0.3, 0.8, p.get("release", 0.25))
    n = env.shape[0]
    t = np.arange(n) / SR
    vib = 1 + (_cents(10) - 1) * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    x = np.zeros((2, n))
    for v in range(p.get("voices", 5)):
        c = p.get("spread", 12) * (2 * v / 4 - 1)
        f = freq * _cents(c) * vib
        s = osc_saw(f, rng.random())
        w = 0.5 + 0.3 * (c / p.get("spread", 12))
        x[0] += s * (1 - w)
        x[1] += s * w
    sub = 0.35 * osc_pulse(freq * 0.5 * vib, 0.0, 0.5)
    x += sub
    cutoff = p.get("cutoff", 4500) * cm * (1 + 1.5 * np.exp(-t / 0.15))
    x = np.stack([svf(x[c], cutoff, p.get("resonance", 1.4), 0) for c in range(2)])
    x = soft_clip(x * 0.6, p.get("drive", 1.6))
    return x * env * vel


def softbass(freq, n_gate, vel, p, cm, rng):
    """Clean, warm analog-style bass: filtered saw over a sine sub, no drive."""
    env = adsr(n_gate, 0.006, p.get("decay", 0.35), p.get("sustain", 0.7), 0.09)
    n = env.shape[0]
    t = np.arange(n) / SR
    f = np.full(n, freq)
    x = osc_saw(f, rng.random()) + 0.5 * osc_saw(f * _cents(5), rng.random())
    cutoff = p.get("cutoff", 420) * cm * (1 + p.get("env_amount", 1.5) * np.exp(-t / 0.08))
    x = svf(x, cutoff, p.get("resonance", 0.8), 0) * 0.6
    x += p.get("sub", 0.8) * osc_sine(f, 0.0)
    y = x * env * vel
    return np.stack([y, y])


def epiano(freq, n_gate, vel, p, cm, rng):
    """Two-operator FM electric piano with tine attack and stereo tremolo."""
    env = adsr(n_gate, 0.003, p.get("decay", 1.4), p.get("sustain", 0.12), p.get("release", 0.45))
    n = env.shape[0]
    t = np.arange(n) / SR
    index = p.get("index", 1.6) * vel * np.exp(-t / 0.3) + 0.25
    mod = np.sin(2 * np.pi * freq * t)
    tine = 0.35 * vel * np.exp(-t / 0.02) * np.sin(2 * np.pi * freq * 14 * t)
    x = np.sin(2 * np.pi * freq * t + index * mod + tine)
    x = svf(x, np.full(n, p.get("cutoff", 5000) * cm), 0.707, 0)
    trem = p.get("tremolo", 0.25) * np.sin(2 * np.pi * p.get("tremolo_hz", 4.2) * t)
    y = x * env * vel
    return np.stack([y * (1 + trem), y * (1 - trem)])


def piano(freq, n_gate, vel, p, cm, rng):
    """Bright additive house piano: slightly inharmonic, two detuned strings, hammer click."""
    env = adsr(n_gate, 0.002, p.get("decay", 2.0), p.get("sustain", 0.0), p.get("release", 0.25))
    n = env.shape[0]
    t = np.arange(n) / SR
    out = np.zeros((2, n))
    bright = p.get("brightness", 1.0) * cm
    for k in range(1, p.get("partials", 14) + 1):
        fk = k * freq * np.sqrt(1 + 0.0004 * k * k)
        if fk > 16000:
            break
        amp = k ** -1.1 * vel ** ((k - 1) / (6 * bright))
        dec = np.exp(-t * (0.6 + 0.35 * k / bright))
        for c, det in enumerate((-1.5, 1.5)):
            ph = rng.random() * 6.28
            out[c] += amp * dec * np.sin(2 * np.pi * fk * _cents(det) * t + ph)
    hammer = lowpass_noise(n, rng) * np.exp(-t / 0.004) * 0.25
    out += hammer
    return out * env * vel * 0.5


def bell(freq, n_gate, vel, p, cm, rng):
    """Soft FM bell: inharmonic modulator, gentle attack, long ring, lowpassed."""
    n = int((n_gate / SR + p.get("ring", 4.0)) * SR)
    t = np.arange(n) / SR
    att = np.clip(t / p.get("attack", 0.03), 0, 1)
    env = att * np.exp(-t / p.get("decay", 1.6))
    index = p.get("index", 1.2) * np.exp(-t / 0.8)
    out = []
    for det in (-3, 3):
        f = freq * _cents(det)
        mod = np.sin(2 * np.pi * f * p.get("ratio", 3.5) * t + rng.random() * 6.28)
        x = np.sin(2 * np.pi * f * t + index * mod)
        out.append(svf(x, np.full(n, p.get("cutoff", 4000) * cm), 0.707, 0))
    return np.stack(out) * env * vel * 0.6


def mono(freq, n_gate, vel, p, cm, rng):
    """Vintage monosynth: one oscillator that restarts at phase 0, filter envelope, no unison."""
    env = adsr(n_gate, p.get("attack", 0.002), p.get("decay", 0.15), p.get("sustain", 0.5),
               p.get("release", 0.05))
    n = env.shape[0]
    t = np.arange(n) / SR
    f = np.full(n, freq)
    if p.get("vibrato"):
        # cents depth, after a short delay, like a game sound driver
        ramp = np.clip((t - p.get("vibrato_delay", 0.15)) / 0.1, 0, 1)
        f = f * _cents(p["vibrato"] * ramp * np.sin(2 * np.pi * p.get("vibrato_hz", 6.0) * t))
    osc = p.get("osc", "pulse")
    if osc == "saw":
        x = osc_saw(f, 0.0)
    elif osc == "sine":
        x = osc_sine(f, 0.0)
    elif osc == "tri4":
        x = _tri4(f)
    else:
        x = osc_pulse(f, 0.0, p.get("width", 0.5))
    if osc not in ("sine", "tri4") and p.get("filter", True):
        cutoff = p.get("cutoff", 2000) * cm * (1 + p.get("env_amount", 3.0) * np.exp(-t / p.get("env_decay", 0.06)))
        x = svf(x, cutoff, p.get("resonance", 1.2), 0)
    y = x * env * vel
    return np.stack([y, y])


def strings(freq, n_gate, vel, p, cm, rng):
    """Vintage string machine: divide-down saw at 8' and 4', slow envelope, ensemble chorus."""
    env = adsr(n_gate, p.get("attack", 0.35), 1.0, 0.95, p.get("release", 1.0))
    n = env.shape[0]
    f = np.full(n, freq)
    x = osc_saw(f, 0.0) + p.get("octave", 0.5) * osc_saw(f * 2, 0.0)
    x = svf(x, np.full(n, p.get("cutoff", 3000) * cm), 0.8, 0)
    x = svf(x, np.full(n, 180.0), 0.7, 2)
    return ensemble(x * env * vel * 0.5, p.get("depth", 0.0012), p.get("rate", 0.6))


def _tri4(f):
    """4-bit stepped triangle, as in old console sound chips (16 levels, no filtering)."""
    ph = np.cumsum(f / SR) % 1.0
    tri = 1 - 4 * np.abs(ph - 0.5)
    return np.round((tri + 1) * 7.5) / 7.5 - 1


def chiparp(freqs, n_gate, vel, p, cm, rng):
    """Chip-style chord: one pulse voice cycling through the chord notes at frame rate."""
    env = adsr(n_gate, 0.001, p.get("decay", 0.3), p.get("sustain", 0.6), p.get("release", 0.02))
    n = env.shape[0]
    frame = int(SR / p.get("rate", 50.0))
    idx = (np.arange(n) // frame) % len(freqs)
    f = np.asarray(freqs)[idx]
    x = osc_pulse(f, 0.0, p.get("width", 0.25))
    y = x * env * vel
    return np.stack([y, y])


def lowpass_noise(n, rng):
    return svf(rng.standard_normal(n), np.full(n, 3000.0), 0.707, 0)


INSTRUMENTS = {
    "piano": piano,
    "mono": mono,
    "chiparp": chiparp,
    "strings": strings,
    "bell": bell,
    "distbass": distbass,
    "softbass": softbass,
    "pluck": pluck,
    "epiano": epiano,
    "superpad": superpad,
    "superlead": superlead,
}
