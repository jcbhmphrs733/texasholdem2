# Test Bot for All-In Scenarios
from ParentBot import ParentBot
from typing import Dict, Any, Tuple

class AllInBot(ParentBot):
    """
    Test bot that goes all-in frequently to test side pot functionality.
    """
    
    def __init__(self, name: str = "AllInBot", chips: int = 1000):
        super().__init__(name, chips)  # Pass both name and chips correctly
        self.all_in_frequency = 0.7  # 70% chance to go all-in
    
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Simple all-in bot logic.
        """
        import random
        
        # Can we check?
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        # Randomly decide to go all-in
        if random.random() < self.all_in_frequency and self.chips > 0:
            # Try to go all-in
            all_in_amount = self.chips + game_state['player_bet']
            return ('raise', all_in_amount)
        
        # Otherwise, call if we can afford it, or fold
        if can_check:
            return ('check', 0)
        else:
            call_amount = game_state['current_bet'] - game_state['player_bet']
            if call_amount <= self.chips:
                return ('call', game_state['current_bet'])
            else:
                return ('fold', 0)