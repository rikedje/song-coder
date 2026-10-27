"""Pitched synth voices. Each render function returns a stereo (2, n) note."""
import numpy as np

from .dsp import SR, adsr, osc_pulse, osc_saw, osc_sine, soft_clip, svf


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


INSTRUMENTS = {
    "distbass": distbass,
    "pluck": pluck,
    "superpad": superpad,
    "superlead": superlead,
}
