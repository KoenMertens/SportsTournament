# Tafeltennis clubkampioenschap

Eén bestand, `index.html`, dat volledig in de browser draait. Geen server, geen installatie, geen internet nodig.

## Gebruik

1. Open `index.html` in Chrome, Edge of Firefox (dubbelklikken volstaat), of zet de repo op GitHub Pages.
2. **Spelers**: vul namen en klassementen in (één per één of een hele lijst plakken: `Naam; C4`). Namen staan als Familienaam Voornaam (`De Moerloose Wim`), zodat alfabetisch sorteren op familienaam gebeurt.
3. **Loting maken**: de spelers worden op klassement over de poules verdeeld volgens het slangsysteem (A1, B1, … en dan terug), zodat de sterkste spelers niet samen zitten. Bij gelijk klassement kies je zelf: alfabetisch (standaard), omgekeerd alfabetisch, willekeurig of de volgorde van je lijst. Je kunt ook laten loten binnen de potten, of twee spelers wisselen door ze aan te klikken.
4. **Wedstrijden & tafels**: klik op *Vrije tafels vullen* en geef uitslagen in. Typ `11-7`, of kort `7` (11-7 gewonnen) of `-9` (9-11 verloren).
5. **Eindrondes**: maak de hoofdtabel (top 2 per poule) en de troosttabel aan. Dat kan ook al terwijl er nog poules bezig zijn: de tabel toont dan "1ste poule A" en vult zich vanzelf in zodra een poule klaar is. Iedereen speelt door tot zijn eindplaats vaststaat. Na het aanmaken kun je geen laatkomer meer toevoegen.
6. **🖥 Scherm**: opent een tweede venster voor tv of beamer dat automatisch meevolgt.

## Talen

De app bestaat in het Nederlands (standaard), Frans en Engels. Kies de taal rechtsboven (NL / FR / EN) of in *Instellingen & back-up*; de keuze wordt onthouden in de browser. Ook de wedstrijdbriefjes, het pouleblad en het tv-scherm volgen de taal. Een link kan meteen een taal openen: `index.html?lang=fr` of `?lang=en`.

Alle teksten staan in het Nederlands in de code (`L('…')`); de Franse en Engelse vertaling staat in `I18N_TABLE` bovenaan het script. De tests controleren dat elke zin een vertaling heeft.

## Formaat

- Poules van 4, of van 3 waar het niet uitkomt (de poules van 3 zijn A, B, C).
- Eindrondes volgens de vaste clubtabellen voor 2 tot 8 poules ("Tabellen voor eindrondes"): één tabel voor de 1ste en 2de, één voor de 3de en 4de.
- 2 winnende sets tot 11; halve finales, finale en wedstrijd om plaats 3 naar 3 winnende sets (instelbaar).
- Poulestand: matchpunten (winst 2, verlies 1, forfait 0), bij gelijkstand het onderlinge resultaat (punten, sets, balpunten).
- Puntenaanpassing (Instellingen): **voorgift** (standaard: de laagst geklasseerde begint elke set met 1 punt per 2 klassementen verschil voorsprong, iedereen speelt tot 11), **handicap** (oud systeem: de hoogst geklasseerde speelt verder dan 11) of **geen aanpassing**. De app toont dit per wedstrijd en op de briefjes, en controleert de setstanden daarop.
- Volgorde in een poule van 4: 1-4, 2-3, 1-3, 2-4, 1-2, 3-4 (hoogst geplaatste eerst).
- Elke speler heeft een vast nummer in zijn poule (de volgorde van de loting). Dat nummer staat op het pouleblad en voor elke wedstrijd ("1-4"). In de loting wissel je twee spelers door ze aan te klikken, ook binnen dezelfde poule.
- "Wedstrijdbriefjes poules" drukt één blad per poule af, in de volgorde van het pouleblad, met de voorgift op elk briefje.
- In de eindrondes zijn wedstrijden die al gespeeld kunnen worden groen gekleurd.
- Clubleden kiezen: standaard de vaste ledenlijst van TTC Sterke Stut (werkt offline). Via de keuzelijst **Club** kun je de leden en klassementen van een andere club ophalen bij VTTL (TabT-API, zonder login; heeft internet nodig).
- De clubfoto zit in de repo (`clubfoto.jpg`); het logo (`logo.png`) en de twee achtergrondfoto's (`achtergrond-links.jpg`, `achtergrond-rechts.jpg`) ook.
- Bij poulewedstrijden stelt de app een poulegenoot voor die telt.
- Wedstrijdbriefjes kun je afdrukken, per poule of voor de lopende wedstrijden.

## Gegevens en historiek

Alles wordt automatisch in de browser bewaard (`localStorage`) en overleeft herladen of afsluiten. Via *Instellingen & back-up* download je het hele tornooi als JSON-bestand. Bewaar dat bestand per tornooi als historiek, of laad het op een andere laptop om verder te werken.

Let op: werk altijd op dezelfde laptop en in dezelfde browser, en gebruik geen privévenster.

## Gratis hosten

GitHub → Settings → Pages → *Deploy from a branch* → `main` / root. De app staat dan op `https://koenmertens.github.io/clubkampioenschap-tafeltennis/`. De gegevens blijven ook dan lokaal in de browser.

## Tests

```bash
node tests/logic.test.js
```

Speelt honderden volledige tornooien na (3 tot 40 spelers) en controleert poules, standen, tabellen en eindklassement.

## Maker

Gemaakt door [MKict](https://mkict.be). De vermelding staat onderaan elke pagina en op de afdrukken. Daarnaast staat een link naar de trainer van de club, [capatt.be](https://www.capatt.be/) ("Les nodig?"), alleen op het scherm. Het logo staat in de repo (`mkict-logo.png`, en `mkict-logo-wit.png` voor het donkere tv-scherm).
