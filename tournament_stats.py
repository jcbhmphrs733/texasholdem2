# Tournament Statistics and Analysis System
"""
Comprehensive tournament statistics tracking and post-game analysis.

This module tracks detailed player statistics throughout the tournament and
generates insightful analysis reports including hand strength analysis,
betting patterns, and interesting tournament facts.
"""

from typing import Dict, List, Any, Optional, Tuple
from treys import Card, Evaluator
from collections import defaultdict
import statistics

class TournamentStats:
    """
    Tracks comprehensive tournament statistics for post-game analysis.
    """
    
    def __init__(self):
        """Initialize the tournament statistics tracker."""
        self.evaluator = Evaluator()
        
        # Player statistics
        self.player_stats = defaultdict(lambda: {
            'hands_played': 0,
            'hands_won': 0,
            'total_winnings': 0,
            'total_invested': 0,
            'strongest_hand': None,
            'strongest_hand_score': 7462,  # Worst possible score in treys
            'strongest_hand_description': 'None',
            'fold_count': 0,
            'call_count': 0,
            'raise_count': 0,
            'check_count': 0,
            'total_raise_amount': 0,
            'all_in_count': 0,
            'pre_flop_folds': 0,
            'post_flop_folds': 0,
            'bluff_attempts': 0,
            'hands_seen_flop': 0,
            'hands_seen_turn': 0,
            'hands_seen_river': 0,
            'hands_seen_showdown': 0,
            'biggest_pot_won': 0,
            'final_position': 0,
            'starting_chips': 0,
            'ending_chips': 0
        })
        
        # Tournament-wide statistics
        self.tournament_stats = {
            'total_hands': 0,
            'total_pot_size': 0,
            'biggest_pot': 0,
            'biggest_pot_winner': '',
            'longest_hand': 0,
            'most_aggressive_player': '',
            'most_conservative_player': '',
            'luckiest_win': None,
            'best_hand_seen': None,
            'total_all_ins': 0,
            'pre_flop_fold_rate': 0.0,
            'average_pot_size': 0.0
        }
        
        # Elimination tracking
        self.elimination_order = []  # Track order of elimination
        self.remaining_players = 0   # Track how many players are left
        
        # Hand tracking
        self.current_hand_actions = defaultdict(list)
        self.current_hand_investments = defaultdict(int)
        self.current_hand_participants = set()
        self.hand_history = []
        
    def start_hand(self, players: List[Any]):
        """Initialize tracking for a new hand."""
        self.tournament_stats['total_hands'] += 1
        self.current_hand_actions.clear()
        self.current_hand_investments.clear()
        self.current_hand_participants = {player.name for player in players}
        
        # Track starting chips for new players
        for player in players:
            if self.player_stats[player.name]['starting_chips'] == 0:
                self.player_stats[player.name]['starting_chips'] = player.chips
    
    def record_action(self, player_name: str, action: str, amount: int, 
                     round_name: str = 'Unknown'):
        """Record a player action."""
        self.current_hand_actions[player_name].append({
            'action': action,
            'amount': amount,
            'round': round_name
        })
        
        stats = self.player_stats[player_name]
        
        if action == 'fold':
            stats['fold_count'] += 1
            if round_name == 'Pre-flop':
                stats['pre_flop_folds'] += 1
            else:
                stats['post_flop_folds'] += 1
        elif action == 'call' or action == 'call_all_in':
            stats['call_count'] += 1
            self.current_hand_investments[player_name] += amount
            if action == 'call_all_in':
                stats['all_in_count'] += 1
        elif action == 'raise' or action == 'raise_all_in':
            stats['raise_count'] += 1
            stats['total_raise_amount'] += amount
            self.current_hand_investments[player_name] += amount
            if action == 'raise_all_in':
                stats['all_in_count'] += 1
        elif action == 'check':
            stats['check_count'] += 1
    
    def record_round_progression(self, player_name: str, round_name: str):
        """Record that a player saw a particular round."""
        stats = self.player_stats[player_name]
        
        if round_name == 'Flop':
            stats['hands_seen_flop'] += 1
        elif round_name == 'Turn':
            stats['hands_seen_turn'] += 1
        elif round_name == 'River':
            stats['hands_seen_river'] += 1
    
    def record_showdown(self, players_and_scores: List[Tuple[Any, int]], 
                       community_cards: List[int]):
        """Record showdown results and hand strengths."""
        for player, score in players_and_scores:
            stats = self.player_stats[player.name]
            stats['hands_seen_showdown'] += 1
            
            # Check if this is the strongest hand they've had
            if score < stats['strongest_hand_score']:  # Lower score = better hand in treys
                stats['strongest_hand_score'] = score
                stats['strongest_hand'] = player.hand.copy()
                stats['strongest_hand_description'] = self.evaluator.class_to_string(
                    self.evaluator.get_rank_class(score)
                )
            
            # Track tournament's best hand
            if (self.tournament_stats['best_hand_seen'] is None or 
                score < self.tournament_stats['best_hand_seen'][1]):
                self.tournament_stats['best_hand_seen'] = (player.name, score, 
                                                         player.hand.copy(), 
                                                         community_cards.copy())
    
    def record_hand_winner(self, winner_name: str, pot_size: int):
        """Record the winner of a hand."""
        stats = self.player_stats[winner_name]
        stats['hands_won'] += 1
        stats['total_winnings'] += pot_size
        
        if pot_size > stats['biggest_pot_won']:
            stats['biggest_pot_won'] = pot_size
            
        if pot_size > self.tournament_stats['biggest_pot']:
            self.tournament_stats['biggest_pot'] = pot_size
            self.tournament_stats['biggest_pot_winner'] = winner_name
        
        self.tournament_stats['total_pot_size'] += pot_size
    
    def complete_hand(self):
        """Complete hand tracking and update statistics."""
        # Update investment tracking
        for player_name, investment in self.current_hand_investments.items():
            self.player_stats[player_name]['total_invested'] += investment
        
        # Track hands played for all participants
        for player_name in self.current_hand_participants:
            self.player_stats[player_name]['hands_played'] += 1
    
    def record_player_elimination(self, player_name: str):
        """Record when a player is eliminated from the tournament."""
        self.elimination_order.append(player_name)
        # Set their final position (higher position number = eliminated earlier)
        # Total players - current elimination position gives us placement
        stats = self.player_stats[player_name]
        stats['final_position'] = len(self.player_stats) - len(self.elimination_order) + 1
        stats['ending_chips'] = 0

    def finalize_tournament(self, final_players: List[Any]):
        """Finalize tournament statistics."""
        # Set final positions and ending chips for remaining players
        sorted_players = sorted(final_players, key=lambda p: p.chips, reverse=True)
        for i, player in enumerate(sorted_players, 1):
            stats = self.player_stats[player.name]
            stats['final_position'] = i
            stats['ending_chips'] = player.chips
        
        # Calculate tournament-wide statistics
        if self.tournament_stats['total_hands'] > 0:
            self.tournament_stats['average_pot_size'] = (
                self.tournament_stats['total_pot_size'] / self.tournament_stats['total_hands']
            )
        
        # Find most aggressive/conservative players
        self._calculate_player_tendencies()
    
    def _calculate_player_tendencies(self):
        """Calculate player aggression and conservative tendencies."""
        aggression_scores = {}
        
        for player_name, stats in self.player_stats.items():
            if stats['hands_played'] > 0:
                # Aggression score: (raises + calls) / total_actions - fold_rate
                total_actions = (stats['fold_count'] + stats['call_count'] + 
                               stats['raise_count'] + stats['check_count'])
                
                if total_actions > 0:
                    fold_rate = stats['fold_count'] / total_actions
                    aggression_rate = stats['raise_count'] / total_actions
                    aggression_scores[player_name] = aggression_rate - fold_rate * 0.5
        
        if aggression_scores:
            most_aggressive = max(aggression_scores.items(), key=lambda x: x[1])
            most_conservative = min(aggression_scores.items(), key=lambda x: x[1])
            
            self.tournament_stats['most_aggressive_player'] = most_aggressive[0]
            self.tournament_stats['most_conservative_player'] = most_conservative[0]
    
    def get_player_analysis(self, player_name: str) -> Dict[str, Any]:
        """Get comprehensive analysis for a specific player."""
        stats = self.player_stats[player_name]
        
        if stats['hands_played'] == 0:
            return {'error': 'No data available for this player'}
        
        total_actions = (stats['fold_count'] + stats['call_count'] + 
                        stats['raise_count'] + stats['check_count'])
        
        analysis = {
            'name': player_name,
            'final_position': stats['final_position'],
            'hands_played': stats['hands_played'],
            'hands_won': stats['hands_won'],
            'win_rate': stats['hands_won'] / stats['hands_played'] if stats['hands_played'] > 0 else 0,
            'total_winnings': stats['total_winnings'],
            'total_invested': stats['total_invested'],
            'net_profit': stats['total_winnings'] - stats['total_invested'],
            'roi': ((stats['total_winnings'] - stats['total_invested']) / stats['total_invested'] * 100) if stats['total_invested'] > 0 else 0,
            'strongest_hand': stats['strongest_hand_description'],
            'biggest_pot_won': stats['biggest_pot_won'],
            'starting_chips': stats['starting_chips'],
            'ending_chips': stats['ending_chips'],
            'chip_change': stats['ending_chips'] - stats['starting_chips'],
        }
        
        if total_actions > 0:
            analysis.update({
                'fold_frequency': stats['fold_count'] / total_actions,
                'aggression_frequency': stats['raise_count'] / total_actions,
                'call_frequency': stats['call_count'] / total_actions,
                'check_frequency': stats['check_count'] / total_actions,
                'pre_flop_fold_rate': stats['pre_flop_folds'] / stats['hands_played'] if stats['hands_played'] > 0 else 0,
                'post_flop_fold_rate': stats['post_flop_folds'] / (stats['hands_seen_flop'] or 1),
                'average_raise_amount': stats['total_raise_amount'] / stats['raise_count'] if stats['raise_count'] > 0 else 0,
                'showdown_frequency': stats['hands_seen_showdown'] / stats['hands_played'] if stats['hands_played'] > 0 else 0,
            })
        
        return analysis
    
    def get_all_player_names(self) -> List[str]:
        """Get names of all players who participated in the tournament."""
        return list(self.player_stats.keys())

    def get_tournament_summary(self) -> Dict[str, Any]:
        """Get overall tournament summary and interesting facts."""
        return {
            'total_hands_played': self.tournament_stats['total_hands'],
            'biggest_pot': self.tournament_stats['biggest_pot'],
            'biggest_pot_winner': self.tournament_stats['biggest_pot_winner'],
            'average_pot_size': round(self.tournament_stats['average_pot_size'], 2),
            'most_aggressive_player': self.tournament_stats['most_aggressive_player'],
            'most_conservative_player': self.tournament_stats['most_conservative_player'],
            'best_hand_seen': self._format_best_hand(),
            'total_players': len(self.player_stats),
        }
    
    def _format_best_hand(self) -> Dict[str, Any]:
        """Format the best hand seen in the tournament."""
        if self.tournament_stats['best_hand_seen'] is None:
            return {'description': 'No hands recorded'}
        
        player_name, score, hole_cards, community_cards = self.tournament_stats['best_hand_seen']
        hand_description = self.evaluator.class_to_string(self.evaluator.get_rank_class(score))
        
        return {
            'player': player_name,
            'description': hand_description,
            'hole_cards': [Card.int_to_str(card) for card in hole_cards],
            'community_cards': [Card.int_to_str(card) for card in community_cards],
            'score': score
        }