# Texas Hold'em Bot Hackathon Tournament
from rich.console import Console
from game_logic import TexasHoldemGame
from tournament_ui import TournamentUI

# Import participant bots from player pool
from player_pool import get_all_bots, get_bot_summary

# Import tournament configuration
import configure_tournament as config

# Import ParentBot for fallback bots
from ParentBot import ParentBot
import random
from typing import Dict, Any, Tuple

console = Console()

def run_betting_round(game: TexasHoldemGame, ui: TournamentUI, round_name: str):
    """
    Run a complete betting round with UI coordination.
    
    Args:
        game: The game logic instance
        ui: The UI instance
        round_name: Name of the betting round ('Pre-flop', 'Flop', etc.)
    """
    ui.display_betting_round_header(round_name)
    
    # Clear screen for clean betting round display
    if round_name != "Pre-flop":
        ui.clear_screen()
        game_state = game.get_game_state()
        ui.display_persistent_game_state(
            game_state['players'], round_name, game_state['community_cards'],
            game_state['pot'], game_state['current_bet'], game_state['dealer_pos']
        )
    
    # Get betting order
    betting_order = game.get_betting_order(round_name)
    last_raiser_pos = None
    players_to_act = [pos for pos in betting_order if not game.players[pos].folded and not game.players[pos].all_in]
    
    # Track who has acted this round
    players_acted = set()
    
    while True:
        action_taken_this_round = False
        
        for pos in betting_order:
            player = game.players[pos]
            
            # Skip players who folded, are all-in, or have already acted unless there was a raise
            if player.folded or player.all_in:
                continue
                
            # If there was a raise, everyone needs to act again (except the raiser)
            if last_raiser_pos is not None:
                if pos in players_acted and pos != last_raiser_pos:
                    players_acted.discard(pos)  # Remove so they can act again
            
            # If player has already acted and no raise since, skip them
            if pos in players_acted:
                continue
            
            # Clear screen and show updated game state
            ui.clear_screen()
            game_state = game.get_game_state()
            ui.display_persistent_game_state(
                game_state['players'], round_name, game_state['community_cards'],
                game_state['pot'], game_state['current_bet'], game_state['dealer_pos']
            )
            
            # Show player's turn info
            ui.display_player_action_table(player)
            
            # Get player decision
            player_game_state = {
                'current_bet': game.current_bet,
                'min_raise': game.big_blind,
                'max_raise': player.chips + player.current_bet,
                'pot': game.pot,
                'community_cards': game.community_cards,
                'player_bet': player.current_bet
            }
            
            action, amount = player.decide_action(player_game_state)
            
            # Validate and execute action
            is_valid, error_msg = game.validate_action(player, action, amount)
            
            if not is_valid:
                ui.display_invalid_action_message(error_msg)
                ui.display_player_action_result(player.name, 'invalid_' + action, amount)
                ui.prompt_action_continue(player.name)
                continue
            
            # Execute the action
            result = game.execute_action(player, action, amount)
            
            # Display result
            ui.display_player_action_result(
                result['player_name'], result['display_action'], result['display_amount']
            )
            
            # Track that this player has acted
            players_acted.add(pos)
            action_taken_this_round = True
            
            # Track if this was a raise for betting round completion
            if result['display_action'] in ['raise', 'raise_all_in']:
                last_raiser_pos = pos
                players_acted.clear()  # Clear all previous actions since there was a raise
                players_acted.add(pos)  # Raiser has acted
            
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

def run_showdown(game: TexasHoldemGame, ui: TournamentUI):
    """
    Run the showdown phase with UI coordination.
    
    Args:
        game: The game logic instance
        ui: The UI instance
    """
    ui.display_showdown_header()
    
    active_players = game.get_active_players()
    
    if len(active_players) == 1:
        # Single winner (everyone else folded)
        winner = active_players[0]
        prize = game.distribute_pot([winner])
        ui.display_hand_winner(winner.name, prize, "Unopposed")
        return
    
    # Evaluate hands
    scores = game.evaluate_hands()
    ui.display_showdown_results(active_players, scores, game.evaluator)
    
    # Determine winners and distribute pot
    winners = game.determine_winners(scores)
    prize = game.distribute_pot(winners)
    
    # Display winners
    for winner in winners:
        hand_description = game.get_winner_hand_description(winner, scores)
        ui.display_hand_winner(winner.name, prize, hand_description)

def main():
    # Initialize UI
    ui = TournamentUI()
    
    # Display welcome and tournament configuration
    ui.display_welcome()
    console.print(config.get_tournament_settings_summary())
    
    # Get all participant bots from player pool
    participant_bots = get_all_bots(starting_chips=config.STARTING_CHIPS)
    
    if not participant_bots:
        ui.display_no_bots_error()
        return
    
    # Validate player count
    if len(participant_bots) < config.MIN_PLAYERS:
        ui.display_insufficient_players_error(len(participant_bots))
        return
    
    if len(participant_bots) > config.MAX_PLAYERS:
        ui.display_too_many_players_error(len(participant_bots))
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
            
            # Clear screen and show initial game state
            ui.clear_screen()
            game_state = game.get_game_state()
            ui.display_persistent_game_state(
                game_state['players'], "Pre-flop", game_state['community_cards'],
                game_state['pot'], game_state['current_bet'], game_state['dealer_pos']
            )
            
            # Pre-flop betting
            run_betting_round(game, ui, "Pre-flop")
            
            # Flop
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(3)
                game.reset_bets_for_new_round()
                run_betting_round(game, ui, "Flop")
            
            # Turn
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(1)
                game.reset_bets_for_new_round()
                run_betting_round(game, ui, "Turn")
            
            # River
            if len(game.get_active_players()) > 1:
                game.deal_community_cards(1)
                game.reset_bets_for_new_round()
                run_betting_round(game, ui, "River")
            
            # Showdown
            if len(game.get_active_players()) > 0:
                run_showdown(game, ui)
            
            # Remove bankrupt players and check for eliminations
            eliminated = game.remove_bankrupt_players()
            for eliminated_player in eliminated:
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
        
    # Show final standings
    ui.display_final_standings(game.players)
    ui.display_thanks()

if __name__ == "__main__":
    main()