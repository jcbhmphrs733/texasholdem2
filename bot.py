# Texas Hold'em Bot Classes
import random

# Base Bot Class
class TexasHoldemBot:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
    
    def decide_action(self, game_state):
        # To be implemented by subclasses
        raise NotImplementedError("Subclasses must implement decide_action")
    
    def receive_cards(self, cards):
        self.hand = cards
    
    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False

# Example Bot Implementation
class AggressiveBot(TexasHoldemBot):
    """Aggressive bot that likes to raise and bluff"""
    def decide_action(self, game_state):
        # Determine if checking is legal (no bet to call)
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        if can_check:
            # Can check, but aggressive bots prefer to bet/raise
            actions = ['fold', 'check', 'call', 'raise']
            weights = [0.05, 0.1, 0.25, 0.6]  # Very aggressive - prefer raising
        else:
            # Must fold, call, or raise (cannot check)
            actions = ['fold', 'call', 'raise']
            weights = [0.1, 0.3, 0.6]  # Still very aggressive with raises
        
        action = random.choices(actions, weights=weights)[0]
        
        if action == 'raise':
            min_raise = game_state['current_bet'] + game_state['min_raise']
            max_raise = min(self.chips + game_state['player_bet'], game_state['current_bet'] * 4)
            if max_raise >= min_raise:
                raise_amount = random.randint(min_raise, max_raise)
                return (action, raise_amount)
            else:
                return ('call', 0)
        
        return (action, 0)