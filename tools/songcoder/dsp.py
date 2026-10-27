"""Low-level DSP building blocks: oscillators, filters, envelopes, dynamics."""
import numpy as np
from numba import njit
from scipy import signal
from scipy.ndimage import minimum_filter1d

SR = 44100


# --- oscillators ---------------------------------------------------------

@njit(cache=True)
def _blep(t, dt):
    if t < dt:
        t = t / dt
        return t + t - t * t - 1.0
    if t > 1.0 - dt:
        t = (t - 1.0) / dt
        return t * t + t + t + 1.0
    return 0.0


@njit(cache=True)
def osc_saw(freq, phase):
    """Band-limited saw (polyBLEP). freq: per-sample Hz array."""
    n = freq.shape[0]
    out = np.empty(n)
    p = phase
    for i in range(n):
        dt = freq[i] / SR
        out[i] = 2.0 * p - 1.0 - _blep(p, dt)
        p += dt
        if p >= 1.0:
            p -= 1.0
    return out


@njit(cache=True)
def osc_pulse(freq, phase, width):
    """Band-limited pulse built from two saws."""
    n = freq.shape[0]
    out = np.empty(n)
    p = phase
    for i in range(n):
        dt = freq[i] / SR
        q = p + width
        if q >= 1.0:
            q -= 1.0
        a = 2.0 * p - 1.0 - _blep(p, dt)
        b = 2.0 * q - 1.0 - _blep(q, dt)
        out[i] = 0.5 * (a - b)
        p += dt
        if p >= 1.0:
            p -= 1.0
    return out


@njit(cache=True)
def osc_sine(freq, phase):
    n = freq.shape[0]
    out = np.empty(n)
    p = phase
    for i in range(n):
        out[i] = np.sin(2.0 * np.pi * p)
        p += freq[i] / SR
        if p >= 1.0:
            p -= 1.0
    return out


# --- filters -------------------------------------------------------------

@njit(cache=True)
def svf(x, cutoff, q, mode):
    """TPT state-variable filter, per-sample cutoff. mode 0=lp 1=bp 2=hp."""
    n = x.shape[0]
    out = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 1.0 / q
    for i in range(n):
        fc = cutoff[i]
        if fc > 0.45 * SR:
            fc = 0.45 * SR
        if fc < 10.0:
            fc = 10.0
        g = np.tan(np.pi * fc / SR)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            out[i] = v2
        elif mode == 1:
            out[i] = v1
        else:
            out[i] = x[i] - k * v1 - v2
    return out


def lowpass(x, fc, q=0.707):
    return svf(x, np.full(x.shape[-1], float(fc)), q, 0)


def highpass(x, fc, q=0.707):
    return svf(x, np.full(x.shape[-1], float(fc)), q, 2)


def bandpass(x, fc, q=1.0):
    return svf(x, np.full(x.shape[-1], float(fc)), q, 1)


def sos_filter(x, kind, freq, order=2):
    sos = signal.butter(order, freq, btype=kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=-1)


# --- envelopes -----------------------------------------------------------

def adsr(n_gate, a, d, s, r):
    """Gate-length ADSR; returns n_gate + release samples."""
    na, nd, nr = max(int(a * SR), 1), max(int(d * SR), 1), max(int(r * SR), 1)
    t = np.arange(n_gate)
    env = np.where(t < na, t / na, s + (1.0 - s) * np.exp(-(t - na) / nd))
    level = env[-1] if n_gate else 0.0
    rel = level * np.exp(-np.arange(nr) / (nr / 5.0))
    return np.concatenate([env, rel])


def decay(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


# --- effects -------------------------------------------------------------

@njit(cache=True)
def pingpong_delay(x, d_samples, feedback, damp):
    """Stereo ping-pong delay with one-pole damping in the feedback loop."""
    n = x.shape[1]
    out = np.zeros((2, n))
    bl = np.zeros(d_samples)
    br = np.zeros(d_samples)
    lpl = 0.0
    lpr = 0.0
    idx = 0
    for i in range(n):
        yl = bl[idx]
        yr = br[idx]
        out[0, i] = yl
        out[1, i] = yr
        lpl += damp * (yr - lpl)
        lpr += damp * (yl - lpr)
        bl[idx] = 0.5 * (x[0, i] + x[1, i]) + feedback * lpl
        br[idx] = feedback * lpr
        idx += 1
        if idx >= d_samples:
            idx = 0
    return out


def reverb_ir(seconds, rng, predelay=0.02, damping=5500.0):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.9 * t / seconds)
    ir = rng.standard_normal((2, n)) * env
    ir = sos_filter(ir, "lowpass", damping, order=1)
    # high frequencies die faster: blend in a darker tail
    dark = sos_filter(ir, "lowpass", damping / 4, order=2)
    mix = np.clip(t / seconds * 2.0, 0.0, 1.0)
    ir = ir * (1 - mix) + dark * mix
    ir = np.concatenate([np.zeros((2, int(predelay * SR))), ir], axis=1)
    return ir / np.sqrt(np.sum(ir ** 2) / 2.0)


def convolve_reverb(x, ir):
    out = np.stack([signal.oaconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return out


@njit(cache=True)
def _vardelay(x, delay):
    n = x.shape[1]
    out = np.zeros_like(x)
    for i in range(n):
        pos = i - delay[i]
        if pos < 0:
            continue
        j = int(pos)
        f = pos - j
        if j + 1 < n:
            for c in range(2):
                out[c, i] = x[c, j] * (1 - f) + x[c, j + 1] * f
    return out


def tape(x, wow, wow_hz, flutter, flutter_hz):
    """Tape wow/flutter: pitch wobble from a slowly modulated delay (depths in seconds)."""
    t = np.arange(x.shape[1]) / SR
    d = (wow + flutter) + wow * np.sin(2 * np.pi * wow_hz * t) + flutter * np.sin(2 * np.pi * flutter_hz * t)
    return _vardelay(x, d * SR + 2)


def ensemble(x, depth=0.0012, rate=0.6, vib=0.00015, vib_rate=5.5):
    """String-machine ensemble: three modulated delay taps 120 degrees apart, spread to stereo."""
    n = x.shape[0]
    t = np.arange(n) / SR
    src = np.stack([x, x])
    taps = []
    for k in range(3):
        ph = 2 * np.pi * k / 3
        d = 0.006 + depth * (1 + np.sin(2 * np.pi * rate * t + ph)) + vib * np.sin(2 * np.pi * vib_rate * t + ph)
        taps.append(_vardelay(src, d * SR)[0])
    return np.stack([taps[0] + 0.6 * taps[1], taps[2] + 0.6 * taps[1]]) / 1.6


def soft_clip(x, drive):
    return np.tanh(drive * x) / np.tanh(drive)


# --- dynamics ------------------------------------------------------------

@njit(cache=True)
def _env_follow(det, att, rel):
    n = det.shape[0]
    out = np.empty(n)
    e = 0.0
    a = np.exp(-1.0 / (att * SR))
    r = np.exp(-1.0 / (rel * SR))
    for i in range(n):
        v = det[i]
        c = a if v > e else r
        e = c * e + (1.0 - c) * v
        out[i] = e
    return out


def compressor(x, threshold_db, ratio, attack, release, makeup_db=0.0):
    det = np.max(np.abs(x), axis=0)
    env = _env_follow(det, attack, release)
    env_db = 20 * np.log10(env + 1e-9)
    over = np.maximum(env_db - threshold_db, 0.0)
    gain_db = -over * (1.0 - 1.0 / ratio) + makeup_db
    return x * 10 ** (gain_db / 20)


@njit(cache=True)
def _release_smooth(g, rel):
    n = g.shape[0]
    out = np.empty(n)
    r = np.exp(-1.0 / (rel * SR))
    s = 1.0
    for i in range(n):
        v = g[i]
        if v < s:
            s = v
        else:
            s = r * s + (1.0 - r) * v
        out[i] = s
    return out


def limiter(x, ceiling_db=-1.0, lookahead=0.005, release=0.08):
    ceil = 10 ** (ceiling_db / 20)
    peak = np.max(np.abs(x), axis=0)
    need = np.minimum(1.0, ceil / (peak + 1e-12))
    w = int(lookahead * SR) * 2 + 1
    need = minimum_filter1d(need, size=w)
    g = _release_smooth(need, release)
    # smooth attack edge so gain never jumps
    g = np.convolve(g, np.hanning(w) / np.hanning(w).sum(), mode="same")
    g = np.minimum(g, need)
    return np.clip(x * g, -ceil, ceil)


def pan(x, p):
    """Balance-pan a stereo signal, p in [-1, 1]."""
    gl = min(1.0, 1.0 - p)
    gr = min(1.0, 1.0 + p)
    return x * np.array([[gl], [gr]])


def db(v):
    return 10 ** (v / 20)
