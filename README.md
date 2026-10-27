# song-coder

Låtar gjorda helt av kod. Du svarar på några frågor om känsla, tempo, form, ljud och röst. Sedan skriver [Claude Code](https://claude.com/claude-code) noterna, syntar alla ljud, mixar, viskar eller robotpratar texten, ritar ett omslag och lämnar en färdig `song.mp3`. Allt sker offline, utan samplingar och utan molntjänster.

> **TL;DR:** Det här är en lek. Ta det inte på allvar. Använd det gärna om du vill, men allt sker på egen risk och ingen kan hållas ansvarig för något. Se [Ansvarsfriskrivning](#ansvarsfriskrivning-läs-det-här) och [LICENSE](LICENSE).

---

## Det här är en lek – på riktigt

Projektet är ett **experiment för skojs skull**. Det kom till en kväll ur frågan "Kan man be en AI-agent att göra en hel låt från noll, bara med kod?" och svaret blev "ja, typ".

Ta det inte på något särskilt allvar. Konkret betyder det:

- **Det är inget musikverktyg.** Det är ingen DAW, inget plugin och ingen produkt. Ingen roadmap, inga releaser, ingen support och inga löften.
- **Musiken låter som den låter.** Ibland överraskande bra, ibland som en ledsen hiss på väg till en parkeringsplats. Båda utfallen är helt i sin ordning.
- **Koden är skriven för att det ska gå fort och vara roligt,** inte för att vara snygg, effektiv, testad eller hållbar. Det finns inga tester. Inga alls. Det var ett medvetet val, eller i alla fall ett val.
- **Mycket är skrivet av en AI** och har bara kontrollerats lagom noga. Siffrorna i `NOTES.md` stämde när de skrevs, men hur låtarna *låter* har ingen människa granskat på allvar.
- **Saker kan sluta fungera när som helst:** nya Python-versioner, nya paketversioner, en ändrad röstmodell eller att jag helt enkelt tappar intresset.
- **Låtarna är inte konst med anspråk.** Texterna är skrivna på en minut och omslagen är rektanglar och cirklar. Det är meningen.
- **Ingen bör bygga något viktigt ovanpå det här.** Inte en tjänst, inte ett företag, inte en skoluppgift du behöver godkänt på och inte ett bröllopsframträdande.

Om du hittar en bugg är den troligen en feature. Om du hittar en feature är den troligen en bugg. Om du blir glad av att lyssna har projektet gjort mer än det lovade.

## Hur det fungerar

1. **Fråga:** skillen `/ny-lat` i Claude Code ställer några frågor och fyller i mallen [`mall.md`](mall.md).
2. **Skriv:** Claude skriver låten som läsbara textfiler i `songs/<låt>/`:
   - `song.yaml`: tempo, ackord, form, instrument, mix och omslag
   - `patterns.yaml`: noter och trummönster i en enkel textnotation
   - `lyrics.yaml`: texten och var den ligger
3. **Rendera:** motorn i `tools/songcoder/` gör resten:
   - syntar allt ljud från grunden (oscillatorer, filter och syntade trummor)
   - gör tal med [Piper](https://github.com/OHF-Voice/piper1-gpl) och processar det till robot eller viskning
   - mixar och mastrar
   - skriver wav och mp3 med ID3-taggar och ett genererat omslag

### Kom igång

Det här behövs: macOS eller Linux, [uv](https://docs.astral.sh/uv/) och nätverk vid första körningen, för Python-paket och röstmodell. Efter det fungerar allt offline.

```sh
./render.sh songs/midnattsmotor     # renderar om en befintlig låt
./tag.sh                            # gör bara om omslag och ID3-taggar för alla låtar, ljudet lämnas orört
```

Vill du göra en ny låt öppnar du repot i Claude Code och skriver `/ny-lat`.

Allt som skapas hamnar i `songs/<låt>/out/`:

- `song.mp3` med taggar och inbäddat omslag
- `song.wav` i 24 bit
- `cover.jpg`

### Låtar hittills

| Låt | Stil | Tempo |
|---|---|---|
| [Midnattsmotor](songs/midnattsmotor/) | mörk synthwave, robotprat om en biljakt | 125 BPM, F-moll |
| [Sista tåget](songs/sista-taget/) | melankolisk elektronika, svenska viskningar | 105 BPM, D-moll |
| [Klockan fem](songs/klockan-fem/) | euforisk pianohouse, hackad röst-hook | 140 BPM, F-dur |
| [När jag ska somna vaknar jag](songs/nar-jag-ska-somna-vaknar-jag/) | ambient/drone, avlägsna viskningar | 80 BPM, D-dur |
| [Hemmaautomat](songs/hemmaautomat/) | Kraftwerk-inspirerad electro, vocoderprat om ett smart hem | 115 BPM, C-moll |
| [Regnig söndag](songs/regnig-sondag/) | lo-fi hiphop i halvtid, regn, vinyl och filmrepliker | 128 BPM, F-dur |
| [Ljusfart](songs/ljusfart/) | liquid drum & bass, MC-utrop om en satellitsignal | 172 BPM, F#-moll |
| [Nya tider](songs/nya-tider/) | instrumental syntpop à la tidig Depeche Mode, en ringsignal som aldrig besvaras | 118 BPM, A-moll |
| [Maskinkropp](songs/maskinkropp/) | EBM med tunga sequencerbasar och hårda tyska kommandon | 125 BPM, E-moll |

## Ansvarsfriskrivning (läs det här)

Allt i det här repot (kod, ljudfiler, bilder, texter, dokumentation, mallar, skills och allt annat) tillhandahålls **i befintligt skick ("as is")**, utan någon som helst garanti, uttrycklig eller underförstådd.

**Upphovspersonen kan aldrig hållas ansvarig för någonting i eller som har med repot att göra.** Det gäller bland annat:

- skador på hårdvara, mjukvara, data, hörsel, högtalare, grannrelationer eller självkänsla
- förlorad tid, förlorade pengar, förlorade möjligheter eller förlorad musiksmak
- att något inte fungerar, fungerar fel eller fungerar alldeles för bra
- vad du eller någon annan gör med koden, ljudet, bilderna eller texterna
- hur det AI-genererade innehållet låter, ser ut, tolkas eller används
- intrång, tvister eller anspråk av något slag som uppstår vid användning

Ansvarsfriskrivningen gäller **utan undantag, nu, i framtiden och för alltid**, i den utsträckning lagen tillåter. Använder du något härifrån gör du det helt på egen risk och tar själv fullt ansvar för det.

## Licens

Repots eget innehåll släpps som **public domain** under [The Unlicense](LICENSE). Du får kopiera, ändra, sälja, sprida och använda det till vad du vill, kommersiellt eller inte, utan att fråga och utan att nämna mig. Licensen innehåller samma ansvarsfriskrivning som ovan: ingen garanti och inget ansvar.

**Undantag: tredjepartsdelar har egna licenser.** Unlicense gäller bara det som skapats i det här repot. Följande har sina egna villkor:

- Typsnittet `fonts/SpaceGrotesk.ttf` omfattas av SIL Open Font License, se [`fonts/OFL-SpaceGrotesk.txt`](fonts/OFL-SpaceGrotesk.txt).
- Python-beroendena, bland andra Piper, numpy, scipy, numba, Pillow, mutagen och lameenc, har sina egna licenser.
- Röstmodellerna som Piper laddar ner till `voices/` finns inte i repot och har egna licenser. Kontrollera dem själv innan du använder röster i något annat än lek.
