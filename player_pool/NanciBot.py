"""
Test bot to verify enhanced game state and callback functionality.
This bot demonstrates the new opponent information and action history features.
"""

from ParentBot import ParentBot
from typing import Dict, List, Tuple, Any
from treys import Card

class NanciBot(ParentBot):
    """Test bot that uses enhanced game state features for opponent analysis."""
    
    def __init__(self, name: str = "NanciBot", chips: int = 1000):
        super().__init__(name, chips)
        # Track opponent behavior
        self.opponent_actions = {}  # player_name -> list of actions
        self.opponent_aggression = {}  # player_name -> aggression count
        self.board_analysis = []  # Track board development
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """Decision making using enhanced game state information."""
        
        # Check if we have enhanced features
        has_opponents = 'opponents' in game_state
        has_position = 'your_position' in game_state
        has_history = 'hand_actions' in game_state
        
        # Simple decision logic
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength()
        
        # Use enhanced info if available
        if has_opponents and has_position:
            # Count active opponents
            active_opponents = sum(1 for opp in game_state['opponents'] if opp['active'])
            
            # Adjust strategy based on position and opponents
            if game_state['your_position'] == game_state['dealer_position']:
                # Play more aggressively in dealer position
                threshold = 0.4
            else:
                threshold = 0.6
        else:
            threshold = 0.5
        
        if hand_strength < threshold:
            if can_check:
                return ('check', 0)
            else:
                return ('fold', 0)
        else:
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
            elif can_check:
                return ('check', 0)
            else:
                call_amount = game_state['current_bet'] - game_state['player_bet']
                if call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
    
    def on_player_action(self, player_name: str, action: str, amount: int) -> None:
        """Track opponent actions for behavioral analysis."""
        if player_name != self.name:
            # Track opponent actions
            if player_name not in self.opponent_actions:
                self.opponent_actions[player_name] = []
                self.opponent_aggression[player_name] = 0
            
            self.opponent_actions[player_name].append({
                'action': action,
                'amount': amount
            })
            
            # Track aggression
            if action in ['raise', 'raise_all_in']:
                self.opponent_aggression[player_name] += 1
    
    def on_community_cards_dealt(self, cards: List[int], stage: str) -> None:
        """Analyze board texture and development."""
        card_strings = [Card.int_to_str(card) for card in cards]
        board_analysis = {
            'stage': stage,
            'cards': card_strings,
            'num_cards': len(cards)
        }
        self.board_analysis.append(board_analysis)
    
    def on_hand_complete(self, winner: str, pot_size: int, winning_hand=None) -> None:
        """Learn from hand results."""
        super().on_hand_complete(winner, pot_size, winning_hand)
        
        # Reset action tracking for next hand
        self.opponent_actions.clear()
        for player in self.opponent_aggression:
            self.opponent_aggression[player] = max(0, self.opponent_aggression[player] - 1)