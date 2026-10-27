"""Synthesized drum and FX one-shots. Each returns a stereo (2, n) sample."""
import numpy as np

from .dsp import SR, bandpass, decay, highpass, lowpass, osc_pulse, osc_sine, soft_clip, sos_filter, svf


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


def _fade(x, seconds):
    k = min(int(seconds * SR), x.shape[1] // 2)
    ramp = np.linspace(0, 1, k)
    x[:, :k] *= ramp
    x[:, -k:] *= ramp[::-1]
    return x


def rain(p, rng, seconds):
    """Rain on a window: soft broadband hiss plus scattered droplets."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    hiss = sos_filter(rng.standard_normal((2, n)), "bandpass", [400, 6000])
    hiss *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t + rng.random() * 6.28)
    imp = np.zeros((2, n))
    count = int(seconds * 30)
    pos = rng.integers(0, n, count)
    imp[rng.integers(0, 2, count), pos] = rng.exponential(1.0, count)
    drops = np.stack([svf(imp[c], np.full(n, 2600.0), 4.0, 1) for c in range(2)])
    return _fade(0.12 * hiss + 0.5 * drops, 2.0)


def vinyl(p, rng, seconds):
    """Record surface: faint hiss, crackle and the odd pop."""
    n = int(seconds * SR)
    hiss = sos_filter(rng.standard_normal((2, n)), "bandpass", [1500, 9000]) * 0.04
    imp = np.zeros(n)
    count = int(seconds * 12)
    imp[rng.integers(0, n, count)] = rng.exponential(1.0, count) * rng.choice([-1, 1], count)
    crackle = sos_filter(imp, "highpass", 1800)
    pops = np.zeros(n)
    big = int(seconds * 0.4)
    pops[rng.integers(0, n, big)] = rng.uniform(1.5, 3.0, big)
    pops = sos_filter(pops, "lowpass", 900)
    x = hiss + (crackle + pops)[None, :] * 0.5
    return _fade(x, 1.0)


def metal(p, rng):
    """Metallic clank, like a sampled anvil or pipe: inharmonic partials with fast decays."""
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f0 = p.get("pitch", 420.0)
    x = np.zeros(n)
    for ratio, amp, tau in ((1.0, 1.0, 0.12), (2.76, 0.7, 0.07), (5.40, 0.5, 0.04), (8.93, 0.35, 0.025)):
        x += amp * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t / (tau * p.get("decay", 1.0)))
    x += highpass(rng.standard_normal(n), 2000) * np.exp(-t / 0.004) * 0.6
    return np.stack([x, x]) * 0.5


def timpani(p, rng):
    """Tuned kettle drum: membrane modes (1, 1.5, 1.98, 2.44) with a slight pitch settle and a felt mallet."""
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    f0 = p.get("pitch", 55.0)
    glide = 1 + 0.03 * np.exp(-t / 0.05)
    x = np.zeros(n)
    for ratio, amp, tau in ((1.0, 1.0, 1.1), (1.5, 0.5, 0.6), (1.98, 0.3, 0.4), (2.44, 0.15, 0.25)):
        x += amp * osc_sine(f0 * ratio * glide, 0.0) * np.exp(-t / (tau * p.get("decay", 1.0)))
    x += lowpass(rng.standard_normal(n), 700) * np.exp(-t / 0.015) * 0.6
    return np.stack([x, x]) * 0.6


def zap(p, rng):
    """Space-age zap: a resonant sine falling fast in pitch."""
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 200 + 3200 * np.exp(-t / 0.07)
    x = osc_sine(f, 0.0) * np.exp(-t / 0.15)
    return np.stack([x, np.concatenate([np.zeros(400), x[:-400]])]) * 0.5


def _chipnoise(n, rate, rng):
    """Console-style noise: random +/-1 held for `rate`-Hz steps (no filtering)."""
    hold = max(1, int(SR / rate))
    steps = rng.choice([-1.0, 1.0], n // hold + 1)
    return np.repeat(steps, hold)[:n]


def chipkick(p, rng):
    """Triangle pitch drop, the way 8-bit games fake a kick."""
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    f = 50 + 300 * np.exp(-t / 0.02)
    ph = np.cumsum(f / SR) % 1.0
    tri = np.round((1 - 4 * np.abs(ph - 0.5) + 1) * 7.5) / 7.5 - 1
    x = tri * np.exp(-t / p.get("decay", 0.06))
    return np.stack([x, x])


def chipsnare(p, rng):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    x = _chipnoise(n, p.get("rate", 9000), rng) * np.exp(-t / p.get("decay", 0.06))
    return np.stack([x, x]) * 0.7


def chiphat(p, rng):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = _chipnoise(n, p.get("rate", 22000), rng) * np.exp(-t / p.get("decay", 0.015))
    return np.stack([x, x]) * 0.5


DRUMS = {"kick": kick, "snare": snare, "hat": hat, "ohat": ohat, "etom": etom, "metal": metal,
         "timpani": timpani, "chipkick": chipkick, "chipsnare": chipsnare, "chiphat": chiphat}
FX = {"crash": crash, "impact": impact, "riser": riser, "downlifter": downlifter,
      "rain": rain, "vinyl": vinyl, "zap": zap}
LONG_FX = {"riser", "downlifter", "rain", "vinyl"}  # take a length in bars
