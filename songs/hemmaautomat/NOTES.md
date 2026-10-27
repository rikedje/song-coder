# Hemmaautomat – anteckningar

Elektronisk popmusik i Kraftwerk-anda om ett hem som sköter sig självt. Låtprompten finns i `hemmaautomat.md`. Allt är eget: melodier, mönster och text är nyskrivna och inget riff är lånat. Inspirationen ligger i formen, klangerna och den monotona vocoderrösten.

## Rendera om

```sh
./render.sh songs/hemmaautomat      # ljud, omslag och taggar
./tag.sh songs/hemmaautomat         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tonart och tempo:** C-moll, 115 BPM. **Inga ackordbyten i onödan:** intro, verser och outro står helt still på Cm. Bara hooken växlar till Bb och tillbaka, två takter åt gången.
- **Form (88 takter, 3:07):** typisk Kraftwerk-form, med lång uppbyggnad, korta upprepade versrader, en instrumental hook i stället för sjungen refräng, en lång instrumental mitt och en lång uttoning.
  - Intro (16 takter, byggs lager för lager): oktavbas ensam, sedan hi-hat och datorpip, sedan trummor och sequencer, och en tom-fill in i första versen.
  - Vers 1, hook, vers 2, hook: versen har bas, trummor och stråkmaskin, där vocodern pratar fyra rader och avslutar med "Home automat." Hooken är en pulsvågsmelodi över sequencern.
  - Mitt (16 takter): sextondelsbas, en tätare sequencer, elektroniska toms som svarar varandra och fler pip. Systemmeddelanden: "Updating firmware … Please wait … Update complete." Hooken återkommer en oktav ned.
  - Vers 3, hook 3 (hooken dubblad en oktav ned), och sedan outro där filtret stängs under 8 takters uttoning.
- **Ljudbild (gamla syntar, krispigt, torrt):**
  - Nytt instrument i motorn: `mono`, en klassisk monosynt med en oscillator (pulse, saw eller sinus) som alltid startar i fas 0, plus en filterenvelope. Ingen unison och inga detunade lager. Den används till oktavbasen (fyrkant), sequencern (saw med hög resonans och kort envelope), hooken (25 % pulsvåg) och pipen (korta sinustoner).
  - Ny trumma i motorn: `etom`, en elektronisk tom med snabbt pitchfall.
  - Kort, torr kick, en kort clap-virvel och krispiga sextondels-hi-hats.
  - Stråkmaskin: `superpad` med bara 3 röster och liten detune, i stället för en modern supersaw.
  - Nästan inget rum (1,2 s reverb, låga sändningar), ingen sidechain-pump och ingen mättnad i mastern.
- **Röst:** Piper `en_US-ryan-high` genom vocodern, med bärvågen låst på C2/G2/C3. Den ändrar alltså aldrig tonhöjd: monoton pratsång. Vocoderandelen är 85 %. Texten är egenskriven om kylskåp, robotdammsugare och en termostat med egna planer.
- **Omslag:** ny stil `circuit`, ett kretskort där ledningarna ritar ett hus med ett tänt fönster.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 186,7 s lång, vilket stämmer med 88 takter (183,7 s) plus 3 s efterklang.
- Alla sektioner har ljud: introt byggs från −17 till −15 dB RMS, verser och hooks ligger runt −14, mitten på −13,0 och outrot på −22,3 (uttoning). Toppnivån är −1,0 dBFS och integrerad loudness ca −12,8 LUFS.
- Ändringen i motorn (trumljud cachas per spår i stället för per typ) ger exakt samma ljud i alla fyra tidigare låtar (MD5 på ljudströmmen är oförändrad).
