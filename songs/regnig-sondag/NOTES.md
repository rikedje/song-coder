# Regnig söndag – anteckningar

Lo-fi hiphop om en regnig söndag inomhus. Låtprompten finns i `regnig-sondag.md`.

## Rendera om

```sh
./render.sh songs/regnig-sondag      # ljud, omslag och taggar
./tag.sh songs/regnig-sondag         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tempo:** 128 BPM, som önskat. Lo-fi ligger normalt på 70–90 BPM, så trummorna går i **halvtid**: kicken och virveln (på taktslag 3) ger en boom-bap-känsla runt 64 BPM, medan hi-hats och detaljer följer 128.
- **Tonart och ackord:** F-dur, med jazziga, rotlösa voicings. Huvudloopen är Gm9 – C13 – Fmaj9 – Dm9 (ii–V–I–vi). B-delarna går Bbmaj7 – Am7 – Gm9 – C7sus.
- **Form, en loop med variationer (96 takter, 3:04):** intro 8 · loop A 16 · loop A2 16 · B 16 · loop A3 16 · B2 16 · outro 8.
  - Intro: bara elpiano som öppnar sig, regn och vinyl.
  - Loop A: trummor och bas kommer in.
  - Loop A2: melodin, rim och tätare hi-hats.
  - B: ny ackordföljd, trummorna glesas ut och melodin svarar.
  - Loop A3: melodin en oktav upp.
  - B2: B-ackorden med fullt komp.
  - Outro: elpianot stängs och tonar ut i regnet.
- **Ljudbild (välj själv):**
  - Rhodes-liknande FM-elpiano (`epiano`), varm `softbass` och en mjuk, filtrerad saw-melodi som låter nästan som en visselflöjt.
  - Dova trummor och en hög rim.
  - Hela låten har **regn** på rutan och **vinylknaster**, två nya kontinuerliga ljudlager i motorn (`rain`, `vinyl`).
- **Inget för rent:** flera nya, frivilliga lo-fi-funktioner i motorn.
  - **Swing** (`swing: 0.28` på åttondelar) och **humanisering** (±7 ms i timing och ±12 % i styrka). Humaniseringen använder en egen slumpgenerator, så att andra låtar inte påverkas.
  - **Bitkross och sänkt samplingsfrekvens** per spår (`crush`, `downsample`) på trummor och röst.
  - **Tape** i mastern (`lofi`): wow (0,45 Hz) och flutter (6,5 Hz) som får tonhöjden att svaja lite, lågpass vid 9,5 kHz och bandmättnad.
- **Röst:** Piper `en_US-lessac-high`, med rent tal som mixen gör till gammal film eller radio (bandpass 350–3400 Hz, bitkross och tape). Sex korta repliker som jag har skrivit själv: "It's raining again." … "Sundays are made for this."
- **Omslag:** ny stil `rainwindow`, en våt fönsterruta med droppar och rinnande strimmor framför suddiga varma ljus.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 184,0 s lång, vilket stämmer med 96 takter (180 s) plus 4 s efterklang.
- Alla sektioner har ljud: intro −15,3, looparna −12,3 till −12,7, B-delarna −13,6/−12,4 och outro −17,5 dB RMS. Integrerad loudness ca −11,9 LUFS. Energin över 10 kHz ligger 34 dB under totalen, så det låter dovt och inte för rent.
- Motorändringarna ger exakt samma ljud i alla fem tidigare låtar (MD5 på ljudströmmen är oförändrad).
