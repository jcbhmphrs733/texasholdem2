# DumbBot.py
from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card

class DumbBot(ParentBot):
    """
    Author: RippleTech
    """

    def __init__(self, name: str = "DumbBot"):
        super().__init__(name)
        self.current_game_state = None

    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Decide DumbBot's action based on hand strength.
        Uses default hand evaluation but applies deliberately bad decisions.
        Handles all cases safely to avoid invalid raises.
        """
        self.current_game_state = game_state
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength()

        # How much it costs to call
        to_call = game_state['current_bet'] - game_state['player_bet']

        # Strong hand: fold (dumb!)
        if hand_strength > 0.7:
            return ('fold', 0)

        # Medium hand: check if possible, otherwise call
        elif hand_strength > 0.4:
            return ('check', 0) if can_check else ('call', game_state['current_bet'])

        # Weak hand: attempt a "dumb raise" safely
        else:
            min_raise = game_state['current_bet'] + game_state['min_raise']
            max_affordable = self.chips + game_state['player_bet']

            # Case 1: Cannot even call → go all-in
            if self.chips <= to_call:
                return ('call', self.chips)

            # Case 2: Cannot meet minimum raise → just call
            if max_affordable < min_raise:
                return ('call', to_call)

            # Case 3: Can safely raise → perform dumb raise
            # Optionally, you could raise more, but must not exceed chips
            raise_amount = min_raise
            return ('raise', raise_amount)



    def get_hand_strength(self) -> float:
        if not self.hand:
            return 0.0
            
        community_cards = []
        if self.current_game_state:
            community_cards = self.current_game_state.get('community_cards', [])
        
        # Pre-flop evaluation
        if len(community_cards) == 0:
            ranks = [Card.get_rank_int(card) for card in self.hand]
            if ranks[0] == ranks[1]:
                return 0.7
            elif max(ranks) >= 10:
                return 0.5
            else:
                return 0.3
        
        all_cards = self.hand + community_cards
        ranks = [Card.get_rank_int(card) for card in all_cards]
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        max_count = max(rank_counts.values()) if rank_counts else 1
        if max_count >= 3:
            return 0.8
        elif max_count >= 2:
            return 0.6
        else:
            return 0.3
