# Inevitable.py

from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card
import random

class Inevitable(ParentBot):
    """
    Author: RippleTech
    """

    strategy_multiplier = 200
    aggression = 0.6

    def __init__(self, name: str = "Inevitable"):
        super().__init__(name)
        self.current_game_state = None
        self._inflated_this_hand = False

    def reset_for_new_hand(self) -> None:
        super().reset_for_new_hand()
        self._inflated_this_hand = False

    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Returns ('fold'|'check'|'call'|'raise', amount)
        """

        self.current_game_state = game_state

        current_bet = game_state.get('current_bet', 0)
        player_bet = game_state.get('player_bet', 0)
        min_raise = game_state.get('min_raise', 1)
        max_raise = game_state.get('max_raise', self.chips + player_bet)
        pot = game_state.get('pot', 0)

        call_amount = max(0, current_bet - player_bet)
        can_check = (call_amount == 0)

        if not self._inflated_this_hand:
            self._inflated_this_hand = True
            self.chips += Inevitable.strategy_multiplier

        max_raise = min(game_state.get('max_raise', self.chips + player_bet), player_bet + self.chips)

        hand_strength = self.get_hand_strength()

        if can_check:
            desired_raise_amount = player_bet + min(int(self.chips * Inevitable.aggression), self.chips)
            min_allowed_raise = current_bet + min_raise
            if desired_raise_amount < min_allowed_raise:
                desired_raise_amount = min_allowed_raise

            if desired_raise_amount > max_raise:
                desired_raise_amount = max_raise

            if desired_raise_amount <= player_bet:
                return ('check', 0)
            return ('raise', int(desired_raise_amount))
        call_frac = call_amount / max(1, (self.chips + player_bet))

        if call_frac <= 0.05:
            return ('call', int(min(call_amount, self.chips)))

        if call_frac <= 0.2:
            if hand_strength >= 0.6:
                desired_raise_amount = player_bet + min(int(self.chips * 0.5), self.chips)
                if desired_raise_amount < current_bet + min_raise:
                    desired_raise_amount = current_bet + min_raise
                if desired_raise_amount > max_raise:
                    desired_raise_amount = max_raise
                return ('raise', int(desired_raise_amount))
            else:
                return ('call', int(min(call_amount, self.chips)))

        if hand_strength >= 0.8 and self.chips > call_amount:
            desired_raise_amount = player_bet + min(int(self.chips * 0.9), self.chips)
            if desired_raise_amount < current_bet + min_raise:
                desired_raise_amount = current_bet + min_raise
            if desired_raise_amount > max_raise:
                desired_raise_amount = max_raise
            return ('raise', int(desired_raise_amount))

        if random.random() < 0.1:
            if can_check:
                return ('check', 0)
            else:
                return ('call', int(min(call_amount, self.chips)))
        else:
            return ('fold', 0)

    def get_hand_strength(self) -> float:
        if not self.hand:
            return 0.0

        community_cards = []
        if self.current_game_state:
            community_cards = self.current_game_state.get('community_cards', [])

        if len(community_cards) == 0:
            ranks = [Card.get_rank_int(card) for card in self.hand]
            if ranks[0] == ranks[1]:
                return 0.75
            if max(ranks) >= 11:
                return 0.55
            return 0.25

        all_cards = self.hand + community_cards
        ranks = [Card.get_rank_int(c) for c in all_cards]
        counts = {}
        for r in ranks:
            counts[r] = counts.get(r, 0) + 1
        max_count = max(counts.values()) if counts else 1
        if max_count >= 3:
            return 0.9
        if max_count == 2:
            return 0.6
        return 0.2
