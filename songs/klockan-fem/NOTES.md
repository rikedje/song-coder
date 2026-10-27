# Klockan fem – anteckningar

Euforisk, pianodriven house om att inte vilja gå hem från dansgolvet. Låtprompten finns i `klockan-fem.md`.

## Rendera om

```sh
./render.sh songs/klockan-fem      # ljud, omslag och taggar
./tag.sh songs/klockan-fem         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tonart och tempo:** F-dur, 140 BPM. Hela låten är samma fyrtaktsloop, F – C – Dm – Bb (I–V–vi–IV). I fjärde varvet vänds den till Dm – Bb – F – C, vilket ger samma ackord men en ny tyngdpunkt.
- **Form, en loop med variationer (104 takter, 3:02):** intro 8 · varv1 16 · varv2 16 · paus 8 · varv3 24 · varv4 24 · outro 8.
  - Intro: filtrerat pianoackord, ett ensamt "home!" och hi-hats.
  - Varv 1: kick, klapp, offbeat-bas, pianostötar och pad.
  - Varv 2: rösthooken, arpeggio och ett tätare pianomönster.
  - Paus: pianot håller ackorden, pianoriffet kommer, frasen sägs rent en gång, sedan klapprulle och riser.
  - Varv 3: allt samtidigt, med riff och hook.
  - Varv 4: den vända loopen med ett eget riff, rullande bas och en hackig hook ("home, home, home").
  - Outro: filtret stängs och låten tonar ut.
- **Ljudbild:**
  - Nytt instrument i motorn: `piano`, ett additivt housepiano med lätt inharmoniska övertoner, två strängar per ton och hammarklick. Det används både för ackordstötar och för riffet.
  - Pumpande offbeat-bas (`softbass`) med kraftig sidechain, supersaw-pad, pluck-arpeggio med delay, kick och klapp.
- **Röst-hook:**
  - Ny funktion i motorn: röstklipp (`chops`). Varje ord ("don't", "wanna", "go", "home!", "one more", "song.") läses in separat med Piper `en_US-lessac-high`. Klippen triggas sedan från mönster i `patterns.yaml` (`@a`, `@b` …), som samplingar.
  - Varje klipp vocodas mot den takt­ens ackord och blandas 55/45 med originalet. Då följer kroken harmonierna, som en stämd housevokal.
  - Ett klipp klingar tills nästa klipp börjar, så att orden hinner höras.
  - I pausen sägs hela frasen rent: "It's five in the morning. And I don't wanna go home."
- **Mix och master:** loudness ca −8,3 LUFS, som i genren. Måttlig mättnad i mastern och en limiter på −1 dBFS.
- **Omslag:** ny stil `dawnclock`, med gryningshimmel, ljusstrålar och en klocka som visar fem.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 182,3 s lång, vilket stämmer med 104 takter (178,3 s) plus 4 s efterklang.
- Alla sektioner har ljud: intro −14,8, varven −9,0 till −9,3, paus −10,6 och outro −12,2 dB RMS. Toppnivån är −1,0 dBFS.
- De tidigare låtarna renderar till exakt samma ljud som förut (MD5 på ljudströmmen är oförändrad).
