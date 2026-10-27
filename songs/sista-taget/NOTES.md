# Sista tåget – anteckningar

Melankolisk elektronika om en stad som somnar, där ljusen slocknar ett efter ett. Låtprompten finns i `sista-taget.md`.

## Rendera om

```sh
./render.sh songs/sista-taget
```

Kommandot körs från repots rot. Det installerar verktygen vid behov (uv-hanterad Python 3.12 och Pipers svenska röst `sv_SE-nst-medium`) och skriver:

- `out/song.wav` (24 bit, 44,1 kHz)
- `out/song.mp3` (320 kbps, med ID3-taggar, låttext och inbäddat omslag)
- `out/cover.jpg` (1500×1500)

## Filer

| Fil | Innehåll |
|---|---|
| `song.yaml` | tempo, tonart, ackord, sektioner, instrument, mix, master och metadata/omslag |
| `patterns.yaml` | trum-, bas-, elpiano-, arpeggio-, pad- och leadmönster |
| `lyrics.yaml` | de viskade replikerna och var de ligger |

## Val jag gjort

- **Tonart och tempo:** D-moll, 105 BPM. A-delen går Dm9 – Bbmaj7 – Fmaj7 – Cadd9 (i–VI–III–VII), vemodig men framåtlutad. B-delen går Gm7 – Bbmaj7 – Dm – A (iv–VI–i–V), där A-dur drar hem igen. Utvidgade ackord (9:or och maj7) ger Röyksopp-känslan.
- **Form (80 takter, 3:08 inklusive efterklang):** intro 8 · A 16 · B 24 · A' 24 · coda 8.
  - Intro: pad och hållet elpiano, shaker de sista fyra takterna.
  - A: halvtidskick, flytande bas, elpianokomp. Leadet kommer in efter 8 takter.
  - B: ny ackordföljd, rak fyra-kick, clap, arpeggio med delay, staccato-elpiano och B-temat i leadet. Tre viskningar. De två sista takterna andas utan trummor.
  - A': allt in. Leadet växlar mellan A-temat och en högre variant, med en viskning i takt 12. Trummorna glesas ut i slutet.
  - Coda: filtret stängs, sista viskningen "Godnatt, staden." och uttoning.
- **Ljudbild (ingen distorsion):**
  - Två nya instrumenttyper i motorn: `softbass` (filtrerad saw och sinussub, ingen drive) och `epiano` (FM-elpiano med tine-attack och stereotremolo).
  - Mjuk kick (låg pitchenvelop, nästan ingen drive) och dämpad clap.
  - Supersaw-pad med lång attack, lugn supersaw-lead med låg cutoff.
  - Mastern har mättnaden avstängd (`saturation: 0`). Bara en ren limiter tar topparna.
- **Röst:** Piper `sv_SE-nst-medium`, långsamt talad (`length_scale` 1,25). Den görs till viskning genom att talet vocodas på rent brus (28 band), med lite luftig diskant ovanpå, så rösten saknar tonhöjd precis som en riktig viskning. Texten är egenskriven.
- **Mix:** lätt sidechain-pump från kicken. Lång reverb (3,4 s) och punkterad åttondelsdelay på arp, lead och elpiano. Mjukare loudness, ca −12,9 LUFS integrerat.
- **Omslag:** stilen `nightcity`, en stadssiluett där fönstren slocknar från vänster till höger, med det sista tåget som en ljusstrimma som lämnar bilden.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 187,9 s lång, vilket stämmer med 80 takter (182,9 s) plus 5 s efterklang.
- Alla sektioner har ljud: intro −17,8, A −14,3, B −14,2, A' −13,4 och coda −19,0 dB RMS. Toppnivån är −1,0 dBFS.
- ID3v2.3-taggar finns: titel, artist/kodare song-coder, datum, genre, BPM, tonart, kommentar, låttext (USLT) och omslaget som APIC.
