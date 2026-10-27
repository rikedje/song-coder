"""Synthesized drum and FX one-shots. Each returns a stereo (2, n) sample."""
import numpy as np

from .dsp import SR, bandpass, decay, highpass, lowpass, osc_pulse, osc_sine, soft_clip, svf


def kick(p, rng):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    f0, f1 = p.get("pitch_hi", 190.0), p.get("pitch_lo", 47.0)
    freq = f1 + (f0 - f1) * np.exp(-t / 0.032)
    body = osc_sine(freq, 0.0) * np.exp(-t / p.get("decay", 0.22))
    click = highpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.003) * 0.5
    x = soft_clip(body + click, p.get("drive", 2.4))
    x *= np.minimum(1, (n - np.arange(n)) / 400)
    return np.stack([x, x])


def snare(p, rng):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    tone = osc_sine(np.full(n, 185.0) * (1 + 0.6 * np.exp(-t / 0.01)), 0.0) * np.exp(-t / 0.07)
    noise = rng.standard_normal(n)
    noise = bandpass(noise, 3500, 0.6) * np.exp(-t / p.get("decay", 0.17))
    clap = np.zeros(n)
    for k, off in enumerate((0.0, 0.011, 0.022)):
        s = int(off * SR)
        tt = t[: n - s]
        clap[s:] += np.exp(-tt / (0.006 if k < 2 else 0.09))
    clap = bandpass(rng.standard_normal(n), 1400, 1.2) * clap
    x = 0.7 * tone + 1.0 * noise + 0.9 * clap
    x = soft_clip(x, p.get("drive", 1.8))
    return np.stack([x, x])


def _metal(n, rng):
    freqs = np.array([205.3, 304.4, 369.6, 522.7, 540.0, 800.0]) * 1.7
    x = sum(osc_pulse(np.full(n, f), rng.random(), 0.5) for f in freqs)
    return x / len(freqs) + 0.6 * rng.standard_normal(n)


def hat(p, rng):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    x = highpass(_metal(n, rng), 7500, 0.9) * np.exp(-t / p.get("decay", 0.03))
    return np.stack([x, x])


def ohat(p, rng):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    x = highpass(_metal(n, rng), 6500, 0.9) * np.exp(-t / p.get("decay", 0.16))
    return np.stack([x, x])


def crash(p, rng):
    n = int(2.8 * SR)
    t = np.arange(n) / SR
    out = []
    for _ in range(2):
        x = highpass(_metal(n, rng) + rng.standard_normal(n), 3200, 0.7)
        out.append(x * np.exp(-t / 0.7) * (0.6 + 0.4 * np.exp(-t / 0.05)))
    return np.stack(out) * 0.5


def riser(p, rng, seconds):
    n = int(seconds * SR)
    t = np.arange(n) / seconds / SR
    cutoff = 200 * (8000 / 200) ** (t ** 1.5)
    out = []
    for _ in range(2):
        x = svf(rng.standard_normal(n), cutoff, 3.0, 1)
        out.append(x)
    amp = t ** 2
    tone = osc_pulse(110 * 2 ** (2 * t), 0.0, 0.5) * 0.15
    x = np.stack(out) * 0.6 + tone
    return x * amp


def impact(p, rng):
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    boom = osc_sine(42 + 60 * np.exp(-t / 0.08), 0.0) * np.exp(-t / 0.9)
    hit = lowpass(rng.standard_normal(n), 900) * np.exp(-t / 0.25)
    x = soft_clip(boom + 0.8 * hit, 1.5)
    return np.stack([x, x])


def downlifter(p, rng, seconds):
    n = int(seconds * SR)
    t = np.arange(n) / seconds / SR
    cutoff = 8000 * (150 / 8000) ** (t ** 0.6)
    x = np.stack([svf(rng.standard_normal(n), cutoff, 2.5, 1) for _ in range(2)])
    return x * (1 - t) ** 2 * 0.6


def etom(p, rng):
    """Electronic tom: sine with a fast pitch drop, a touch of noise, no drive."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f0 = p.get("pitch", 160.0)
    freq = f0 * (1 + p.get("sweep", 1.0) * np.exp(-t / 0.04))
    x = osc_sine(freq, 0.0) * np.exp(-t / p.get("decay", 0.18))
    x += bandpass(rng.standard_normal(n), f0 * 4, 1.0) * np.exp(-t / 0.01) * 0.15
    return np.stack([x, x])


DRUMS = {"kick": kick, "snare": snare, "hat": hat, "ohat": ohat, "etom": etom}
FX = {"crash": crash, "impact": impact, "riser": riser, "downlifter": downlifter}
