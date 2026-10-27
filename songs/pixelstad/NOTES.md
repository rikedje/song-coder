# Pixelstad – anteckningar

Glad 8-bit-chiptune om en stad gjord av pixlar, med arkadutrop. Låtprompten finns i `pixelstad.md`. Allt material är eget, och inga melodier är lånade från något spel.

## Rendera om

```sh
./render.sh songs/pixelstad      # ljud, omslag och taggar
./tag.sh songs/pixelstad         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tempo och tonart:** 125 BPM, C-dur, I–V–vi–IV (C – G – Am – F). Breaket går F – G – Em – Am. Efter utropet "Level up!" byter andra droppen tonart upp till D-dur (D – A – Bm – G), ett klassiskt spelgrepp.
- **Form, en uppbyggnad (96 takter, 3:05):** intro 8 · build 16 · drop 24 · break 16 · drop 24 · outro 8.
  - Intro: bara arpeggioackord, med "Insert coin." och "Ready?"
  - Build: triangelbas, kick och hi-hats. Den slutar med en tvåtakters klättring uppåt plus en virvelrulle, i stället för en modern riser.
  - Drop 1: melodin med vibrato, full brustrumma och "Bonus!" och "Extra life!"
  - Break: en lugnare melodi utan trummor, "Bonus stage!" och klättringen igen.
  - Drop 2 i D-dur: melodin transponerad, dubblad av en tunn pulsvåg (12,5 %) en oktav under. "High score!"
  - Outro: "Game over?" och "Continue?" Sedan tystnar allt utom en kort slutsignal, som när spelet tar slut.
- **Inga moderna ljud: bara det en gammal ljudkrets klarar.** Två pulskanaler, en triangel och brus, inga filter, ingen reverb, ingen delay och ingen mättnad.
  - Melodi: pulsvåg 50 % utan filter, med fördröjd vibrato som en speldrivrutin (nytt i `mono`: `vibrato`, `vibrato_hz`, `vibrato_delay`, `filter: false`).
  - Ackord: ny instrumenttyp `chiparp`, där en pulsvåg (25 %) bläddrar genom ackordtonerna 50 gånger i sekunden. Så spelade gamla spelkonsoler ackord på en kanal.
  - Bas: ny oscillator `tri4` i `mono`, en trekantsvåg i 4 bitar (16 trappsteg), som i NES-triangeln.
  - Trummor: nya `chipkick` (en trappstegad triangel som faller i tonhöjd), `chipsnare` och `chiphat` (brus som ±1-värden som hålls kvar i olika takt, utan filter).
- **Röst:** Piper `en_US-ryan-high`, rent tal som mixen krossar till ett 8-bitarssample: bandpass, sänkt samplingsfrekvens (÷4) och 5 bitar. Elva korta arkadutrop som jag har skrivit själv.
- **Omslag:** ny stil `pixelcity`, en glad stad ritad i 50×50 pixlar med en begränsad palett, uppskalad utan utjämning.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 185,4 s lång, vilket stämmer med 96 takter (184,3 s) plus 1 s efterklang.
- Alla sektioner har ljud: intro −22,6 (bara arpeggio), build −14,4, drop 1 −13,3, break −13,9, drop 2 −13,3 och outro −13,0 dB RMS. Toppnivån är −1,0 dBFS och integrerad loudness ca −10,9 LUFS.
- `mono` byggdes ut. Därför renderades de fem låtar som använder den om, och de gav exakt samma ljud (MD5 på ljudströmmen är oförändrad).
