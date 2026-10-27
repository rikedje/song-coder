# Ljusfart – anteckningar

Liquid drum & bass om en satellitsignal som fångas upp mitt i natten. Låtprompten finns i `ljusfart.md`.

## Rendera om

```sh
./render.sh songs/ljusfart      # ljud, omslag och taggar
./tag.sh songs/ljusfart         # bara omslag och taggar
```

Utdata hamnar i `out/`: `song.wav` (24 bit), `song.mp3` (320 kbps, taggad, med inbäddat omslag) och `cover.jpg`.

## Val jag gjort

- **Tempo:** 172 BPM i stället för ~150 i mallen. Drum & bass ligger på 170–175, och vid 150 försvinner den rullande känslan. Genren vägde tyngre än det ungefärliga tempoförslaget.
- **Tonart och ackord:** F#-moll, liquid-ackord två takter vardera: F#m9 – Dmaj9 – Bm9 – C#7sus4 (i–VI–iv–V).
- **Form (128 takter, 3:03), en klassisk DJ-vänlig DnB-form:** intro 16 · build 16 · drop 32 · breakdown 16 · drop 32 · outro 16.
  - Intro: pad, filtrerat elpiano och satellitpip som ett morseanrop. Hi-hats de sista 8 takterna, och MC:n tar emot signalen.
  - Build: tvåstegs-breaket kommer in, filtret öppnas, sedan virvelrulle, riser och "Locked on."
  - Drop 1: "Lightspeed!", sinus-sub, spökslag i virveln, klockarpeggio och crash var 8:e takt.
  - Breakdown: trummorna ut, och padden och pipen bär "A signal from the stars."
  - Drop 2: som drop 1 plus en liquid-melodi över åtta takter.
  - Outro: trummorna och subben tonar ut för DJ-mixning.
- **Ljudbild (välj själv):** tvåstegs-break (kick på 1 och efter 3, virvel på 2 och 4, med spökslag), krispiga sextondels-hi-hats och ride på offbeat. Rhodes-liknande elpiano, bred supersaw-pad, FM-klockor i arpeggio, korta sinuspip som satellitsignal och en mjuk lead i andra droppen.
- **Ingen aggressiv bas:** basen är en ren sinus-sub (`mono` med `osc: sine`) som följer kicken, plus en lågmäld, ofiltrerad `softbass` för att den ska höras i små högtalare. Ingen reese, ingen distorsion, ingen rävbas.
- **Röst:** Piper `en_US-ryan-high`, rent och lite snabbt talat (`length_scale` 0,95), med kraftiga delay-kast som en MC över ett rave-ljudsystem. Nio korta utrop som jag har skrivit själv: "Incoming signal." … "Lightspeed!" … "Satellite one. Signal locked."
- **Omslag:** ny stil `hyperspace`, stjärnor utdragna till strimmor mot en ljus punkt.

## Verifierat

- `out/song.mp3` avkodas felfritt med ffmpeg och är 182,6 s lång, vilket stämmer med 128 takter (178,6 s) plus 4 s efterklang.
- Alla sektioner har ljud: intro −13,0, build −9,9, droppar −9,5/−9,3, breakdown −10,9 och outro −11,9 dB RMS. Toppnivån är −1,0 dBFS och integrerad loudness ca −8,2 LUFS, som i genren.
- Motorn ändrades bara med en ny omslagsstil, inget i ljudkedjan. Därför behövdes ingen kontroll av de tidigare låtarna.
