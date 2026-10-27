# Maskinkropp – anteckningar

EBM i andan av DAF och Nitzer Ebb, där dansgolvet blir ett träningsläger. Låtprompten finns i `maskinkropp.md`. Allt material är eget: basgångar, mönster och text är nyskrivna, och inga rader är lånade.

## Rendera om

```sh
./render.sh songs/maskinkropp      # ljud, omslag och taggar
./tag.sh songs/maskinkropp         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tempo och tonart:** 125 BPM, E-moll. Basen står på E i intro, verser och stick. Bara refrängen kliver C – D – Em, för att lyfta.
- **Form, en klassisk poplåt (88 takter, 2:51):** intro 8 · vers 16 · refräng 8 · vers 16 · refräng 8 · stick 8 · refräng 16 · outro 8.
  - Intro: kick och en sequencerbas vars filter öppnas, sedan hi-hats.
  - Verser: rak fyra-kick, en tydlig virvel på 2 och 4, sextondels-hi-hats och offbeat-öppna hi-hats. Kommandon var fjärde takt.
  - Refränger: metalliska slag, tätare oktavhopp i basen och korta saw-stabs.
  - Stick: trummorna ut ("Halt! … Stillstand."), bara bas och metall, sedan kick och virvelrulle in i sista refrängen ("Und los!").
  - Outro: basfiltret stängs.
- **Ljudbild (four on the floor, tight och tydlig virvel, tung synthbas):**
  - Kick med lätt drive, en kort och hård virvel med clap (decay 0,1 s, drive 2) och hi-hats.
  - Basen är en `distbass` i sextondelar med resonant filter och drive, som en gammal monosynt med sequencer. Den har betoning på varje fjärdedel och oktavhopp på offbeat, plus en sub under.
  - Metalliska slag (`metal`) i refrängerna.
- **Ingen reverbsoppa:** reverben är bara 0,8 s med låga sändningar, delayen är kort med låg feedback och sidechainen är mild. Allt ligger nära och torrt.
- **Röst:** Piper `de_DE-thorsten-high` med den nya röststilen `shout`. Rösten bandbegränsas, normaliseras, överstyrs (drive 4,5) och får ett slapback-eko på 90 ms. Talsyntesen kan inte skrika, men så här blir kommandona hårda och framåt. Texten (egen, på tyska):
  - *Beweg dich! · Arme hoch! · Nach links! · Nach rechts!*: rör dig, armarna upp, åt vänster, åt höger.
  - *Maschinenkörper! · Schweiß und Stahl!*: maskinkropp, svett och stål (refrängen).
  - *Spür den Takt! · Atme ein! · Atme aus! · Schneller! Schneller!*: känn takten, andas in, andas ut, snabbare.
  - *Halt! · Stillstand. · Und los!*: stopp, stillastående, och kör!
- **Omslag:** ny stil `gears`, svarta kugghjul som griper i varandra på röd botten.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 171,0 s lång, vilket stämmer med 88 takter (169 s) plus 2 s efterklang.
- Alla sektioner har ljud: −9,0 till −9,5 dB RMS genom hela låten och −11,0 i outrot. Toppnivån är −1,0 dBFS och integrerad loudness ca −8,3 LUFS, alltså tätt och hårt.
- Motorändringarna (röststilen `shout` och omslagsstilen `gears`) rör inte befintliga ljud- eller omslagsvägar.
