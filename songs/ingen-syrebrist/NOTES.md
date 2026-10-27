# Ingen syrebrist – anteckningar

Instrumental, rymdinspirerad elektronika med gamla fina syntstråkar, i andan av Jean-Michel Jarre och Klaus Schulze. Låtprompten finns i `ingen-syrebrist.md`. Allt material är eget: melodi, ackordföljder och sequencermönster är nyskrivna.

## Rendera om

```sh
./render.sh songs/ingen-syrebrist      # ljud, omslag och taggar
./tag.sh songs/ingen-syrebrist         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tonart och tempo:** A-moll, 118 BPM.
  - Tema A: Am – F – Dm – E, två takter per ackord. E-dur drar tillbaka mot Am.
  - Tema B: F – G – Am – Am – F – G – E – E, ett ackord per takt, under melodin.
- **Form (jag valde själv, 88 takter, 3:05):** intro 8 · tema A 16 · tema B 16 · mellanspel 8 · tema A2 8 · tema B2 16 · coda 16. Rymdresan:
  - Intro: stråkmaskinen sveper in, pukslag och rymd-zap, sedan kommer sequencern.
  - Tema A: rytmbox, en pulserande bas och en sequencer i sextondelar vars filter öppnas.
  - Tema B: melodin och pukor som svarar.
  - Mellanspel: bara stråkar och en pukvirvel, med zap och riser.
  - Tema A2: en tätare sequencervariant.
  - Tema B2: melodin en oktav upp.
  - Coda: filter och stråkar stängs och tonar ut.
- **Ljudbild (stråkar och pukor):**
  - Nytt instrument i motorn: `strings`, en stråkmaskin som en gammal string ensemble. Saw i 8' och 4', långsam envelope och den klassiska **ensemblekorusen**: tre modulerade delay-tappar med 120° fasförskjutning, spridda i stereo. Den bär hela låten.
  - Nytt trumljud i motorn: `timpani`, stämda pukor med membranets övertoner (1 / 1,5 / 1,98 / 2,44), lätt tonhöjdsglid och en filtklubba. Två pukor stämda i A1 och E2, alltså tonika och dominant. De används till slag på ettan, svar och en virvel.
  - Schulze-sequencer: en mono-saw med hög resonans och kort filterenvelope, plus en pulserande åttondelsbas.
  - Jarre-lead: en sjungande lead med vibrato, lång delay och reverb.
  - Rytmbox: mjuk kick, hi-hats och en clave i tresillo.
  - Rymdeffekter: nytt `zap`, en resonant sinus som faller snabbt i tonhöjd, plus risers.
- **Rum:** 3,5 s reverb och en lång delay på punkterad fjärdedel. Ingen mättnad i mastern.
- **Omslag:** ny stil `orbit`, en halvbelyst planet med omloppsbanor som går bakom och framför den, en liten måne och en stjärnhimmel.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 185,0 s lång, vilket stämmer med 88 takter (179 s) plus 6 s efterklang.
- Alla sektioner har ljud: intro −16,9, tema A −14,1, tema B −13,5, mellanspel −13,4, A2 −13,7, B2 −13,7 och coda −16,6 dB RMS. Toppnivån är −1,0 dBFS och integrerad loudness ca −12,1 LUFS.
- Motorändringarna (`strings`, `timpani`, `zap`, `ensemble` och omslagsstilen `orbit`) är nya funktioner. Inga befintliga ljud- eller omslagsvägar ändrades.
