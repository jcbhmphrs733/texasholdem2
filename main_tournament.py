# Texas Hold'em Bot Hackathon Tournament
from rich.console import Console
from game_logic import TexasHoldemGame
from setup.tournament_ui import TournamentUI
from setup.tournament_stats import TournamentStats
from setup.tournament_analysis import TournamentAnalyzer
from player_pool import get_all_bots, get_bot_summary
import setup.configure_tournament as config
from ParentBot import ParentBot
from PitBoss import PitBoss
import random
from typing import Dict, Any, Tuple

console = Console()

def check_and_remove_cheaters(game):
    """Remove players eliminated for cheating from the active game"""
    eliminated_players = []
    
    for i, player in enumerate(game.players):
        if (hasattr(player, 'is_eliminated_for_cheating') and 
            player.is_eliminated_for_cheating and 
            player.chips > 0):
            # Set chips to 0 to trigger natural elimination
            if hasattr(player, '_tournament_set_chips'):
                player._tournament_set_chips(0)
            eliminated_players.append(player.name)
    
    if eliminated_players:
        print(f"REMOVED cheaters from tournament: {', '.join(eliminated_players)}")

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
    # Check for and remove cheaters at the start of each betting round
    check_and_remove_cheaters(game)
    
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
    invalid_attempts = {}  # Track invalid attempts per player position
    max_invalid_attempts = 3
    
    while True:
        action_taken_this_round = False
        
        for pos in betting_order:
            player = game.players[pos]
            
            # Check if bot has been eliminated for cheating
            if hasattr(player, 'is_eliminated_for_cheating') and player.is_eliminated_for_cheating:
                # Set chips to 0 to trigger natural tournament elimination
                if player.chips > 0:
                    if hasattr(player, '_tournament_set_chips'):
                        player._tournament_set_chips(0)
                    print(f"ELIMINATED {player.name} from tournament (cheating)")
                continue
            
            if player.folded or player.all_in:
                continue
            
            # Skip players who have already acted, unless there was a raise after they acted
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
            
            # Validation loop for player action
            while True:
                action, amount = player.decide_action(player_game_state)
                
                is_valid, error_msg = game.validate_action(player, action, amount)
                
                if is_valid:
                    break  # Valid action, proceed with execution
                
                # Track invalid attempts to prevent infinite loops
                if pos not in invalid_attempts:
                    invalid_attempts[pos] = 0
                invalid_attempts[pos] += 1
                
                ui.display_invalid_action_message(error_msg)
                ui.display_player_action_result(player.name, 'invalid_' + action, amount)
                
                # Check for chip manipulation (cheating)
                if "CHIP MANIPULATION DETECTED" in error_msg:
                    print(f"\nPIT BOSS ALERT:")
                    print(f"Bot: {player.name}")
                    print(f"Violation: {error_msg}")
                    print(f"Action attempted: {action} with amount {amount}")
                    print(f"The house has corrected chips to: {player.chips}")
                    print(f"Bot will retry with legitimate chip count.\n")
                    
                    # Continue to let bot try again with corrected chips (but track attempts)
                    if invalid_attempts[pos] >= max_invalid_attempts:
                        print(f"WARNING: {player.name} has made {invalid_attempts[pos]} invalid attempts. Forcing fold to prevent infinite loop.")
                        action, amount = 'fold', 0
                        break
                    
                    ui.prompt_action_continue(player.name)
                    continue
                
                # Check for other serious rule violations
                elif "RULE VIOLATION" in error_msg:
                    print(f"\nSERIOUS RULE VIOLATION DETECTED:")
                    print(f"Bot: {player.name}")
                    print(f"Violation: {error_msg}")
                    print(f"Action attempted: {action} with amount {amount}")
                    print(f"Current chips: {player.chips}")
                    print(f"Forcing fold due to rule violation.\n")
                    
                    # Force fold for other serious violations
                    action, amount = 'fold', 0
                    break
                
                # Handle common invalid actions with auto-correction
                elif invalid_attempts[pos] >= max_invalid_attempts:
                    print(f"\nWARNING: {player.name} has made {invalid_attempts[pos]} invalid attempts.")
                    print(f"Auto-correcting to prevent infinite loop...")
                    
                    # Auto-correct invalid raise to all-in
                    if action == 'raise' and player.chips > 0:
                        action = 'raise'
                        amount = player.current_bet + player.chips
                        print(f"Auto-correcting invalid raise to ALL-IN: ${amount}")
                    
                    # Auto-correct invalid call to all-in or fold
                    elif action == 'call':
                        call_needed = game.current_bet - player.current_bet
                        if player.chips > 0 and player.chips < call_needed:
                            action = 'raise'
                            amount = player.current_bet + player.chips
                            print(f"Auto-correcting call to ALL-IN: ${amount}")
                        else:
                            action = 'fold'
                            amount = 0
                            print(f"Auto-correcting to FOLD")
                    
                    # Default fallback: force fold
                    else:
                        action = 'fold'
                        amount = 0
                        print(f"Auto-correcting to FOLD")
                    
                    print(f"Proceeding with corrected action: {action} ${amount}")
                    # The corrected action will be validated in the next iteration
                    invalid_attempts[pos] = 0  # Reset attempts after correction
                    break  # Re-validate the corrected action
                
                # Normal retry for first few attempts
                ui.prompt_action_continue(player.name)
                # Let the loop continue to get a new decision
            
            # Reset invalid attempts counter on successful action
            if pos in invalid_attempts:
                invalid_attempts[pos] = 0
            
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
                # When someone raises, clear the acted list except for the raiser
                players_acted.clear()
                players_acted.add(pos)
            
            ui.prompt_action_continue(player.name)
            
            # Check if only one player remains active
            if len(game.get_active_players()) <= 1:
                return
        
        # Check for betting round completion
        # Round is complete when:
        # 1. All bets are equal (from game logic), AND
        # 2. All eligible players have acted since the last raise
        eligible_players = [pos for pos in betting_order if not game.players[pos].folded and not game.players[pos].all_in]
        
        if (game.is_betting_round_complete(last_raiser_pos) and 
            all(pos in players_acted for pos in eligible_players)):
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
        if hasattr(winner, '_tournament_add_chips'):
            winner._tournament_add_chips(total_pot)
        else:
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
            if hasattr(winner, '_tournament_add_chips'):
                winner._tournament_add_chips(prize_per_winner)
            else:
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

def display_security_report(players):
    """Display comprehensive security report for all protected bots"""
    protected_bots = [p for p in players if hasattr(p, 'get_cheat_report')]
    
    if not protected_bots:
        return
    
    print("\n" + "=" * 60)
    print("PIT BOSS SECURITY REPORT")
    print("=" * 60)
    
    total_strikes = 0
    eliminated_count = 0
    
    for bot in protected_bots:
        report = bot.get_cheat_report()
        total_strikes += report['strikes']
        
        if report['strikes'] > 0:
            status = "ELIMINATED" if report['eliminated'] else "ACTIVE"
            print(f"TARGET {report['name']}: {report['strikes']}/{report['max_strikes']} strikes - {status}")
            
            if report['eliminated']:
                eliminated_count += 1
                print(f"   ELIMINATED for excessive cheating!")
            
            # Show strike details
            for strike in report['cheat_log'][-3:]:  # Show last 3 strikes
                print(f"   Strike {strike['strike']}: {strike['type']} - {strike['details'][:50]}...")
    
    if total_strikes == 0:
        print("CLEAN TOURNAMENT: No cheating attempts detected!")
    else:
        print(f"\nSECURITY SUMMARY:")
        print(f"   Total strikes issued: {total_strikes}")
        print(f"   Bots eliminated: {eliminated_count}")
        print(f"   PitBoss system: FULLY OPERATIONAL")
    
    print("=" * 60 + "\n")

def main():
    # Initialize UI, statistics, and analyzer
    ui = TournamentUI()
    stats = TournamentStats()
    analyzer = TournamentAnalyzer(console)
    
    # Display welcome and tournament configuration
    ui.display_welcome()
    console.print(config.get_tournament_settings_summary())
    
    # Get all participant bots from player pool
    raw_bots = get_all_bots(starting_chips=config.STARTING_CHIPS)
    
    if not raw_bots:
        ui.display_player_count_error(0)
        return
    
    if len(raw_bots) < config.MIN_PLAYERS:
        ui.display_player_count_error(len(raw_bots))
        return
    
    if len(raw_bots) > config.MAX_PLAYERS:
        ui.display_player_count_error(len(raw_bots))
        raw_bots = raw_bots[:config.MAX_PLAYERS]
    
    # Assign a pit boss to watch each bot and prevent cheating
    print("The Pit Boss is now watching all bots for cheating...")
    participant_bots = []
    for bot in raw_bots:
        protected_bot = PitBoss(bot, config.STARTING_CHIPS)
        participant_bots.append(protected_bot)
        print(f"   Pit Boss watching: {bot.name}")
    
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
    
    # Generate security report if CheaterBot participated
    display_security_report(game.players)
    
    # Show final standings (simplified version after detailed analysis)
    # ui.display_final_standings(game.players)
    ui.display_thanks()

if __name__ == "__main__":
    main()