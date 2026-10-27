# Nya tider – anteckningar

Instrumental syntpop i andan av tidig Depeche Mode (1981–83). Låtprompten finns i `nya-tider.md`. Allt material är eget: melodier, mönster och ackordföljder är nyskrivna, och inget är lånat från någon verklig låt.

## Rendera om

```sh
./render.sh songs/nya-tider      # ljud, omslag och taggar
./tag.sh songs/nya-tider         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Ingen röst:** syntmelodin (en lätt detunad lead med vibrato) tar sångens plats och bär både vers och refräng.
- **Tema, ett telefonsamtal utan ord:** en ringsignal spelad på pulsvåg (snabb drill mellan E6 och C6) öppnar låten ensam, återkommer i sticket och ringer i outrot. Samtalet blir aldrig besvarat.
- **Tonart och ackord:** A-moll, 118 BPM.
  - Vers: Am – F – C – G.
  - Refräng: F – G – C – Am, alltså samma ackord men startpunkten flyttad mot dur så att refrängen lyfter.
  - Stick: Dm – Em – F – G, som klättrar tillbaka in i refrängen.
- **Form, en klassisk poplåt (88 takter, 3:02):** intro (ringsignal, sedan trummaskin och sequencer) · vers 16 · refräng 8 · vers 16 · refräng 8 · stick 8 · dubbel refräng 16 · outro 8.
  - Den sista refrängen dubblas: melodin spelas också en oktav ned på en pulsvågssynt.
- **Ljudbild (retro syntar, skarpt, krispigt, gammal trummaskin):**
  - Trummaskin: kort och torr kick, krispig virvel med clap, snabba hi-hats och en öppen hi-hat i slutet av varje takt.
  - Nytt instrument i motorn: `metal`, ett metalliskt slag med inharmoniska övertoner, som en samplad städ eller ett rör, i två tonhöjder som svarar varandra. Den används i refränger och i vers 2.
  - Studsande oktavbas på fyrkantsvåg, ett snabbt pulsvågsarpeggio, korta saw-stabs och en lågmäld stråkmaskin i refrängerna.
  - Allt är monosyntar (`mono`) som startar om i fas 0. Ingen unison och ingen sidechain.
  - Kort rum (1,1 s), en åttondelsdelay och ingen mättnad i mastern.
- **Ingen gitarr.**
- **Omslag:** ny stil `geometric`, tidig 80-talsgrafik med platta färgblock, staplar, en röd cirkel och en spiralsladd från en telefon. Mörk titeltext (`text`) och ljus sidfot (`footer`), två nya omslagsinställningar.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 182,0 s lång, vilket stämmer med 88 takter (179 s) plus 3 s efterklang.
- Alla sektioner har ljud: ringsignalsintro −19,3, verser −14,7/−14,8, refränger −14,0 till −13,8, stick −14,3 och outro −17,9 dB RMS. Toppnivån är −1,0 dBFS och integrerad loudness ca −12,7 LUFS.
- Motorändringarna (nytt trumljud, nya omslagsinställningar och ny omslagsstil) rör inte befintliga ljudvägar. Alla tidigare omslag genererades om och är byte-identiska.
