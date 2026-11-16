# Tafeltennis clubkampioenschap

Eén bestand, `index.html`, dat volledig in de browser draait. Geen server, geen installatie, geen internet nodig.

## Gebruik

1. Open `index.html` in Chrome, Edge of Firefox (dubbelklikken volstaat), of zet de repo op GitHub Pages.
2. **Spelers**: vul namen en klassementen in (één per één of een hele lijst plakken: `Naam; C4`).
3. **Loting maken**: de spelers worden per sterkte in potten verdeeld en per pot over de poules geloot, zodat de sterkste spelers niet samen zitten. Je kunt nog spelers wisselen door er twee aan te klikken.
4. **Wedstrijden & tafels**: klik op *Vrije tafels vullen* en geef uitslagen in. Typ `11-7`, of kort `7` (11-7 gewonnen) of `-9` (9-11 verloren).
5. **Eindrondes**: als alle poules klaar zijn, maak je de hoofdtabel (top 2 per poule) en de troosttabel aan. Iedereen speelt door tot zijn eindplaats vaststaat.
6. **🖥 Scherm**: opent een tweede venster voor tv of beamer dat automatisch meevolgt.

## Formaat

- Poules van 4, of van 3 waar het niet uitkomt.
- 2 winnende sets tot 11; halve finales, finale en wedstrijd om plaats 3 naar 3 winnende sets (instelbaar).
- Poulestand: matchpunten (winst 2, verlies 1, forfait 0), bij gelijkstand het onderlinge resultaat (punten, sets, balpunten).
- Poulewinnaars zijn reekshoofd; spelers uit dezelfde poule zitten zo ver mogelijk uit elkaar in de tabel.
- Voorgift wordt niet door de app berekend.

## Gegevens en historiek

Alles wordt automatisch in de browser bewaard (`localStorage`) en overleeft herladen of afsluiten. Via *Instellingen & back-up* download je het hele tornooi als JSON-bestand. Bewaar dat bestand per tornooi als historiek, of laad het op een andere laptop om verder te werken.

Let op: werk altijd op dezelfde laptop en in dezelfde browser, en gebruik geen privévenster.

## Gratis hosten

GitHub → Settings → Pages → *Deploy from a branch* → `main` / root. De app staat dan op `https://koenmertens.github.io/SportsTournament/`. De gegevens blijven ook dan lokaal in de browser.

## Tests

```bash
node tests/logic.test.js
```

Speelt honderden volledige tornooien na (3 tot 40 spelers) en controleert poules, standen, tabellen en eindklassement.

## Vorige versie

De oorspronkelijke Streamlit-app staat in `legacy/`.
