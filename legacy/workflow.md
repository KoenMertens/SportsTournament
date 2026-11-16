# Workflow voor Toernooi Aanmaken

## Stap-voor-stap proces:

### 1. Toernooi Aanmaken
- **Sport Type**: Tafeltennis (of later Padel)
- **Toernooi Type**: Default Tournament (Clubkampioenschap)
- **Team Type**: 
  - **Single**: Individueel (1 speler per team)
  - **Double**: Dubbelspel (2 spelers per team)
- **Troostfinale**: Ja/Nee (consolation bracket)

### 2. Spelers Toevoegen
- **Globale spelers database**: Spelers kunnen meerdere keren gebruikt worden
- **Nieuw speler toevoegen**: Voer naam in, wordt opgeslagen in globale database
- **Bestaande speler selecteren**: Kies uit lijst van bestaande spelers

### 3. Teams Samenstellen
**Voor Single (team_type = "single"):**
- Elke speler = 1 team
- Selecteer spelers die deelnemen
- Teams worden automatisch aangemaakt (1 speler per team)

**Voor Double (team_type = "double"):**
- Team = 2 spelers
- Selecteer 2 spelers per team
- Teams worden aangemaakt met 2 spelers

### 4. Matches Genereren
- **Poule fase**: Automatisch genereren van poule matches
  - Minimaal 3 teams nodig
  - Verdeling: 4 per poule (standaard), resterende in poules van 3
  - Iedereen speelt tegen iedereen in eigen poule

### 5. Poule Matches Invoeren
- Voer resultaten in per match
- Score = aantal sets gewonnen (bijv. 3-1 betekent 3 sets gewonnen)

### 6. Knockout Bracket Genereren
- **Voorwaarde**: Alle poule matches moeten gespeeld zijn
- **Automatisch**:
  - Top 2 van elke poule gaan door
  - Bracket wordt gegenereerd op basis van aantal teams
  - Bij 6 teams: 2 beste krijgen bye naar halve finale

### 7. Knockout Matches Invoeren
- Voer resultaten in voor elke knockout match
- Volgende ronde wordt automatisch bepaald door winnaars

### 8. Troostfinale (optioneel)
- Als `has_consolation = True`
- Verliezers uit knockout fase spelen verder in consolation bracket

## UI Flow Suggestie:

```
Hoofdmenu
├── Nieuw Toernooi
│   ├── Toernooi Details (naam, sport, type, team_type, consolation)
│   ├── Spelers Toevoegen
│   ├── Teams Samenstellen
│   └── Matches Genereren
│
└── Toernooien
    ├── [Selecteer Toernooi]
    │   ├── Overzicht
    │   ├── Spelers/Teams Beheren
    │   ├── Poule Standen
    │   ├── Poule Matches Invoeren
    │   ├── Knockout Bracket Genereren (knop verschijnt als poules klaar)
    │   ├── Knockout Matches Invoeren
    │   └── Troostfinale (indien van toepassing)
```

