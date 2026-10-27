# När jag ska somna vaknar jag – anteckningar

Ambient/drone om att ligga vaken när man försöker somna. Låtprompten finns i `nar-jag-ska-somna-vaknar-jag.md`.

## Rendera om

```sh
./render.sh songs/nar-jag-ska-somna-vaknar-jag      # ljud, omslag och taggar
./tag.sh songs/nar-jag-ska-somna-vaknar-jag         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tonart och tempo:** D-dur, 80 BPM, men tempot märks knappt eftersom det inte finns några trummor. Ackorden ligger två takter vardera (ca 6 s): Dmaj9 – Gmaj9 – Bm11 – Asus2. G-ackordet har C# (lydisk färg), vilket ger den svävande, olösta känslan.
- **Form, fritt flödande (60 takter, 3:09 inklusive 9 s efterklang):** fyra lager som tonar in i varandra utan tydliga gränser.
  - *Dimma* (12 takter): bara orgelpunkt på D och pad som långsamt öppnar sig.
  - *Ytor* (16 takter): glesa klockor kommer in, med de första viskningarna.
  - *Uppvaknande* (16 takter): ljusare filter, fler klockor och en nästan stillastående melodi. Här ligger den viskade titeln, alltså vändpunkten.
  - *Tillbaka* (16 takter): allt stängs och tunnas ut, och titeln viskas en sista gång.
- **Ljudbild:**
  - Drönare (supersaw med 4 s attack, filtrerad under 1,6 kHz) och en pad med 2,5 s attack.
  - En melodi spelad på ett mjukt padljud med 0,9 s attack.
  - Ett nytt instrument i motorn: `bell`, en FM-klocka med inharmonisk modulator, mjuk attack (40 ms) och lång efterklang.
  - En reverb på 6,5 s och en delay på punkterad fjärdedel med hög feedback.
- **Inga skarpa ljud:**
  - Ny funktion i motorn: `lowpass` per spår i `mix` (4:e ordningen). Den används på allt: viskningarna vid 3,5 kHz, melodin vid 3,8 kHz, klockorna vid 4,5 kHz och paden vid 5 kHz.
  - Reverben är mörk (dämpning vid 3,2 kHz). Inga trummor, ingen mättnad i mastern.
  - Mätt resultat: energin över 6 kHz ligger 55 dB under totalen.
- **Röst:** Piper `sv_SE-nst-medium`, mycket långsamt talad (`length_scale` 1,4), viskad via brus-vocodern med nästan ingen diskant. Den ligger långt bak i mixen med 85 % reverb och mycket delay, så att den knappt hörs. Sex korta repliker som jag har skrivit själv.
- **Loudness:** ca −16 LUFS, avsiktligt lågt och dynamiskt.
- **Omslag:** ny stil `nocturne`, med en suddig månskära bakom dimband på en natthimmel. Långa titlar radbryts nu automatiskt på omslaget.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 189,0 s lång, vilket stämmer med 60 takter (180 s) plus 9 s efterklang.
- Alla sektioner har ljud: dimma −19,9, ytor −18,2, uppvaknande −17,0 och tillbaka −18,7 dB RMS. Toppnivån ligger under −1,5 dBFS.
- Frekvensbalans: under 40 Hz −58 dB, 2–6 kHz −23 dB och över 6 kHz −55 dB, alla relativt totalen.
