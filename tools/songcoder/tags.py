"""ID3 metadata and embedded cover art for the rendered MP3."""
import datetime

from mutagen.id3 import (APIC, COMM, ID3, TALB, TBPM, TCON, TDRC, TENC, TIT2, TKEY,
                         TLEN, TPE1, TSSE, TXXX, USLT)

KEY_SUFFIX = {"minor": "m", "major": ""}


def _id3_key(key):
    """'F minor' -> 'Fm', 'C# major' -> 'C#'."""
    parts = (key or "").split()
    if len(parts) != 2:
        return None
    return parts[0] + KEY_SUFFIX.get(parts[1].lower(), "")


def write_tags(mp3_path, song, lyrics, cover_path, seconds):
    date = str(song.get("date") or datetime.date.today().isoformat())
    tags = ID3()
    tags.add(TIT2(encoding=3, text=song["title"]))
    tags.add(TPE1(encoding=3, text=song.get("artist", "song-coder")))
    tags.add(TALB(encoding=3, text=song.get("album", song["title"])))
    tags.add(TDRC(encoding=3, text=date))
    if song.get("genre"):
        tags.add(TCON(encoding=3, text=song["genre"]))
    tags.add(TBPM(encoding=3, text=str(song["bpm"])))
    if _id3_key(song.get("key")):
        tags.add(TKEY(encoding=3, text=_id3_key(song.get("key"))))
    tags.add(TLEN(encoding=3, text=str(int(seconds * 1000))))
    tags.add(TENC(encoding=3, text="song-coder"))
    tags.add(TSSE(encoding=3, text="song-coder (offline synthesis, lameenc)"))
    tags.add(TXXX(encoding=3, desc="Created by", text="song-coder"))
    tags.add(COMM(encoding=3, lang="swe", desc="",
                  text=f"Skapad av song-coder {date}. Helt kodgenererad låt."))
    if lyrics and lyrics.get("lines"):
        text = "\n".join(line["text"] for line in lyrics["lines"])
        lang = "swe" if lyrics.get("voice", "").startswith("sv") else "eng"
        tags.add(USLT(encoding=3, lang=lang, desc="", text=text))
    if cover_path:
        tags.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover",
                      data=open(cover_path, "rb").read()))
    tags.save(mp3_path, v2_version=3)
