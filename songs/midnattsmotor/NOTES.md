# Midnattsmotor – anteckningar

Mörk synthwave/darksynth om en nattlig biljakt genom en neonstad. Låtprompten finns i `midnattsmotor.md`.

## Rendera om

```sh
./render.sh songs/midnattsmotor
```

Kommandot körs från repots rot. Det installerar verktygen vid behov (uv-hanterad Python 3.12 och Pipers röstmodell) och skriver:

- `out/song.wav` (24 bit, 44,1 kHz)
- `out/song.mp3` (320 kbps, med ID3-taggar, låttext och inbäddat omslag)
- `out/cover.jpg`, med stilen `sunset`: en randig synthwave-sol över ett neonrutnät

Det tar ca 20 s.

## Filer

| Fil | Innehåll |
|---|---|
| `song.yaml` | tempo, tonart, ackord, form/sektioner, instrumentinställningar, mix och master |
| `patterns.yaml` | trum-, bas-, arpeggio-, pad- och leadmönster (textnotation, förklarad överst i filen) |
| `lyrics.yaml` | rösttext, placering per sektion/takt och röstinställningar |

Koden (motorn) finns i `tools/songcoder/` och delas med andra låtar.

## Val jag gjort

- **Ljudmotor:** egen syntes i Python (numpy/scipy, numba för filter och oscillatorer). Allt ljud skapas från grunden: bandbegränsade saw/pulse-oscillatorer, resonanta SVF-filter, syntade trummor. Inga samplingar, så inget behöver laddas ner förutom rösten.
- **Röst:** Piper TTS (`en_US-ryan-high`), helt offline, genom en 22-bands kanalvocoder med bärvåg på F2/C3/F3, blandad med ringmodulerad torrsignal. Det ger en monoton maskinröst som i en sci-fi-film.
- **Tonart och tempo:** F-moll, 125 BPM. Ackordföljd Fm – Db – Bbm – C (i–VI–iv–V, harmonisk moll), där C-dur ger dragningen tillbaka.
- **Form (112 takter, 3:39):** intro 16 · uppbyggnad 16 · drop 24 · break 16 · drop 32 · outro 8.
  - Intro: filtrerad pad och åttondelsarpeggio, impact, två repliker och riser.
  - Uppbyggnad: rak kick, filtret öppnas på bas och arp, virvelrulle och riser under 8 takter.
  - Drop 1: allt in. Rullande sextondelsbas med sidechain, lead_a och crashar var 8:e takt.
  - Break: trummorna ut, hållen bas, tre repliker och en 4-takters rulle tillbaka in.
  - Drop 2: leadet växlar mellan lead_a och den högre lead_b, dubblat en oktav ned.
  - Outro: filtret stängs, sista repliken "Midnight engine. Offline." och sedan uttoning.
- **Ljudbild:** distad bas (två saws plus suboktav-pulse genom tanh och en ren sinussub), tunga kickar med pitchenvelop och drive, 80-talsvirvel med clap och stort rum, pluckarp med ping-pong-delay på punkterad åttondel, supersaw-pad och supersaw-lead.
- **Mix:** sidechain-duckning från kicken på bas, pad, arp och lead. Ett delay och en reverb som bussar. Mastern har glue-kompressor, mjuk klippning och lookahead-limiter vid −1 dBFS. Integrerad loudness blir ca −8,6 LUFS (högt, som i genren).
- **Text:** egenskriven, på engelska, om en jakt genom "sector nine" fram till gryningen.
- **Ingen saxofon**, enligt prompten.

## Verifierat

- `out/song.mp3` avkodas felfritt hela vägen med ffmpeg och är 219,1 s lång (arrangemanget är 215 s plus reverb-svans).
- Varje sektion har ljud. Det finns inga tysta block före outrot, och toppnivån ligger på −1,0 dBFS.
