"""Reads a song directory (song.yaml, patterns.yaml, lyrics.yaml) and renders it."""
import re
import wave
from pathlib import Path

import lameenc
import mutagen.mp3
import numpy as np
import yaml

from . import dsp
from .cover import make_cover
from .drums import DRUMS, FX, LONG_FX
from .dsp import SR, db
from .instruments import INSTRUMENTS
from .tags import write_tags
from .voice import chop_note, load_chops, plain, robotize, shout, tts, whisper

VEL = {"x": 1.0, "o": 0.6, "g": 0.35}
NOTE_RE = re.compile(r"^([A-G])(#|b)?(-?\d)$")
PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_freq(name):
    m = NOTE_RE.match(name)
    if not m:
        raise ValueError(f"Okänd not: {name}")
    pc = PC[m[1]] + {"#": 1, "b": -1, None: 0}[m[2]]
    midi = 12 * (int(m[3]) + 1) + pc
    return 440.0 * 2 ** ((midi - 69) / 12)


def load(song_dir):
    d = Path(song_dir)
    song = yaml.safe_load((d / "song.yaml").read_text())
    patterns = yaml.safe_load((d / "patterns.yaml").read_text())
    lyr = d / "lyrics.yaml"
    lyrics = yaml.safe_load(lyr.read_text()) if lyr.exists() else None
    return song, patterns, lyrics


# --- pattern parsing -----------------------------------------------------

def pattern_steps(pat):
    if set(pat) <= set("xog. \n"):
        return list("".join(pat.split()))  # drum string; spaces only group steps
    return pat.split()


def resolve_token(tok, chord):
    """Return list of freqs for a melodic token given the bar's chord."""
    vel = 1.0 if tok.endswith("!") else 0.82
    tok = tok.rstrip("!")
    if tok == "C":
        return [note_freq(n) for n in chord["notes"]], vel
    octave = tok.count("+") - tok.count("-")
    base = tok.strip("+-")
    if base == "r":
        f = note_freq(chord["root"])
    elif base.isdigit():
        # indices past the chord size wrap around an octave up
        k = int(base) - 1
        octave += k // len(chord["notes"])
        f = note_freq(chord["notes"][k % len(chord["notes"])])
    else:
        f = note_freq(base)
    return [f * 2 ** octave], vel


def chord_freqs(chord, cfg):
    """Chord tones used as the vocoder carrier for tuned vocal chops."""
    shift = 2 ** cfg.get("carrier_octave", 0)
    return [note_freq(n) * shift for n in chord["notes"]]


def normalize_spec(spec):
    if spec is None:
        return None
    if isinstance(spec, str):
        spec = {"pattern": [spec]}
    elif isinstance(spec, list):
        spec = {"pattern": spec}
    elif isinstance(spec.get("pattern"), str):
        spec = {**spec, "pattern": [spec["pattern"]]}
    return spec


def iter_pattern_bars(spec, patterns, bars):
    """Yield (bar_offset, steps_for_that_chunk) cycling the pattern list."""
    pos, i = 0, 0
    while pos < bars:
        steps = pattern_steps(patterns[spec["pattern"][i % len(spec["pattern"])]])
        nb = max(1, len(steps) // 16)
        keep = min(nb, bars - pos)
        yield pos, steps[: keep * 16]
        pos += nb
        i += 1


# --- arrangement ---------------------------------------------------------

class Song:
    def __init__(self, song_dir):
        self.dir = Path(song_dir)
        self.song, self.patterns, self.lyrics = load(song_dir)
        self.bpm = self.song["bpm"]
        self.step = 60 / self.bpm / 4
        self.bar = self.step * 16
        self.rng = np.random.default_rng(self.song.get("seed", 1))
        self.sections = []
        b = 0
        for s in self.song["sections"]:
            self.sections.append((b, s))
            b += s["bars"]
        self.total_bars = b
        self.n = int((b * self.bar + self.song.get("tail_seconds", 4)) * SR)
        self.tracks = {}
        # humanize uses its own generator so songs without it keep their exact sound
        self.humanize = self.song.get("humanize")
        self.hrng = np.random.default_rng(self.song.get("seed", 1) + 7)

    def swing_offset(self, i):
        """Delay the off-beat of each swing unit (8ths or 16ths) by `swing` of a unit."""
        sw = self.song.get("swing", 0.0)
        if not sw:
            return 0.0
        unit = 2 if self.song.get("swing_unit", 16) == 8 else 1
        if i % unit == 0 and (i // unit) % 2 == 1:
            return sw * unit * self.step
        return 0.0

    def buf(self, name):
        if name not in self.tracks:
            self.tracks[name] = np.zeros((2, self.n))
        return self.tracks[name]

    def place(self, name, x, start):
        start = int(start)
        if start >= self.n:
            return
        end = min(self.n, start + x.shape[1])
        self.buf(name)[:, start:end] += x[:, : end - start]

    def chord_at(self, section, bar_in_section):
        prog = section.get("progression", self.song["progression"])
        return self.song["chords"][prog[bar_in_section % len(prog)]]

    def segments(self, section):
        """Per track: list of (from_bar, to_bar, spec) inside the section."""
        bars = section["bars"]
        tail = section.get("tail") or {}
        tb = tail.get("bars", 0)
        out = {}
        for name, spec in (section.get("tracks") or {}).items():
            spec = normalize_spec(spec)
            end = bars - tb if name in (tail.get("tracks") or {}) else bars
            if spec:
                out.setdefault(name, []).append((0, end, spec))
        for name, spec in (tail.get("tracks") or {}).items():
            spec = normalize_spec(spec)
            if spec:
                out.setdefault(name, []).append((bars - tb, bars, spec))
        return out

    def render_sequences(self):
        kicks = []
        inst_cfg = self.song["instruments"]
        drum_cache = {}
        for sec_start, section in self.sections:
            bars = section["bars"]
            for name, segs in self.segments(section).items():
                cfg = inst_cfg[name]
                kind = cfg["type"]
                for b0, b1, spec in segs:
                    c0, c1 = spec.get("cutoff", [1.0, 1.0])
                    gain = db(spec.get("gain", 0.0))
                    transpose = 2 ** (spec.get("transpose", 0) / 12)
                    for off, steps in iter_pattern_bars(spec, self.patterns, b1 - b0):
                        for i, tok in enumerate(steps):
                            if tok in (".", "-"):
                                continue
                            bar_in_sec = b0 + off + i // 16
                            t_in_sec = (b0 + off) * self.bar + i * self.step
                            t_in_sec += self.swing_offset(i)
                            hv = 1.0
                            if self.humanize:
                                t_in_sec += self.humanize.get("time", 0.0) * (2 * self.hrng.random() - 1)
                                hv = 1 + self.humanize.get("vel", 0.0) * (2 * self.hrng.random() - 1)
                            start = max(0.0, (sec_start * self.bar + t_in_sec) * SR)
                            if kind in DRUMS:
                                # cache per track: two tracks of one kind may differ in params
                                if name not in drum_cache:
                                    drum_cache[name] = DRUMS[kind](cfg, self.rng)
                                v = VEL[tok] * gain * hv
                                self.place(name, drum_cache[name] * v, start)
                                if kind == "kick":
                                    kicks.append(int(start))
                                continue
                            length = 1
                            while i + length < len(steps) and steps[i + length] == "-":
                                length += 1
                            if kind == "chop":
                                # a vocal slice rings until the next slice, rests don't cut it
                                length = 1
                                while i + length < len(steps) and steps[i + length] in ("-", "."):
                                    length += 1
                                chord = self.chord_at(section, bar_in_sec)
                                x = chop_note(self.chop_samples(cfg)[tok.lstrip("@")],
                                              int(length * self.step * SR), chord_freqs(chord, cfg),
                                              cfg, self.rng)
                                self.place(name, x * gain * hv, start)
                                continue
                            frac = t_in_sec / (bars * self.bar)
                            cm = c0 * (c1 / c0) ** frac
                            freqs, vel = resolve_token(tok, self.chord_at(section, bar_in_sec))
                            n_gate = int(length * self.step * cfg.get("legato", 0.88) * SR)
                            for f in freqs:
                                note = INSTRUMENTS[kind](f * transpose, n_gate, vel * gain * hv, cfg, cm, self.rng)
                                self.place(name, note, start)
            for fx in section.get("fx") or []:
                start = (sec_start + fx.get("at", 0)) * self.bar * SR
                g = db(fx.get("gain", 0.0))
                if fx["type"] in LONG_FX:
                    x = FX[fx["type"]]({}, self.rng, fx.get("bars", 4) * self.bar)
                else:
                    x = FX[fx["type"]]({}, self.rng)
                self.place("fx", x * g, start)
        return kicks

    def chop_samples(self, cfg):
        if not hasattr(self, "_chops"):
            self._chops = load_chops(self.lyrics, self.dir / "build" / "voice")
        return self._chops

    def render_voice(self):
        if not self.lyrics:
            return
        cfg = self.lyrics
        carrier = [note_freq(n) for n in cfg.get("carrier", ["F2", "F3"])]
        sec_by_name = {s["name"]: b for b, s in self.sections}
        for line in cfg.get("lines") or []:
            x = tts(line["text"], cfg["voice"], self.dir / "build" / "voice",
                    cfg.get("length_scale", 1.0))
            style = line.get("style", cfg.get("style", "robot"))
            if style == "whisper":
                y = whisper(x, self.rng, cfg.get("air", 0.12))
            elif style == "plain":
                y = plain(x)
            elif style == "shout":
                y = shout(x, cfg.get("drive", 4.0), cfg.get("slap", 0.09))
            else:
                y = robotize(x, carrier, self.rng, cfg.get("vocoder_mix", 0.7))
            bar = sec_by_name[line["section"]] + line.get("bar", 0)
            self.place("voice", y * db(line.get("gain", 0.0)), bar * self.bar * SR)

    def duck_env(self, kicks):
        L = int(self.step * 2.2 * SR)
        curve = (1 - np.arange(L) / L) ** 2
        env = np.zeros(self.n)
        for k in kicks:
            e = min(self.n, k + L)
            env[k:e] = np.maximum(env[k:e], curve[: e - k])
        return env

    def mix(self, kicks):
        mixcfg = self.song["mix"]
        duck = self.duck_env(kicks)
        master = np.zeros((2, self.n))
        rev_in = np.zeros((2, self.n))
        dly_in = np.zeros((2, self.n))
        stats = {}
        for name, x in self.tracks.items():
            m = mixcfg.get(name, {})
            y = x * db(m.get("gain", 0.0))
            if m.get("highpass"):
                y = dsp.sos_filter(y, "highpass", m["highpass"])
            if m.get("lowpass"):
                y = dsp.sos_filter(y, "lowpass", m["lowpass"], order=4)
            if m.get("downsample"):
                k = int(m["downsample"])
                y = np.repeat(y[:, ::k], k, axis=1)[:, : y.shape[1]]
            if m.get("crush"):
                q = 2 ** (m["crush"] - 1)
                y = np.round(y * q) / q
            if m.get("duck"):
                y = y * (1 - m["duck"] * duck)
            y = dsp.pan(y, m.get("pan", 0.0))
            stats[name] = y
            master += y
            rev_in += y * m.get("reverb", 0.0)
            dly_in += y * m.get("delay", 0.0)
        fx = self.song.get("fx_buses", {})
        d = fx.get("delay", {})
        d_samples = int(self.step * d.get("steps", 3) * SR)
        dly = dsp.pingpong_delay(dly_in, d_samples, d.get("feedback", 0.42), d.get("damp", 0.35))
        rev_in += dly * d.get("reverb", 0.3)
        r = fx.get("reverb", {})
        ir = dsp.reverb_ir(r.get("seconds", 2.6), self.rng, damping=r.get("damping", 5500))
        rev = dsp.convolve_reverb(dsp.sos_filter(rev_in, "highpass", 220), ir)
        master += dly * db(d.get("return", 0.0)) + rev * db(r.get("return", 0.0))
        return master, stats

    def master(self, x):
        mcfg = self.song.get("master", {})
        x = dsp.sos_filter(x, "highpass", 28)
        lofi = mcfg.get("lofi")
        if lofi:
            x = dsp.tape(x, lofi.get("wow", 0.0015), lofi.get("wow_hz", 0.5),
                         lofi.get("flutter", 0.0002), lofi.get("flutter_hz", 7.0))
            x = dsp.sos_filter(x, "lowpass", lofi.get("lowpass", 9000), order=2)
            x = dsp.soft_clip(x, lofi.get("drive", 1.5)) * 0.8
        x = dsp.compressor(x, mcfg.get("glue_threshold", -14), 2.0, 0.01, 0.15)
        # loudness: match RMS of the loudest blocks to target
        blk = int(0.4 * SR)
        nb = x.shape[1] // blk
        rms = np.sqrt(np.mean(x[:, : nb * blk].reshape(2, nb, blk) ** 2, axis=(0, 2)))
        loud = np.sort(rms)[int(nb * 0.7):].mean()
        x = x * (db(mcfg.get("target_rms_db", -10.0)) / loud)
        sat = mcfg.get("saturation", 1.2)
        if sat:
            x = dsp.soft_clip(x * 0.9, sat) / 0.9
        x = dsp.limiter(x, mcfg.get("ceiling_db", -1.0))
        fade = self.song.get("fade_out_bars", 0)
        if fade:
            s = int((self.total_bars - fade) * self.bar * SR)
            ramp = np.linspace(1, 0, self.n - s) ** 1.5
            x[:, s:] *= ramp
        return x


def write_wav24(path, x):
    i = np.ascontiguousarray(np.clip(np.round(x.T * 8388607), -8388608, 8388607).astype("<i4"))
    b = i.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(b)


def write_mp3(path, x):
    enc = lameenc.Encoder()
    enc.set_bit_rate(320)
    enc.set_in_sample_rate(SR)
    enc.set_channels(2)
    enc.set_quality(2)
    pcm = np.clip(np.round(x.T * 32767), -32768, 32767).astype("<i2").tobytes()
    data = enc.encode(pcm) + enc.flush()
    Path(path).write_bytes(data)


def retag(song_dir):
    """Regenerate cover.jpg and ID3 tags on an existing mp3 without re-rendering audio."""
    song, _, lyrics = load(song_dir)
    od = Path(song_dir) / "out"
    mp3 = od / "song.mp3"
    if not mp3.exists():
        raise SystemExit(f"Saknas: {mp3} – rendera låten först")
    cover = make_cover(song, np.random.default_rng(song.get("seed", 1)), od / "cover.jpg")
    seconds = mutagen.mp3.MP3(mp3).info.length
    write_tags(mp3, song, lyrics, cover, seconds)
    print(f"Taggat: {mp3}, {cover}")


def render(song_dir):
    s = Song(song_dir)
    print(f"{s.song['title']}: {s.total_bars} takter, {s.n / SR:.1f} s")
    kicks = s.render_sequences()
    s.render_voice()
    mixed, stats = s.mix(kicks)
    for name, y in stats.items():
        rms = 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)
        peak = 20 * np.log10(np.max(np.abs(y)) + 1e-9)
        print(f"  {name:8s} rms {rms:6.1f} dB  peak {peak:6.1f} dB")
    out = s.master(mixed)
    od = s.dir / "out"
    od.mkdir(exist_ok=True)
    write_wav24(od / "song.wav", out)
    write_mp3(od / "song.mp3", out)
    # cover.jpg next to the mp3 is picked up by players that read folder art
    cover = make_cover(s.song, np.random.default_rng(s.song.get("seed", 1)), od / "cover.jpg")
    write_tags(od / "song.mp3", s.song, s.lyrics, cover, out.shape[1] / SR)
    print(f"Klart: {od / 'song.wav'}, {od / 'song.mp3'}, {cover}")
