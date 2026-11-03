# Så säger Adam att det ska låta – anteckningar

Modern, elektronisk R&B med swing i halvtakt, syntetiska handklapp och subbig kick. Versen är gles och torr, pre-chorus staplar stämmor över stigande arpeggion och refrängen landar bred och blank. Låtprompten finns i `sa-sager-adam-att-det-ska-lata.md`. Allt material är eget.

## Rendera om

```sh
./render.sh songs/sa-sager-adam-att-det-ska-lata      # ljud, omslag och taggar
./tag.sh songs/sa-sager-adam-att-det-ska-lata         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Tolkningar av svaren

- **Text:** svaret var "Så säger Adam att det ska låta". Jag tolkade det som låtens ämne. Rösten skulle vara engelsk, så jag skrev en engelsk text där hooken är titeln översatt: "That's how Adam says it should sound". Texten handlar om att följa Adams instruktioner, så versraderna beskriver produktionen ("Claps that never touched a hand").
- **Får inte finnas:** svaret var samma text som känslobeskrivningen. Stilen kan inte vara det som ska undvikas, så jag tolkade det som felklistrat och valde själv: inget akustiskt, ingen lo-fi-textur, inget dist.
- **Mellantempo och 128 BPM:** beskrivningen säger mellantempo och tempovalet säger 128 BPM. Båda stämmer genom halvtakt: klappen ligger på trean i varje takt, så att känslan blir 64 BPM medan hi-hat och arpeggion rör sig i 128.

## Val jag gjort

- **Tonart och ackord:** C-dur, ett ackord per två takter.
  - Vers: Cmaj9 – Am9 – Fmaj9 – G13.
  - Pre-chorus: Dm9 – Em7 – Fmaj9 – Gsus/G13.
  - Refräng: Fmaj9 – G13 – Em7 – Am9, andra halvan Fmaj9 – G13 – Cmaj9.
  - Stick: Am9 – Em7 – Fmaj9 – Cmaj9. Lyft: Dm9 – Em7 – Fmaj9 – G13.
- **Form (128 takter, 4:04 med efterklang):** intro 8 · vers 16 · pre 8 · refräng 16 · vers 16 · pre 8 · refräng 16 · stick 8 · lyft 8 · refräng 16 · outro 8.
- **Sång:** Piper `en_US-lessac-high` sjunger ord för ord. Varje ord sträcks ut och får sin ton med WORLD-vocodern (`pyworld`), med scoop, glid och vibrato. Noter och text ligger i `lyrics.yaml`.
  - Vers: torr, centrerad närbild utan reverb.
  - Pre-chorus: stämmor en ters upp och en kvart ned, panorerade.
  - Refräng: stämmor en ters ned plus gemensamma dubblingar med flyttade formanter (som andra strupar), vida isär och en oktav ned.
  - Delaykast på utvalda ord ("hook", "line", "why", "fall", "sound"). De går via spåret `throw`, som bara hörs som eko.
- **Ljud:** bara syntar och trummaskin. `softbass` för sub, `pluck` filtrerad i versen, `pluck` för arpeggion och ackordstötar, `superpad` för blanka ackord och `bell` för små digitala klockspel.
- **Nytt i motorn:**
  - Sångstilen med `sing`-rader och `layers` (se `CLAUDE.md`), ny beroende `pyworld`.
  - Trumljudet `clap` och FX:et `reverse`, en baklänges svällning som slutar på taktslaget. Den ligger inför var fjärde takt.
  - `kick` har fått `length`. `mix` har fått `comp`, `air` och `dry`.
- **Omslag:** `nightcity` utan ändringar, en stad sent på natten.

## Kända begränsningar

- Rösten är TTS som tvingas till toner, ord för ord. Den låter syntetisk och binder inte ihop orden som en sångare, vilket jag lät stå som en del av den digitala karaktären.
- Mixen är balanserad efter mätvärden (RMS, topp, frekvensband, stereobredd) och tonhöjden är kontrollmätt. Den är inte avlyssnad.
