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


def robotize(x, carrier_freqs, rng, vocoder_mix=0.7, ring_hz=55.0):
    t = np.arange(x.shape[0]) / SR
    voc = vocoder(x, carrier_freqs, rng)
    dry = sos_filter(x, "bandpass", [250, 5500])
    dry = dry * (0.6 + 0.4 * np.sin(2 * np.pi * ring_hz * t))
    y = vocoder_mix * voc + (1 - vocoder_mix) * dry * _rms(voc) / _rms(dry)
    d = int(0.013 * SR)
    right = np.concatenate([np.zeros(d), y[:-d]])
    return np.stack([0.85 * y + 0.15 * right, 0.85 * right + 0.15 * y])
