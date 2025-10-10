from ParentBot import ParentBot
from typing import Dict, Any, Tuple

class PassiveBot(ParentBot):
    """
    Test bot that always checks or calls (never raises, never folds).
    This will help us test that all betting rounds work properly.
    """

    def __init__(self, name: str = "TestPassive", chips: int = 1000):
        super().__init__(name, chips)
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Always check if possible, otherwise call.
        Never raise, never fold (for testing purposes).
        """
        
        # Can we check (no bet to call)?
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        if can_check:
            return ('check', 0)
        else:
            # Call if we have enough chips
            call_amount = game_state['current_bet'] - game_state['player_bet']
            if call_amount <= self.chips:
                return ('call', game_state['current_bet'])
            else:
                # All-in if we don't have enough
                return ('call', self.chips + game_state['player_bet'])