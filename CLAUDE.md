# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This repo turns a song brief into a finished, listenable track rendered entirely by code. The brief follows the template in `mall.md` (Swedish): the user fills in feel/references, tempo/key/length, form, sound palette, vocals, and things to avoid. Anything left unspecified is Claude's call, made in the spirit of the song.

New songs are made with the project skill `/ny-lat` (`.claude/skills/ny-lat/SKILL.md`). It asks questions, saves the filled-in brief as `songs/<slug>/<slug>.md`, and produces the song in that same directory.

## Commands

```sh
./render.sh songs/<slug>        # setup if needed, then render out/song.wav + out/song.mp3
./tag.sh [songs/<slug> ...]     # only regenerate cover.jpg + ID3 tags, audio untouched (no args = all songs)
tools/setup.sh [voice ...]      # uv sync + download Piper voice models into voices/
ffprobe -v error -show_entries format=duration -of default=nw=1 songs/<slug>/out/song.mp3
```

Python is uv-managed **3.12**, pinned via `.python-version`, `requires-python` and `python-preference = "only-managed"` in `pyproject.toml`. Don't use the system Pythons: `/usr/local/bin/python3.8` is a broken x86 install, Homebrew's 3.15 lacks wheels, and Piper can't find its espeak data on 3.14. There are no tests or linter.

## Architecture

Songs are **data-driven**. Each `songs/<slug>/` contains only YAML and docs, and the shared engine in `tools/songcoder/` interprets them:

- `song.yaml`: title, bpm, key, `date`, `genre`, `cover` (`style`: `sunset` | `nightcity`, optional `palette`/`subtitle`), chords plus a `progression` (one chord per bar, cycled from each section's start), `instruments` (track name → `type` plus synth params), `sections` (bars, `tracks` → pattern spec, optional `tail` that overrides tracks for the last N bars, `fx` one-shots), `mix` (per-track gain/pan/sends/`duck`), `fx_buses`, `master`.
- `patterns.yaml`: 16 steps per bar; longer strings span several bars. The notation is documented at the top of the file (drums `x/o/g/.`; melodic tokens `r`, `1-3`, `C`, note names, `+`/`-` octaves, `-` hold, `!` accent).
- `lyrics.yaml`: Piper voice name, `style` (`robot`: pitched vocoder with `carrier` notes; `whisper`: noise-carrier vocoder), and lines placed by section and bar.

Engine modules:
- `dsp.py`: numba oscillators/SVF, delay, convolution reverb, compressor, limiter.
- `instruments.py`: pitched voices registered in `INSTRUMENTS` (`distbass`, `softbass`, `pluck`, `epiano`, `superpad`, `superlead`).
- `drums.py`: the `DRUMS` and `FX` one-shots.
- `voice.py`: Piper via subprocess, cached in `songs/<slug>/build/voice/`, plus the robot and whisper processors.
- `cover.py`: procedural 1500×1500 cover art using the committed font `fonts/SpaceGrotesk.ttf` (OFL). Pillow's default font lacks å/ä/ö.
- `tags.py`: ID3v2.3 tags via mutagen (title, artist `song-coder`, date, genre, BPM, key, lyrics, embedded APIC cover).
- `render.py`: sequencer → per-track buffers → kick sidechain → buses → master (`saturation: 0` disables soft clipping) → 24-bit WAV, lameenc MP3, `out/cover.jpg`, tags.

Rendering prints per-track RMS/peak, which is used to balance `mix`. Chord-tone indices past the chord size wrap an octave up.

When a new song needs a new sound, add an instrument type or FX to the engine rather than writing song-specific code, and keep existing songs rendering.

## Hard requirements from `mall.md`

- **Deliverables:** `songs/<slug>/out/song.wav` and `songs/<slug>/out/song.mp3`, fully mixed (instruments, drums, effects, and vocals if requested). They should sound like a finished song, not a demo.
- **Offline only:** the synth engine, sample libraries and voice/TTS tools must install into this repo with no manual steps and use no cloud services.
- **Autonomy:** don't ask questions and don't stop for approval. Decide, and record every choice in the song's `NOTES.md`.
- **Verify before finishing:** run `ffmpeg -v error -i out/song.mp3 -f null -` and compare the `ffprobe` duration with the arrangement length.

## Git

The repo is the private GitHub repo `rikedje/song-coder`. Only commit or push when the user asks. Voice models, `.venv/`, WAV files and `build/` are gitignored. MP3 files are committed.
