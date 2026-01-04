# Sports Tournament Management System

Een Streamlit applicatie voor het beheren van tafeltennis en padel toernooien met OOP-architectuur.

## Features

- 🏓 Toernooi beheer (Tafeltennis en Padel)
- 👥 Globale spelers database (herbruikbaar)
- 📊 Automatische stand berekening per poule
- 🎯 Wedstrijd invoer met sets scores
- 📈 Poule fase met automatische verdeling
- 🔄 Knockout bracket generatie
- 🏆 Default Tournament (Poules → Knockout → Troostfinale)
- 🤝 Round-robin toernooi (vriendschappelijk)
- ⚙️ Enkel en dubbelspel ondersteuning

## Lokaal Installeren

1. Clone de repository:
```bash
git clone https://github.com/KoenMertens/SportsTournament.git
cd SportsTournament
```

2. Installeer dependencies:
```bash
pip install -r requirements.txt
```

3. Run de applicatie:
```bash
streamlit run app.py
```

De app zal openen op `http://localhost:8501`

## Deployen naar Streamlit Cloud (GRATIS!)

### Stap 1: Code staat al op GitHub! ✅

Je repository is al op GitHub: https://github.com/KoenMertens/SportsTournament

### Stap 2: Deploy op Streamlit Cloud

1. Ga naar [share.streamlit.io](https://share.streamlit.io)
2. Log in met je GitHub account
3. Klik op "New app"
4. Selecteer je repository en branch
5. Stel de main file in als `app.py`
6. Klik op "Deploy"

De app wordt automatisch gedeployed en je krijgt een gratis URL zoals:
`https://jouw-app-naam.streamlit.app`

### Automatische Updates

Elke keer dat je code pusht naar GitHub, wordt de app automatisch bijgewerkt op Streamlit Cloud!

## Database

De applicatie gebruikt SQLite voor lokale opslag. De database wordt automatisch aangemaakt bij de eerste run.

## Toekomstige Uitbreidingen

- Export naar Excel/CSV
- Statistieken en grafieken
- Meerdere toernooien gelijktijdig
- Export van standen
- Email notificaties

