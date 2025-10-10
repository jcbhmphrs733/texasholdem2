# Participant Bot Template
# Copy this file and implement your own bot strategy!

from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card
import random

class MyBot(ParentBot):
    """
    Your custom bot implementation.
    
    Replace 'MyBot' with your bot's name and implement the decide_action method.
    You can also override other methods for advanced functionality.
    """
    
    def __init__(self, name: str, chips: int = 1000):
        """Initialize your bot with any custom setup."""
        super().__init__(name, chips)
        
        # Add any custom initialization here
        self.aggression_level = 0.5  # Example: track aggression
        self.bluff_frequency = 0.1   # Example: how often to bluff
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        IMPLEMENT THIS METHOD with your bot's decision logic.
        
        Available game_state keys:
        - 'current_bet': Current highest bet this round
        - 'min_raise': Minimum raise amount (usually big blind)
        - 'max_raise': Maximum you can bet (your chips + current_bet)
        - 'pot': Total chips in the pot
        - 'community_cards': Community cards dealt so far
        - 'player_bet': Your current bet this round
        
        Return: (action, amount) where action is 'fold', 'check', 'call', or 'raise'
        """
        
        # Example simple strategy - REPLACE WITH YOUR LOGIC!
        
        # Can we check (no bet to call)?
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        # Get our hand strength (you can implement better evaluation)
        hand_strength = self.get_hand_strength()
        
        # Simple random strategy - IMPROVE THIS!
        if random.random() < 0.3:  # 30% chance to fold
            if can_check:
                return ('check', 0)
            else:
                return ('fold', 0)
        elif random.random() < 0.7:  # 40% chance to call/check
            if can_check:
                return ('check', 0)
            else:
                call_amount = game_state['current_bet'] - game_state['player_bet']
                if call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
        else:  # 30% chance to raise
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
            elif can_check:
                return ('check', 0)
            else:
                return ('call', game_state['current_bet'])
    
    def get_hand_strength(self) -> float:
        """
        Override this method to implement better hand evaluation.
        
        Returns: float between 0.0 (worst) and 1.0 (best)
        """
        if not self.hand:
            return 0.0
            
        # Very basic evaluation - IMPROVE THIS!
        # Check for pairs
        ranks = [Card.get_rank_int(card) for card in self.hand]
        if ranks[0] == ranks[1]:
            return 0.8  # Pocket pair is strong
        
        # High cards
        high_card = max(ranks)
        if high_card >= 10:  # Jack or higher
            return 0.6
        elif high_card >= 7:
            return 0.4
        else:
            return 0.2
    
    def on_hand_complete(self, winner: str, pot_size: int, winning_hand=None):
        """Optional: Track your performance."""
        super().on_hand_complete(winner, pot_size, winning_hand)
        # Add any learning/tracking logic here
        
    def on_player_action(self, player_name: str, action: str, amount: int):
        """Optional: Track opponent behavior."""
        # Add opponent modeling logic here
        pass


