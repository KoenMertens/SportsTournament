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

# Navigation tabs at the top
tab_overview, tab_new = st.tabs(["📋 Toernooien", "➕ Nieuw Toernooi"])

with tab_new:
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
                st.error("❌ Voer een toernooi naam in")
            else:
                try:
                    tournament_type_val = tournament_type_choice[1]
                    team_type_val = team_type_choice[1]
                    
                    if tournament_type_val == "default_tournament":
                        tournament = DefaultTournament(
                            name=tournament_name.strip(),
                            sport_type=sport_type,
                            tournament_type="default_tournament",
                            team_type=team_type_val,
                            has_consolation=has_consolation
                        )
                    else:
                        tournament = RoundRobinTournament(
                            name=tournament_name.strip(),
                            sport_type=sport_type,
                            tournament_type="round_robin",
                            team_type=team_type_val,
                            has_consolation=False
                        )
                    
                    tournament.save()
                    st.success(f"✅ Toernooi '{tournament.name}' aangemaakt!")
                    
                    # Store tournament ID to auto-select it
                    if 'created_tournament_id' not in st.session_state:
                        st.session_state.created_tournament_id = tournament.id
                    
                    st.info("💡 Voeg nu teams/spelers toe in het 'Toernooien' tabblad.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fout bij aanmaken: {str(e)}")
                    import traceback
                    with st.expander("🔍 Details"):
                        st.code(traceback.format_exc())

with tab_overview:
    st.subheader("📋 Toernooien Overzicht")
    
    tournaments = Tournament.get_all()
    
    if not tournaments:
        st.info("Nog geen toernooien. Maak er een aan via 'Nieuw Toernooi'.")
    else:
        # Tournament selector - auto-select newly created tournament
        tournament_options = {f"{t.name} ({t.sport_type})": t for t in tournaments}
        default_idx = 0
        
        if 'created_tournament_id' in st.session_state:
            # Find index of newly created tournament
            for idx, (name, t) in enumerate(tournament_options.items()):
                if t.id == st.session_state.created_tournament_id:
                    default_idx = idx
                    break
            # Clear it after use
            if 'created_tournament_id' in st.session_state:
                del st.session_state.created_tournament_id
        
        selected_tournament_name = st.selectbox(
            "Selecteer Toernooi",
            list(tournament_options.keys()),
            index=default_idx
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
            tab_teams, tab_standings, tab_matches, tab_settings = st.tabs(["👥 Teams & Spelers", "📊 Standen", "🎯 Matches", "⚙️ Instellingen"])
            
            with tab_teams:
                st.markdown("### Teams & Spelers Beheer")
                teams = tournament.get_teams()
                players = Player.get_by_tournament(tournament.id)
                
                # Players section
                st.markdown("#### 👥 Spelers Toevoegen")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if players:
                        st.markdown("**Bestaande Spelers:**")
                        player_df = pd.DataFrame([{"Naam": p.name} for p in players])
                        st.dataframe(player_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nog geen spelers toegevoegd")
                
                with col2:
                    new_player_name = st.text_input("Nieuwe Speler", key=f"new_player_{tournament.id}")
                    if st.button("➕ Toevoegen", key=f"add_player_{tournament.id}"):
                        if new_player_name.strip():
                            try:
                                player = Player.create_or_get_in_tournament(tournament.id, new_player_name.strip())
                                st.success(f"✅ {player.name} toegevoegd!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Fout: {e}")
                        else:
                            st.warning("Voer een naam in")
                
                st.markdown("---")
                
                # Teams section
                if not players:
                    st.warning("⚠️ Voeg eerst spelers toe voordat je teams maakt")
                elif len(players) < 3 and tournament.tournament_type == "default_tournament":
                    st.warning(f"⚠️ Minimaal 3 spelers nodig voor toernooi. Huidig: {len(players)}")
                else:
                    st.markdown("#### 🏃 Teams")
                    
                    if not teams:
                        st.info("Nog geen teams aangemaakt")
                        
                        if tournament.team_type == "single":
                            # Single: each player is a team
                            st.markdown("**Enkelspel**: Elke speler wordt automatisch een team")
                            if len(players) >= 3:
                                if st.button("🚀 Teams Aanmaken (alle spelers)", type="primary", key=f"create_all_teams_{tournament.id}"):
                                    try:
                                        for player in players:
                                            team = Team(
                                                tournament_id=tournament.id,
                                                player1=player
                                            )
                                            team.save()
                                        st.success(f"✅ {len(players)} teams aangemaakt!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Fout: {e}")
                            else:
                                st.error(f"❌ Minimaal 3 spelers nodig, huidig: {len(players)}")
                        
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
                                
                                if st.button("➕ Team Toevoegen", key=f"add_team_double_{tournament.id}"):
                                    p1 = Player.find_by_name_in_tournament(tournament.id, player1_name)
                                    p2 = Player.find_by_name_in_tournament(tournament.id, player2_name)
                                    if p1 and p2:
                                        team = Team(
                                            tournament_id=tournament.id,
                                            player1=p1,
                                            player2=p2
                                        )
                                        team.save()
                                        st.success(f"✅ Team '{team.display_name}' toegevoegd!")
                                        st.rerun()
                    
                    if teams:
                        st.markdown(f"**{len(teams)} teams aangemaakt:**")
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
                                            st.success(f"✅ {len(generated)} matches gegenereerd!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Fout: {e}")
                                else:
                                    st.info(f"ℹ️ Er zijn al {len(matches)} matches voor dit toernooi")
            
            with tab_standings:
                st.markdown("### 📊 Standen")
                matches = tournament.get_matches()
                
                if not matches:
                    st.info("Genereer eerst matches via het 'Teams & Spelers' tabblad")
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
            
            with tab_matches:
                st.markdown("### 🎯 Matches Invoeren")
                matches = tournament.get_matches()
                
                if not matches:
                    st.info("Genereer eerst matches via het 'Teams & Spelers' tabblad")
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
                                    
                                    if st.button("💾 Opslaan", key=f"save_{match.id}"):
                                        match.team1_score = score1
                                        match.team2_score = score2
                                        match.save()
                                        st.success("✅ Match opgeslagen!")
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
                                        st.success(f"✅ Knockout bracket gegenereerd! ({len(generated)} matches)")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Fout: {e}")
                            else:
                                st.info("ℹ️ Speel eerst alle poule matches voordat je knockout bracket genereert")
            
            with tab_settings:
                st.markdown("### ⚙️ Toernooi Instellingen")
                st.write(f"**Naam:** {tournament.name}")
                st.write(f"**Sport:** {tournament.sport_type}")
                st.write(f"**Type:** {tournament.tournament_type}")
                st.write(f"**Team Type:** {tournament.team_type}")
                st.write(f"**Troostfinale:** {'Ja' if tournament.has_consolation else 'Nee'}")
                st.write(f"**Aangemaakt:** {tournament.created_at}")
