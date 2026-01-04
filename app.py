"""
Streamlit Tournament Management App
OOP-based tournament management system
"""
import streamlit as st
import pandas as pd
from database import init_db

# Import models in correct order to avoid circular dependencies
from models.player import Player
from models.team import Team
from models.match import Match, MatchPhase
from models.tournament import Tournament
from tournament_types.default_tournament import DefaultTournament
from tournament_types.round_robin import RoundRobinTournament

# Page config
st.set_page_config(
    page_title="Toernooi Beheer",
    page_icon="🏆",
    layout="wide"
)

# Initialize database
init_db()

# Main app
st.title("🏆 Toernooi Beheer Systeem")
st.markdown("Tafeltennis & Padel Toernooien")

# Sidebar navigation
page = st.sidebar.selectbox("Menu", [
    "Toernooien Overzicht",
    "Nieuw Toernooi",
    "Spelers Beheer"
])

if page == "Spelers Beheer":
    st.subheader("👥 Spelers Beheer")
    st.markdown("Globale spelers database - spelers kunnen gebruikt worden in meerdere toernooien")
    
    # List all players
    players = Player.get_all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Beschikbare Spelers")
        if players:
            player_df = pd.DataFrame([{"Naam": p.name, "ID": p.id} for p in players])
            st.dataframe(player_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nog geen spelers toegevoegd")
    
    with col2:
        st.markdown("### Nieuwe Speler")
        new_player_name = st.text_input("Speler Naam", key="new_player")
        if st.button("Speler Toevoegen", type="primary"):
            if new_player_name.strip():
                try:
                    player = Player.create_or_get(new_player_name.strip())
                    st.success(f"Speler '{player.name}' toegevoegd/beschikbaar! (ID: {player.id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fout bij toevoegen: {e}")
            else:
                st.warning("Voer een naam in")

elif page == "Nieuw Toernooi":
    st.subheader("➕ Nieuw Toernooi Aanmaken")
    
    with st.form("create_tournament"):
        tournament_name = st.text_input("Toernooi Naam *")
        sport_type = st.selectbox("Sport Type *", ["Tafeltennis", "Padel"])
        tournament_type_choice = st.selectbox("Toernooi Type *", [
            ("Default Tournament", "default_tournament"),
            ("Vriendschappelijk (Round-Robin)", "round_robin")
        ], format_func=lambda x: x[0])
        
        team_type_choice = st.selectbox("Team Type *", [
            ("Enkel", "single"),
            ("Dubbel", "double")
        ], format_func=lambda x: x[0])
        
        has_consolation = False
        if tournament_type_choice[1] == "default_tournament":
            has_consolation = st.checkbox("Troostfinale (Consolation Bracket)")
        
        submitted = st.form_submit_button("Toernooi Aanmaken", type="primary")
        
        if submitted:
            if not tournament_name.strip():
                st.error("Voer een toernooi naam in")
            else:
                try:
                    if tournament_type_choice[1] == "default_tournament":
                        tournament = DefaultTournament(
                            name=tournament_name.strip(),
                            sport_type=sport_type,
                            tournament_type="default_tournament",
                            team_type=team_type_choice[1],
                            has_consolation=has_consolation
                        )
                    else:
                        tournament = RoundRobinTournament(
                            name=tournament_name.strip(),
                            sport_type=sport_type,
                            tournament_type="round_robin",
                            team_type=team_type_choice[1],
                            has_consolation=False
                        )
                    
                    tournament.save()
                    st.success(f"Toernooi '{tournament.name}' aangemaakt!")
                    st.info("Ga naar 'Toernooien Overzicht' om teams en spelers toe te voegen.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fout bij aanmaken: {e}")

elif page == "Toernooien Overzicht":
    st.subheader("📋 Toernooien Overzicht")
    
    tournaments = Tournament.get_all()
    
    if not tournaments:
        st.info("Nog geen toernooien. Maak er een aan via 'Nieuw Toernooi'.")
    else:
        # Tournament selector
        tournament_options = {f"{t.name} ({t.sport_type})": t for t in tournaments}
        selected_tournament_name = st.selectbox(
            "Selecteer Toernooi",
            list(tournament_options.keys())
        )
        
        if selected_tournament_name:
            tournament = tournament_options[selected_tournament_name]
            
            # Tournament info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sport", tournament.sport_type)
            with col2:
                st.metric("Team Type", "Enkel" if tournament.team_type == "single" else "Dubbel")
            with col3:
                st.metric("Type", "Default" if tournament.tournament_type == "default_tournament" else "Round-Robin")
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["Teams", "Standen", "Matches", "Instellingen"])
            
            with tab1:
                st.markdown("### Teams Beheer")
                teams = tournament.get_teams()
                
                if not teams:
                    st.info("Nog geen teams toegevoegd aan dit toernooi")
                    
                    # Add teams section
                    st.markdown("#### Teams Toevoegen")
                    players = Player.get_all()
                    
                    if not players:
                        st.warning("Voeg eerst spelers toe via 'Spelers Beheer'")
                    else:
                        if tournament.team_type == "single":
                            # Single: each player is a team
                            st.markdown("**Enkelspel**: Elke speler is automatisch een team")
                            selected_players = st.multiselect(
                                "Selecteer Spelers",
                                [p.name for p in players],
                                key=f"select_players_{tournament.id}"
                            )
                            
                            if st.button("Teams Aanmaken", key=f"create_teams_single_{tournament.id}"):
                                if len(selected_players) >= 3:
                                    for player_name in selected_players:
                                        player = Player.find_by_name(player_name)
                                        if player:
                                            team = Team(
                                                tournament_id=tournament.id,
                                                player1=player
                                            )
                                            team.save()
                                    st.success(f"{len(selected_players)} teams aangemaakt!")
                                    st.rerun()
                                else:
                                    st.error("Selecteer minimaal 3 spelers")
                        
                        else:
                            # Double: need 2 players per team
                            st.markdown("**Dubbelspel**: Selecteer 2 spelers per team")
                            
                            if len(players) < 2:
                                st.warning("Minimaal 2 spelers nodig voor dubbelspel")
                            else:
                                st.markdown("**Nieuwe Team Samenstellen:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    player1_name = st.selectbox(
                                        "Speler 1",
                                        [p.name for p in players],
                                        key=f"team_p1_{tournament.id}"
                                    )
                                with col2:
                                    available_players = [p.name for p in players if p.name != player1_name]
                                    player2_name = st.selectbox(
                                        "Speler 2",
                                        available_players,
                                        key=f"team_p2_{tournament.id}"
                                    )
                                
                                if st.button("Team Toevoegen", key=f"add_team_double_{tournament.id}"):
                                    p1 = Player.find_by_name(player1_name)
                                    p2 = Player.find_by_name(player2_name)
                                    if p1 and p2:
                                        team = Team(
                                            tournament_id=tournament.id,
                                            player1=p1,
                                            player2=p2
                                        )
                                        team.save()
                                        st.success(f"Team '{team.display_name}' toegevoegd!")
                                        st.rerun()
                                    
                                # Show existing teams
                                if teams:
                                    st.markdown("**Bestaande Teams:**")
                                    for team in teams:
                                        st.write(f"- {team.display_name}")
                else:
                    st.markdown(f"**{len(teams)} teams in dit toernooi:**")
                    team_list = [{"Team": t.display_name, "Type": "Dubbel" if t.is_double else "Enkel"} for t in teams]
                    st.dataframe(pd.DataFrame(team_list), use_container_width=True, hide_index=True)
                    
                    # Generate matches button (only if tournament type supports it)
                    if tournament.tournament_type == "default_tournament":
                        if len(teams) >= 3:
                            matches = tournament.get_matches()
                            if not matches:
                                if st.button("🎯 Poule Matches Genereren", type="primary", key=f"gen_matches_{tournament.id}"):
                                    try:
                                        generated = tournament.generate_matches()
                                        st.success(f"{len(generated)} matches gegenereerd!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fout: {e}")
                            else:
                                st.info(f"Er zijn al {len(matches)} matches voor dit toernooi")
            
            with tab2:
                st.markdown("### Standen")
                matches = tournament.get_matches()
                
                if not matches:
                    st.info("Genereer eerst matches via het Teams tabblad")
                else:
                    phase = st.selectbox(
                        "Selecteer Fase",
                        ["poule", "knockout", "consolation"] if tournament.tournament_type == "default_tournament" else ["poule"],
                        key=f"phase_select_{tournament.id}"
                    )
                    
                    standings = tournament.get_standings(phase=phase)
                    if not standings.empty:
                        st.dataframe(standings, use_container_width=True)
                    else:
                        st.info("Geen standen beschikbaar voor deze fase")
            
            with tab3:
                st.markdown("### Matches Invoeren")
                matches = tournament.get_matches()
                
                if not matches:
                    st.info("Genereer eerst matches via het Teams tabblad")
                else:
                    # Filter matches by phase
                    phase = st.selectbox(
                        "Selecteer Fase",
                        ["poule", "knockout", "consolation"] if tournament.tournament_type == "default_tournament" else ["poule"],
                        key=f"match_phase_{tournament.id}"
                    )
                    
                    phase_matches = [m for m in matches if m.phase.value == phase]
                    
                    if not phase_matches:
                        st.info(f"Geen matches in fase '{phase}'")
                    else:
                        # Show unplayed matches first
                        unplayed = [m for m in phase_matches if not m.is_played]
                        played = [m for m in phase_matches if m.is_played]
                        
                        if unplayed:
                            st.markdown("#### Nog Te Spelen")
                            for match in unplayed:
                                with st.expander(f"⚪ {match.team1.display_name} vs {match.team2.display_name}"):
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.write(f"**{match.team1.display_name}**")
                                    with col2:
                                        score1 = st.number_input("Sets", min_value=0, key=f"score1_{match.id}", value=0)
                                    with col3:
                                        st.write(f"**{match.team2.display_name}**")
                                    with col4:
                                        score2 = st.number_input("Sets", min_value=0, key=f"score2_{match.id}", value=0)
                                    
                                    if st.button("Opslaan", key=f"save_{match.id}"):
                                        match.team1_score = score1
                                        match.team2_score = score2
                                        match.save()
                                        st.success("Match opgeslagen!")
                                        st.rerun()
                        
                        if played:
                            st.markdown("#### Gespeelde Matches")
                            played_data = [{
                                "Team 1": m.team1.display_name,
                                "Score": f"{m.team1_score}-{m.team2_score}",
                                "Team 2": m.team2.display_name,
                                "Winnaar": m.winner.display_name if m.winner else "Gelijk"
                            } for m in played]
                            st.dataframe(pd.DataFrame(played_data), use_container_width=True, hide_index=True)
                    
                    # Generate knockout bracket button (for default tournament)
                    if (tournament.tournament_type == "default_tournament" and 
                        isinstance(tournament, DefaultTournament)):
                        poule_matches = [m for m in matches if m.phase == MatchPhase.POULE]
                        knockout_matches = [m for m in matches if m.phase == MatchPhase.KNOCKOUT]
                        
                        if poule_matches and not knockout_matches:
                            all_played = all(m.is_played for m in poule_matches)
                            if all_played:
                                if st.button("🎯 Knockout Bracket Genereren", type="primary", key=f"gen_knockout_{tournament.id}"):
                                    try:
                                        generated = tournament.generate_knockout_matches()
                                        st.success(f"Knockout bracket gegenereerd! ({len(generated)} matches)")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fout: {e}")
                            else:
                                st.info("Speel eerst alle poule matches voordat je knockout bracket genereert")
            
            with tab4:
                st.markdown("### Toernooi Instellingen")
                st.write(f"**Naam:** {tournament.name}")
                st.write(f"**Sport:** {tournament.sport_type}")
                st.write(f"**Type:** {tournament.tournament_type}")
                st.write(f"**Team Type:** {tournament.team_type}")
                st.write(f"**Aangemaakt:** {tournament.created_at}")
