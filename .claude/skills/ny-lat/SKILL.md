---
name: ny-lat
description: Skapa en ny färdig låt från grunden. Ställer frågor som fyller i låtmallen (mall.md), sparar den ifyllda mallen i en egen låtkatalog under songs/ och producerar sedan låten (wav + mp3) helt offline. Använd när användaren vill göra en ny låt, kör /ny-lat, eller säger t.ex. "gör en låt", "ny låt".
---

# Ny låt

Arbetsflöde i tre steg: **fråga → fyll i mallen → gör låten.** Kommunicera med användaren på svenska.

## 1. Fråga

Ställ frågorna med AskUserQuestion, i två omgångar med högst 4 frågor var. Ge 2–4 konkreta förslag per fråga som passar det användaren redan sagt, och lägg alltid till "Välj själv" som ett alternativ. Användaren kan skriva fritt via "Other".

**Omgång 1:**
1. **Känsla och referenser:** stämning och ett par artister eller låtar.
2. **Tempo / tonart / längd:** t.ex. "92 BPM, A-moll, ca 3 min".
3. **Form:** t.ex. intro – vers – refräng – vers – refräng – outro.
4. **Ljudbild:** vilka instrument som bär och vad som ska bort.

**Omgång 2**, där förslagen anpassas efter svaren i omgång 1:
1. **Röst:** ingen / prat / rap / sång, plus språk, karaktär och var i låten.
2. **Text:** användarens egen text (klistras in via "Other"), "skriv själv om X" eller ingen text. Hoppa över frågan om rösten är "ingen".
3. **Får inte finnas:** det som absolut ska undvikas.
4. **Låtens namn:** föreslå 2–3 namn som passar svaren.

Om användaren redan har gett svar i sitt meddelande (t.ex. `/ny-lat mörk synthwave 100 BPM`) ställer du inte de frågorna igen.

## 2. Fyll i mallen och skapa låtkatalogen

- Gör en slug av namnet: gemener, a–z, siffror och bindestreck, där å/ä→a och ö→o (t.ex. "Nattåg mot Öst" → `nattag-mot-ost`).
- Skapa `songs/<slug>/`. Om katalogen redan finns lägger du till `-2`, `-3` osv.
- Kopiera `mall.md` från repots rot till `songs/<slug>/<slug>.md` och ersätt varje `[...]`-platshållare med svaret. Lägg till en rubrik överst: `# <Låtens namn>`. Behåll instruktionstexten ovanför `---` som den är, så att filen fungerar som en självständig låtprompt.
- Svar som är "Välj själv" skriver du in som "välj själv".

## 3. Gör låten

Följ den ifyllda mallen (`songs/<slug>/<slug>.md`) som den prompt den är. Det betyder: fråga inget mer, stanna inte för godkännande, välj själv och dokumentera besluten. Anpassningar för den här repostrukturen:

- **Allt som hör till låten ligger i `songs/<slug>/`:** `song.yaml` (form, ackord, instrument, mix), `patterns.yaml` (noter och trummönster), `lyrics.yaml` (text och röst, bara om låten har röst), `NOTES.md` och `out/song.wav` + `out/song.mp3`. Utgå från en befintlig låt, t.ex. `songs/midnattsmotor/`, som förlaga för formatet. Notationen förklaras överst i dess `patterns.yaml`.
- **Gemensam motor:** `tools/songcoder/` (se repots `CLAUDE.md`). Om låten behöver ett nytt ljud lägger du till en instrumenttyp eller FX i motorn i stället för låtspecifik kod, och ser till att tidigare låtar fortfarande renderar. Python är uv-hanterad 3.12. Använd inte systemets Python-versioner.
- **Rendera** med `./render.sh songs/<slug>` (installerar vid behov). Skriv kommandot i låtens `NOTES.md`. Balansera mixen med hjälp av utskriften av RMS/topp per spår.
- **Git:** committa och pusha inte förrän användaren säger till.
- **Verifiera innan du är klar:** kontrollera med `ffprobe` att `out/song.mp3` avkodas och har den längd som arrangemanget anger. Lyssna gärna av delar genom att analysera nivåer, så att inget spår är tyst eller klipper.

Avsluta med en kort sammanfattning till användaren: låtens namn, sökvägarna till mp3 och wav, renderingskommandot och de viktigaste valen du gjorde.
