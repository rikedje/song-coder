"""Offline TTS (Piper) and robotic processing (channel vocoder)."""
import hashlib
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import pyworld
from scipy import signal

from .dsp import SR, osc_saw, sos_filter

REPO = Path(__file__).resolve().parents[2]
FRAME_MS = 5.0


def tts(text, voice, cache_dir, length_scale=1.0):
    model = REPO / "voices" / f"{voice}.onnx"
    if not model.exists():
        raise SystemExit(f"Voice model saknas: {model} – kör tools/setup.sh")
    key = hashlib.sha1(f"{voice}|{length_scale}|{text}".encode()).hexdigest()[:16]
    path = Path(cache_dir) / f"{key}.wav"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [sys.executable, "-m", "piper", "-m", str(model), "-f", str(path),
             "--length-scale", str(length_scale)],
            input=text.encode(), check=True, capture_output=True,
        )
    with wave.open(str(path)) as w:
        rate = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2") / 32768.0
    return signal.resample_poly(x, SR, rate)


def _rms(x):
    return np.sqrt(np.mean(x ** 2) + 1e-12)


def vocoder(mod, carrier_freqs, rng, bands=22, lo=140.0, hi=7800.0):
    n = mod.shape[0]
    car = sum(osc_saw(np.full(n, f), rng.random()) for f in carrier_freqs)
    car = car / len(carrier_freqs) + 0.12 * rng.standard_normal(n)
    edges = np.geomspace(lo, hi, bands + 1)
    env_sos = signal.butter(2, 45, fs=SR, output="sos")
    out = np.zeros(n)
    for a, b in zip(edges[:-1], edges[1:]):
        sos = signal.butter(2, [a, b], btype="band", fs=SR, output="sos")
        env = signal.sosfilt(env_sos, np.abs(signal.sosfilt(sos, mod)))
        out += signal.sosfilt(sos, car) * np.maximum(env, 0)
    return out * _rms(mod) / _rms(out)


def whisper(x, rng, air=0.12):
    """Unvoiced whisper: vocode the speech onto pure noise, plus a little airy top end."""
    n = x.shape[0]
    noise = rng.standard_normal(n)
    edges = np.geomspace(200.0, 10000.0, 29)
    env_sos = signal.butter(2, 60, fs=SR, output="sos")
    y = np.zeros(n)
    for a, b in zip(edges[:-1], edges[1:]):
        sos = signal.butter(2, [a, b], btype="band", fs=SR, output="sos")
        env = signal.sosfilt(env_sos, np.abs(signal.sosfilt(sos, x)))
        y += signal.sosfilt(sos, noise) * np.maximum(env, 0)
    y = y * _rms(x) / _rms(y)
    top = sos_filter(x, "highpass", 3000)
    y = y + air * top * _rms(y) / _rms(top)
    d = int(0.009 * SR)
    right = np.concatenate([np.zeros(d), y[:-d]])
    return np.stack([0.8 * y + 0.2 * right, 0.8 * right + 0.2 * y])


def robotize(x, carrier_freqs, rng, vocoder_mix=0.7, ring_hz=55.0):
    t = np.arange(x.shape[0]) / SR
    voc = vocoder(x, carrier_freqs, rng)
    dry = sos_filter(x, "bandpass", [250, 5500])
    dry = dry * (0.6 + 0.4 * np.sin(2 * np.pi * ring_hz * t))
    y = vocoder_mix * voc + (1 - vocoder_mix) * dry * _rms(voc) / _rms(dry)
    d = int(0.013 * SR)
    right = np.concatenate([np.zeros(d), y[:-d]])
    return np.stack([0.85 * y + 0.15 * right, 0.85 * right + 0.15 * y])


def plain(x):
    """Clean spoken voice: rumble removed, slight stereo width."""
    y = sos_filter(x, "highpass", 90)
    d = int(0.011 * SR)
    right = np.concatenate([np.zeros(d), y[:-d]])
    return np.stack([0.9 * y + 0.1 * right, 0.9 * right + 0.1 * y])


def shout(x, drive=4.0, slap=0.09):
    """Hard commanding voice: levelled, overdriven, band-limited, with a slapback echo."""
    y = sos_filter(x, "bandpass", [180, 5500])
    y = y / (np.max(np.abs(y)) + 1e-9)
    y = np.tanh(drive * y) / np.tanh(drive)
    d = int(slap * SR)
    echo = np.concatenate([np.zeros(d), y])[: y.shape[0]] * 0.35
    left = y + echo
    right = y + np.concatenate([np.zeros(int(d * 1.3)), y])[: y.shape[0]] * 0.3
    return np.stack([left, right]) * 0.5


def _trim(x, floor_db=-38.0):
    env = np.abs(x)
    keep = np.nonzero(env > env.max() * 10 ** (floor_db / 20))[0]
    return x[keep[0]: keep[-1] + 1] if keep.size else x


def load_chops(cfg, cache_dir):
    """TTS each chop word separately so every slice is a clean one-shot."""
    return {name: _trim(tts(text, cfg["voice"], cache_dir, cfg.get("chop_length_scale", 0.95)))
            for name, text in cfg["chops"].items()}


def chop_note(sample, n_gate, carrier_freqs, cfg, rng):
    """Play a vocal slice for at most n_gate samples, tuned to the chord by a vocoder."""
    pitch = cfg.get("pitch", 0)
    x = signal.resample_poly(sample, 100, int(round(100 * 2 ** (pitch / 12)))) if pitch else sample
    x = x[: max(n_gate, 1)].copy()
    f = min(int(0.006 * SR), x.shape[0] // 2)
    if f:
        x[:f] *= np.linspace(0, 1, f)
        x[-f:] *= np.linspace(1, 0, f)
    tune = cfg.get("tune", 0.5)
    if tune:
        voc = vocoder(x, carrier_freqs, rng, bands=18, lo=180.0, hi=8000.0)
        x = tune * voc + (1 - tune) * x
    d = int(0.008 * SR)
    right = np.concatenate([np.zeros(d), x])[: x.shape[0]]
    return np.stack([x, 0.85 * right + 0.15 * x])


def analyze_word(x):
    """WORLD analysis of a TTS word, so it can be resynthesized at any pitch and length."""
    x = _trim(x).astype(np.float64)
    f0, t = pyworld.harvest(x, SR, f0_floor=70.0, f0_ceil=700.0, frame_period=FRAME_MS)
    f0 = pyworld.stonemask(x, f0, t, SR)
    return {"f0": f0, "sp": pyworld.cheaptrick(x, f0, t, SR), "ap": pyworld.d4c(x, f0, t, SR)}


def _warp_formants(sp, ratio):
    """Move the spectral envelope along frequency: another throat singing the same note."""
    bins = sp.shape[1]
    pos = np.clip(np.arange(bins) / ratio, 0, bins - 1)
    i = pos.astype(int)
    j = np.minimum(i + 1, bins - 1)
    a = pos - i
    return sp[:, i] * (1 - a) + sp[:, j] * a


def _time_map(an, v0, v1, m):
    """Source frames for m output frames of the body: steady vowels take most of the stretch."""
    k = v1 - v0
    if m <= k:
        return np.linspace(v0, v1 - 1, m)
    log_sp = np.log(an["sp"][v0:v1])
    flux = np.abs(np.diff(log_sp, axis=0)).mean(axis=1)
    w = 1 / (np.append(flux, flux[-1:]) + np.median(flux) * 0.25 + 1e-6) ** 2
    w[an["f0"][v0:v1] == 0] *= 0.02
    # every frame keeps its natural length first, only the surplus is shared by weight
    frames = 1 + (m - k) * w / w.sum()
    return v0 + np.interp(np.arange(m), np.concatenate([[0], np.cumsum(frames)]), np.arange(k + 1))


def sing_word(an, freqs, seconds, cfg, rng, formant=1.0):
    """Sing one word: the notes in freqs share its length. Returns (mono, samples before the vowel)."""
    f0, sp, ap = an["f0"], an["sp"], an["ap"]
    voiced = np.nonzero(f0 > 0)[0]
    v0, v1 = (voiced[0], voiced[-1] + 1) if voiced.size else (0, f0.shape[0])
    total = max(int(seconds * 1000 / FRAME_MS), 4)
    tail = f0.shape[0] - v1
    body = _time_map(an, v0, v1, max(total - tail, 3))
    src = np.concatenate([np.arange(v0), body, np.arange(v1, f0.shape[0])])
    i = np.minimum(src.astype(int), f0.shape[0] - 2)
    a = (src - i)[:, None]
    out_sp = np.exp(np.log(sp[i]) * (1 - a) + np.log(sp[i + 1]) * a)
    out_ap = ap[i] * (1 - a) + ap[i + 1] * a
    if formant != 1.0:
        out_sp = _warp_formants(out_sp, formant)
    m = src.shape[0]
    t = np.arange(m) * FRAME_MS / 1000
    # pitch line: each note an equal share of the body, glides between notes, a scoop into the first
    idx = np.minimum(((np.arange(m) - v0).clip(0) * len(freqs)) // max(body.shape[0], 1), len(freqs) - 1)
    pitch = np.log(np.asarray(freqs))[idx]
    coef = 1 - np.exp(-FRAME_MS / cfg.get("glide_ms", 35.0))
    pitch = signal.lfilter([coef], [1, coef - 1], pitch, zi=[pitch[0] * (1 - coef)])[0]
    cents = -cfg.get("scoop", 45.0) * np.exp(-(t - t[v0]).clip(0) / 0.05)
    ramp = np.clip((t - cfg.get("vibrato_delay", 0.3)) / 0.25, 0, 1)
    cents += cfg.get("vibrato", 16.0) * ramp * np.sin(2 * np.pi * cfg.get("vibrato_hz", 5.2) * t + rng.random() * 6.28)
    target = np.exp(pitch + cents * np.log(2) / 1200)
    y = pyworld.synthesize(np.where(f0[np.minimum(np.round(src).astype(int), f0.shape[0] - 1)] > 0, target, 0.0),
                           np.ascontiguousarray(out_sp), np.ascontiguousarray(out_ap), SR, FRAME_MS)
    y = y * min(0.16 / (_rms(y) + 1e-9), 0.6 / (np.max(np.abs(y)) + 1e-9))
    f = min(int(0.012 * SR), y.shape[0] // 3)
    y[-f:] *= np.linspace(1, 0, f)
    y[:f // 4] *= np.linspace(0, 1, f // 4)
    return y, int(v0 * FRAME_MS / 1000 * SR)


def sheen(y, amount):
    """Generate the top octave TTS lacks: harmonics of the highs, kept above 9 kHz."""
    if not amount:
        return y
    hi = sos_filter(y, "highpass", 3500)
    return y + amount * sos_filter(np.tanh(hi * 6.0), "highpass", 9000)
