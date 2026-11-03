# En ospelad B-sida – anteckningar

Långsam, raspig och avkopplande lo-fi-jazz på piano och en gammal trummaskin, som en LP som legat bortglömd. En viskande radioröst säger några rader om regn och te då och då. Låtprompten finns i `en-ospelad-b-sida.md`. Allt material är eget.

## Rendera om

```sh
./render.sh songs/en-ospelad-b-sida      # ljud, omslag och taggar
./tag.sh songs/en-ospelad-b-sida         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tempo och tonart:** 66 BPM, A-moll. Jazzackord med ett ackord per takt.
  - A-delen: Am9 – Dm9 – G13 – Cmaj9 – Fmaj9 – Bm7b5 – E7b9 – Am9, en vanlig moll-kvintcirkel som landar hemma igen.
  - Bryggan (B): Fmaj9 – Em9 – Dm9 – Cmaj9 – Fmaj9 – Em9 – Bm7b5 – E7. Den går nedåt stegvis och slutar på E7, som drar tillbaka till A.
- **Form, AABA (56 takter, 3:28):** intro 4 · A 8 · A 8 · B 8 · A 8 · B 8 · A 8 · outro 4. Efter den klassiska AABA-formen spelas bryggan och A en gång till, så att låten når ca 3:30.
  - Intro: bara brutna pianoackord vars filter öppnas, plus regn och skivknaster. "Det regnar igen."
  - A1: pianomelodin, en lugn bas, kick och hi-hat.
  - A2: virveln kommer in. Melodin går ned och landar på grundtonen.
  - B1: hållna ackord, en svag stråkmaskin i bakgrunden och två viskade rader.
  - A3: melodin en oktav upp, med brutna ackord under.
  - B2: trummorna tystnar nästan helt och rösten tar plats. En upptakt på virveln leder in i sista A.
  - Outro: pianot klingar av på Am9, regnet kommer tillbaka och sedan tonar allt ut.
- **Trummaskin:** nya trumljud i motorn som efterliknar Roland TR-606 Drumatix.
  - `kick606`: en kort, torr dov sinus nästan utan tonhöjdssvep.
  - `snare606`: två dämpade toner plus tunt brus.
  - `hat606`: metallklang av fyrkantsvågor i ett smalt band. Ett annat `decay` ger en öppen hi-hat.

  Trummorna är lätt krossade (sänkt samplingsfrekvens, 11–12 bitar), som om de samplats från skiva. De går nästan rakt (lite swing) och är lätt slarvigt spelade.
- **Piano:** motorns additiva `piano` med två nya parametrar. `detune` stämmer strängarna isär så att det låter som ett gammalt, lite ostämt piano. `hammer` styr hammarljudet. Vänster hand spelar ackord (brutna eller hållna) och höger hand melodin.
- **Bas och stråkar:** en mjuk, mörk bas som mest håller grundtonen och en mycket svag stråkmaskin (`strings`) i bryggorna. Båda är gamla ljud, inget modernt.
- **LP-känsla ("raspig"):**
  - Skivknaster (`vinyl`) under hela låten. Jag lade till parametrarna `crackle`, `pops` och `hiss`, som här är tätare än i Regnig söndag.
  - Master-bandsteget (`lofi`) svajar med 0,55 Hz, vilket motsvarar en skiva på 33 varv per minut som inte ligger helt plant. Mastern har också ett lowpass vid 8 kHz och lite drive.
- **Röst:** Piper `sv_SE-nst-medium`, viskning (brusvocoder) och långsamt tempo (`length_scale` 1,3). Mixen gör den till en gammal radio: bandpass 380–3000 Hz, sänkt samplingsfrekvens och 9 bitar. Jag skrev sju korta rader om regn och te.
- **Inga moderna ljud:** inga risers, superpads, rena digitala syntar eller hårda transienter.
- **Omslag:** ny stil `record`. Det är ett slitet skivomslag i kräm med ett ringmärke, och skivan glider ut med en tom röd etikett där det bara står "B". En tekopp med ånga syns ovanifrån.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 207,7 s lång, vilket stämmer med 56 takter (203,6 s) plus 4 s efterklang.
- Alla sektioner har ljud: intro −21,1, A1 −15,6, A2 −15,2, B1 −16,1, A3 −15,1, B2 −17,0, A4 −15,3 och outro −21,3 dB RMS. Toppnivån är −0,9 dBFS och integrerad loudness ca −13,5 LUFS.
- Motorändringarna (`piano`, `vinyl`, och att fx-poster skickas in som parametrar) har standardvärden som ger samma resultat som förut. Jag renderade om Klockan fem och Regnig söndag, och MD5 på ljudströmmen är oförändrad.
