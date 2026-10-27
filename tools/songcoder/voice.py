"""Offline TTS (Piper) and robotic processing (channel vocoder)."""
import hashlib
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from .dsp import SR, osc_saw, sos_filter

REPO = Path(__file__).resolve().parents[2]


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
