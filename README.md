# Tafeltennis clubkampioenschap

Eén bestand, `index.html`, dat volledig in de browser draait. Geen server, geen installatie, geen internet nodig.

## Gebruik

1. Open `index.html` in Chrome, Edge of Firefox (dubbelklikken volstaat), of zet de repo op GitHub Pages.
2. **Spelers**: vul namen en klassementen in (één per één of een hele lijst plakken: `Naam; C4`).
3. **Loting maken**: de spelers worden op klassement over de poules verdeeld volgens het slangsysteem (A1, B1, … en dan terug), zodat de sterkste spelers niet samen zitten. Bij gelijk klassement telt de volgorde van je lijst. Je kunt ook laten loten binnen de potten, of twee spelers wisselen door ze aan te klikken.
4. **Wedstrijden & tafels**: klik op *Vrije tafels vullen* en geef uitslagen in. Typ `11-7`, of kort `7` (11-7 gewonnen) of `-9` (9-11 verloren).
5. **Eindrondes**: als alle poules klaar zijn, maak je de hoofdtabel (top 2 per poule) en de troosttabel aan. Iedereen speelt door tot zijn eindplaats vaststaat.
6. **🖥 Scherm**: opent een tweede venster voor tv of beamer dat automatisch meevolgt.

## Formaat

- Poules van 4, of van 3 waar het niet uitkomt (de poules van 3 zijn A, B, C).
- Eindrondes volgens de vaste clubtabellen voor 2 tot 8 poules ("Tabellen voor eindrondes"): één tabel voor de 1ste en 2de, één voor de 3de en 4de.
- 2 winnende sets tot 11; halve finales, finale en wedstrijd om plaats 3 naar 3 winnende sets (instelbaar).
- Poulestand: matchpunten (winst 2, verlies 1, forfait 0), bij gelijkstand het onderlinge resultaat (punten, sets, balpunten).
- Voorgift (optioneel): de laagst geklasseerde speelt tot 11, de hoogst geklasseerde tot 11 plus 1 punt per 2 klassementen verschil. De app toont de doelscores per wedstrijd en op de briefjes, en controleert de setstanden daarop.
- Bij poulewedstrijden stelt de app een poulegenoot voor die telt.
- Wedstrijdbriefjes kun je afdrukken, per poule of voor de lopende wedstrijden.

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
