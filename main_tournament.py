# Texas Hold'em Bot Hackathon Tournament
from rich.console import Console
from game_logic import TexasHoldemGame
from setup.tournament_ui import TournamentUI
from setup.tournament_stats import TournamentStats
from setup.tournament_analysis import TournamentAnalyzer
from player_pool import get_all_bots, get_bot_summary
import setup.configure_tournament as config
from ParentBot import ParentBot
import random
from typing import Dict, Any, Tuple

console = Console()

def run_betting_round(game: TexasHoldemGame, ui: TournamentUI, round_name: str, 
                     stats: TournamentStats):
    """
    Run a complete betting round with UI coordination and statistics tracking.
    
    Args:
        game: The game logic instance
        ui: The UI instance
        round_name: Name of the betting round ('Pre-flop', 'Flop', etc.)
        stats: Statistics tracker
    """
    ui.display_betting_round_header(round_name)
    
    if round_name != "Pre-flop":
        ui.clear_screen()
        game_state = game.get_game_state()
        ui.display_persistent_game_state(
            game_state['players'], round_name, game_state['community_cards'],
            game_state['pot'], game_state['current_bet'], game_state['dealer_pos'],
            game_state['side_pots'], game_state['main_pot']
        )
    
    betting_order = game.get_betting_order(round_name)
    last_raiser_pos = None
    players_to_act = [pos for pos in betting_order if not game.players[pos].folded and not game.players[pos].all_in]
    
    players_acted = set()
    
    while True:
        action_taken_this_round = False
        
        for pos in betting_order:
            player = game.players[pos]
            
            if player.folded or player.all_in:
                continue
                
            if last_raiser_pos is not None:
                if pos in players_acted and pos != last_raiser_pos:
                    players_acted.discard(pos)
            
            if pos in players_acted:
                continue
            
            ui.clear_screen()
            game_state = game.get_game_state()
            ui.display_persistent_game_state(
                game_state['players'], round_name, game_state['community_cards'],
                game_state['pot'], game_state['current_bet'], game_state['dealer_pos'],
                game_state['side_pots'], game_state['main_pot']
            )
            
            ui.display_player_action_table(player)
            
            # Get enhanced player decision state
            player_game_state = game.get_player_game_state(player)
            
            action, amount = player.decide_action(player_game_state)
            
            is_valid, error_msg = game.validate_action(player, action, amount)
            
            if not is_valid:
                ui.display_invalid_action_message(error_msg)
                ui.display_player_action_result(player.name, 'invalid_' + action, amount)
                ui.prompt_action_continue(player.name)
                continue
            
            result = game.execute_action(player, action, amount)
            
            # Notify all players about the action taken
            for bot_player in game.players:
                try:
                    bot_player.on_player_action(
                        result['player_name'], 
                        result['display_action'], 
                        result['display_amount']
                    )
                except Exception:
                    # Ignore callback errors to prevent bot crashes from affecting the game
                    pass
            
            stats.record_action(result['player_name'], result['display_action'], 
                              result['display_amount'], round_name)
            
            ui.display_player_action_result(
                result['player_name'], result['display_action'], result['display_amount']
            )
            
            players_acted.add(pos)
            action_taken_this_round = True
            
            if result['display_action'] in ['raise', 'raise_all_in']:
                last_raiser_pos = pos
                players_acted.clear()
                players_acted.add(pos)
            
            ui.prompt_action_continue(player.name)
            
            # Check if only one player remains active
            if len(game.get_active_players()) <= 1:
                return
        
        # If no actions were taken this iteration and all eligible players have acted, round is complete
        if not action_taken_this_round:
            break
        
        # Check if all remaining players have acted
        eligible_players = [pos for pos in betting_order if not game.players[pos].folded and not game.players[pos].all_in]
        if all(pos in players_acted for pos in eligible_players):
            break

def run_showdown(game: TexasHoldemGame, ui: TournamentUI, stats: TournamentStats):
    """
    Run the showdown phase with UI coordination and statistics tracking.
    
    Args:
        game: The game logic instance
        ui: The UI instance
        stats: Statistics tracker
    """
    ui.display_showdown_header(game.community_cards)
    
    active_players = game.get_active_players()
    
    if len(active_players) == 1:
        # Single winner (everyone else folded)
        winner = active_players[0]
        total_pot = game.pot
        winner.chips += total_pot
        ui.display_hand_winner(winner.name, total_pot, "Unopposed")
        stats.record_hand_winner(winner.name, total_pot)
        
        # Notify all players that the hand is complete
        for bot_player in game.players:
            try:
                bot_player.on_hand_complete(winner.name, total_pot, None)
            except Exception:
                # Ignore callback errors
                pass
        return
    
    # Evaluate hands for all active players
    scores = game.evaluate_hands()
    ui.display_showdown_results(active_players, scores, game.evaluator)
    
    # Record showdown statistics
    stats.record_showdown(scores, game.community_cards)
    
    # Handle side pot distribution
    side_pot_results = game.get_side_pot_winners(scores)
    
    # Distribute winnings and display results
    for pot_result in side_pot_results:
        pot_type = pot_result['pot_type']
        winners = pot_result['winners'] 
        prize_per_winner = pot_result['prize_per_winner']
        
        # Award chips to winners
        for winner in winners:
            winner.chips += prize_per_winner
        
        # Display pot result
        if len(winners) == 1:
            winner = winners[0]
            hand_description = game.get_winner_hand_description(winner, scores)
            ui.display_side_pot_winner(pot_type, winner.name, prize_per_winner, hand_description)
            stats.record_hand_winner(winner.name, prize_per_winner)
        else:
            # Multiple winners split the pot
            winner_names = [w.name for w in winners]
            ui.display_side_pot_split(pot_type, winner_names, prize_per_winner)
            for winner in winners:
                stats.record_hand_winner(winner.name, prize_per_winner)
    
    # Notify all players that the hand is complete
    # Get the primary winner and pot size for the callback
    main_pot_result = side_pot_results[0] if side_pot_results else None
    if main_pot_result and len(main_pot_result['winners']) > 0:
        primary_winner = main_pot_result['winners'][0]
        primary_pot_size = main_pot_result['prize_per_winner']
        
        # Get winning hand if available
        winning_hand = None
        for winner in main_pot_result['winners']:
            if hasattr(winner, 'hand') and winner.hand:
                winning_hand = winner.hand.copy()
                break
        
        # Notify all players
        for bot_player in game.players:
            try:
                bot_player.on_hand_complete(
                    primary_winner.name, 
                    primary_pot_size, 
                    winning_hand
                )
            except Exception:
                # Ignore callback errors
                pass

def main():
    # Initialize UI, statistics, and analyzer
    ui = TournamentUI()
    stats = TournamentStats()
    analyzer = TournamentAnalyzer(console)
    
    # Display welcome and tournament configuration
    ui.display_welcome()
    console.print(config.get_tournament_settings_summary())
    
    # Get all participant bots from player pool
    participant_bots = get_all_bots(starting_chips=config.STARTING_CHIPS)
    
    if not participant_bots:
        ui.display_player_count_error(0)
        return
    
    if len(participant_bots) < config.MIN_PLAYERS:
        ui.display_player_count_error(len(participant_bots))
        return
    
    if len(participant_bots) > config.MAX_PLAYERS:
        ui.display_player_count_error(len(participant_bots))
        participant_bots = participant_bots[:config.MAX_PLAYERS]
    
    players = participant_bots
    
    # Display tournament information
    ui.display_tournament_participants(players)
    
    # Show bot summary from player pool
    summary = get_bot_summary()
    ui.display_player_pool_summary(summary)
    
    # Display tournament rules
    initial_small_blind, initial_big_blind = config.get_blinds_for_hand(1)
    ui.display_tournament_rules(initial_small_blind, initial_big_blind)
    
    # Create tournament game
    game = TexasHoldemGame(players, small_blind=initial_small_blind, big_blind=initial_big_blind)
    
    # Initialize tournament statistics
    stats.remaining_players = len(players)
    
    hand_number = 1
    
    try:
        while len(game.players) > 1:
            # Update blinds for current hand
            current_small_blind, current_big_blind = config.get_blinds_for_hand(hand_number)
            game.update_blinds(current_small_blind, current_big_blind)
            
            ui.display_hand_header(hand_number, current_small_blind, current_big_blind)
            ui.display_remaining_players(game.players, current_big_blind)
            
            ui.prompt_start_hand()
            
            # Start hand and check if game can continue
            if not game.start_hand():
                break
            
            # Initialize hand statistics
            stats.start_hand(game.players)
            
            # Clear screen and show initial game state
            ui.clear_screen()
            game_state = game.get_game_state()
            ui.display_persistent_game_state(
                game_state['players'], "Pre-flop", game_state['community_cards'],
                game_state['pot'], game_state['current_bet'], game_state['dealer_pos'],
                game_state['side_pots'], game_state['main_pot']
            )
            
            # Pre-flop betting
            run_betting_round(game, ui, "Pre-flop", stats)
            
            # Track players who saw each round
            for player in game.get_active_players():
                stats.record_round_progression(player.name, "Pre-flop")
            
            # Flop
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(3)
                game.reset_bets_for_new_round()
                
                # Notify all players about flop cards
                for bot_player in game.players:
                    try:
                        bot_player.on_community_cards_dealt(game.community_cards.copy(), "flop")
                    except Exception:
                        # Ignore callback errors
                        pass
                
                # Track flop progression
                for player in game.get_active_players():
                    stats.record_round_progression(player.name, "Flop")
                
                run_betting_round(game, ui, "Flop", stats)
            
            # Turn
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(1)
                game.reset_bets_for_new_round()
                
                # Notify all players about turn card
                for bot_player in game.players:
                    try:
                        bot_player.on_community_cards_dealt(game.community_cards.copy(), "turn")
                    except Exception:
                        # Ignore callback errors
                        pass
                
                # Track turn progression
                for player in game.get_active_players():
                    stats.record_round_progression(player.name, "Turn")
                
                run_betting_round(game, ui, "Turn", stats)
            
            # River
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(1)
                game.reset_bets_for_new_round()
                
                # Notify all players about river card
                for bot_player in game.players:
                    try:
                        bot_player.on_community_cards_dealt(game.community_cards.copy(), "river")
                    except Exception:
                        # Ignore callback errors
                        pass
                
                # Track river progression
                for player in game.get_active_players():
                    stats.record_round_progression(player.name, "River")
                
                run_betting_round(game, ui, "River", stats)
            
            # Showdown
            if len(game.get_active_players()) > 0:
                run_showdown(game, ui, stats)
            
            # Complete hand statistics
            stats.complete_hand()            # Remove bankrupt players and check for eliminations
            eliminated = game.remove_bankrupt_players()
            for eliminated_player in eliminated:
                stats.record_player_elimination(eliminated_player.name)
                ui.display_elimination(eliminated_player.name, eliminated_player.chips)
                ui.prompt_elimination_continue(eliminated_player.name)
            
            # Check if game should continue
            if len(game.players) <= 1:
                if len(game.players) == 1:
                    winner = game.players[0]
                    ui.display_tournament_winner(winner.name, winner.chips)
                else:
                    ui.display_all_eliminated()
                break
            
            # Advance dealer button
            game.advance_dealer_button()
            hand_number += 1
            
            # Ask if user wants to continue
            continue_response = ui.prompt_continue_tournament()
            if continue_response.lower() == 'q':
                break
                
    except KeyboardInterrupt:
        ui.display_tournament_interrupted()
    
    # Finalize tournament statistics
    stats.finalize_tournament(game.players)
    
    # Display comprehensive analysis (no podium - final results are at the end)
    analyzer.display_comprehensive_analysis(stats, game.players)
    
    # Show final standings (simplified version after detailed analysis)
    # ui.display_final_standings(game.players)
    ui.display_thanks()

if __name__ == "__main__":
    main()