from ParentBot import ParentBot
from typing import Dict, Any, Tuple
import random

class RandomBot(ParentBot):
    """
    Simple test bot for demonstrating the tournament configuration system.
    """
    
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """Simple random strategy for testing."""
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        # Random decision making
        choice = random.random()
        
        if choice < 0.3:  # 30% fold
            if can_check:
                return ('check', 0)
            else:
                return ('fold', 0)
        elif choice < 0.7:  # 40% call/check
            if can_check:
                return ('check', 0)
            else:
                call_amount = game_state['current_bet'] - game_state['player_bet']
                if call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
        else:  # 30% raise
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
            elif can_check:
                return ('check', 0)
            else:
                return ('call', game_state['current_bet'])