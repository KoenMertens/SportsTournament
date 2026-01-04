# Tafeltennis Clubkampioenschap / Padel Toernooi

Een Streamlit applicatie voor het beheren van clubkampioenschappen en toernooien waar iedereen tegen iedereen speelt (round-robin).

## Features

- 🏓 Toernooi beheer (Tafeltennis en Padel)
- 👥 Speler management
- 📊 Automatische stand berekening
- 🎯 Wedstrijd invoer
- 📈 Wedstrijdgeschiedenis
- 🔄 Round-robin toernooi (iedereen tegen iedereen)

## Lokaal Installeren

1. Clone de repository:
```bash
git clone <jouw-repo-url>
cd PadelTournament
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

### Stap 1: Push naar GitHub

1. Maak een nieuwe repository op GitHub
2. Voeg alle bestanden toe en commit:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <jouw-github-repo-url>
git push -u origin main
```

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

