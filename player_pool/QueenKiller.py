# Participant Bot Template
# Copy this file and implement your own bot strategy!
#
from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card

class QueenKiller(ParentBot):
    """
    Your custom bot implementation.
    Replace 'YourBotNameGoesHere' with your bot's name.
    
    Author(s): Your Name(s) Here
    """
    def __init__(self, name: str = "queen-killer"):
        super().__init__(name)
        self.current_game_state = None  # Store for hand evaluation
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        IMPLEMENT THIS METHOD with your bot's decision logic.
        Return: (action, amount) where action is 'fold', 'check', 'call', or 'raise'
        """
        self.current_game_state = game_state
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength()
        
        # Example strategy - REPLACE WITH YOUR LOGIC!
        if hand_strength < 0.3:
            return ('check', 0) if can_check else ('fold', 0)
        elif hand_strength < 0.6:
            return ('check', 0) if can_check else ('call', game_state['current_bet'])
        else:
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
            else:
                return ('check', 0) if can_check else ('call', game_state['current_bet'])
    
    def get_hand_strength(self) -> float:
        """
        Implement your hand evaluation here - this is where creativity matters!
        Returns: float between 0.0 (worst) and 1.0 (best)
        """
        if not self.hand:
            return 0.0
            
        # Use stored game state for community cards
        community_cards = []
        if self.current_game_state:
            community_cards = self.current_game_state.get('community_cards', [])
        
        # Pre-flop: evaluate hole cards only
        if len(community_cards) == 0:
            ranks = [Card.get_rank_int(card) for card in self.hand]
            if ranks[0] == ranks[1]:  # Pocket pair
                return 0.7
            elif max(ranks) >= 10:  # High cards
                return 0.5
            else:
                return 0.3
        
        # Post-flop: YOUR CREATIVITY GOES HERE!
        # Combine your hole cards with community cards and evaluate the strength
        # Consider pairs, straights, flushes, draws, etc.
        
        # Basic example - improve this!
        all_cards = self.hand + community_cards
        ranks = [Card.get_rank_int(card) for card in all_cards]
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        max_count = max(rank_counts.values()) if rank_counts else 1
        if max_count >= 3:
            return 0.8  # Three of a kind or better
        elif max_count >= 2:
            return 0.6  # Pair
        else:
            return 0.3  # High card