from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card, Evaluator
import random

class Coyote(ParentBot):
    """
    Coyote bot - Lean well-rounded player with proper community card evaluation.
    Author(s): Jacob Humphreys
    Created: October 2025
    """

    def __init__(self, name: str = "Coyote"):
        super().__init__(name)
        self.evaluator = Evaluator()  # For proper hand evaluation with community cards
        self.call_threshold = 0.4        # Call with 40%+ hands
        self.raise_threshold = 0.7       # Raise with 70%+ hands
        self.current_game_state = None   # Store game state for hand evaluation
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        
        # Store the game state for get_hand_strength() calls
        self.current_game_state = game_state
        
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength_with_board(game_state)
        call_amount = game_state['current_bet'] - game_state['player_bet']
        is_preflop = len(game_state['community_cards']) == 0
        
        # Suited bonus pre-flop
        if is_preflop and len(self.hand) == 2:
            suits = [Card.get_suit_int(card) for card in self.hand]
            if suits[0] == suits[1]:
                hand_strength = max(hand_strength, 0.35)
        
        # Position factor (better position = more aggressive)
        active_players = len([p for p in game_state.get('players', []) if not getattr(p, 'folded', False)])
        position_factor = 0.8 if active_players <= 2 else 0.6 if active_players <= 4 else 0.3
        
        # Adjust thresholds
        call_thresh = self.call_threshold - position_factor * 0.1
        raise_thresh = self.raise_threshold - position_factor * 0.1
        
        # Pre-flop: aggressive play
        if is_preflop:
            if hand_strength < 0.15:  # Trash
                return ('check', 0) if can_check else ('fold', 0) if call_amount > self.chips * 0.03 else ('call', game_state['current_bet'])
            elif hand_strength < call_thresh:  # Weak
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips * 0.08 else ('fold', 0)
            elif hand_strength < raise_thresh:  # Good
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips else ('fold', 0)
            else:  # great hole cards
                min_raise = game_state['current_bet'] + game_state['min_raise']
                if min_raise <= self.chips + game_state['player_bet']:
                    bet_size = min_raise * (1.5 + hand_strength)
                    return ('raise', int(min(bet_size, self.chips + game_state['player_bet'])))
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips else ('fold', 0)
        
        # Post-flop: conservative approach
        else:
            if hand_strength < 0.25:  # Very weak
                return ('check', 0) if can_check else ('fold', 0)
            elif hand_strength < call_thresh:  # Weak
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips * 0.05 else ('fold', 0)
            elif hand_strength < raise_thresh:  # Decent
                if can_check and hand_strength >= 0.55 and position_factor > 0.2:
                    min_raise = game_state['current_bet'] + game_state['min_raise']
                    if min_raise <= self.chips + game_state['player_bet']:
                        return ('raise', min_raise)
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips * 0.15 else ('fold', 0)
            else:  # Strong hand
                min_raise = game_state['current_bet'] + game_state['min_raise']
                if min_raise <= self.chips + game_state['player_bet']:
                    multiplier = 2.5 if hand_strength >= 0.9 else 2.0 if hand_strength >= 0.8 else 1.5
                    bet_size = min_raise * multiplier
                    return ('raise', int(min(bet_size, self.chips + game_state['player_bet'])))
                return ('check', 0) if can_check else ('call', game_state['current_bet']) if call_amount <= self.chips else ('fold', 0)
    
    def get_hand_strength(self) -> float:
        """
        Enhanced hand evaluation that uses community cards when available.
        This method is called by the dojo and tournament system.
        """
        # Use stored game state if available for proper evaluation
        if self.current_game_state is not None:
            return self.get_hand_strength_with_board(self.current_game_state)
        else:
            # Fallback to preflop evaluation when no game state available
            return self._evaluate_preflop_strength()
    
    def get_hand_strength_with_board(self, game_state: Dict[str, Any]) -> float:
        """
        PROPER hand evaluation that uses community cards.
        This is the key to good poker strategy!
        """
        if not self.hand:
            return 0.0
        
        community_cards = game_state.get('community_cards', [])
        
        # Pre-flop: evaluate hole cards only
        if len(community_cards) == 0:
            return self._evaluate_preflop_strength()
        
        # Post-flop: use actual hand evaluation with treys
        if len(community_cards) >= 3:
            try:
                # This is the critical line - evaluating with the actual board!
                score = self.evaluator.evaluate(self.hand, community_cards)
                
                # Convert treys score to realistic 0-1 range based on actual ranges
                if score <= 10:  # Royal flush, straight flush
                    return 0.99
                elif score <= 166:  # Four of a kind
                    return 0.95
                elif score <= 322:  # Full house
                    return 0.90
                elif score <= 1599:  # Flush
                    return 0.85
                elif score <= 1609:  # Straight
                    return 0.80
                elif score <= 2467:  # Three of a kind
                    return 0.75
                elif score <= 3325:  # Two pair
                    return 0.65
                elif score <= 6185:  # One pair
                    # Scale pairs from 0.3 to 0.6 based on strength
                    pair_strength = 1.0 - ((score - 3325) / (6185 - 3325))
                    return 0.3 + (pair_strength * 0.3)
                else:  # High card
                    # Scale high card from 0.1 to 0.25 based on how high
                    high_card_strength = 1.0 - ((score - 6185) / (7462 - 6185))
                    return 0.1 + (high_card_strength * 0.15)
                
            except Exception:
                # Fallback if evaluation fails
                return self._evaluate_preflop_strength()
        
        # If only 1-2 community cards (shouldn't happen in Hold'em, but safety)
        return self._evaluate_preflop_strength()
    
    def _evaluate_preflop_strength(self) -> float:
        """Pre-flop evaluation based on hole cards."""
        if not self.hand or len(self.hand) != 2:
            return 0.0
            
        ranks = [Card.get_rank_int(card) for card in self.hand]
        suits = [Card.get_suit_int(card) for card in self.hand]
        is_suited = suits[0] == suits[1]
        high, low = max(ranks), min(ranks)
        
        # Pocket pairs
        if ranks[0] == ranks[1]:
            return 0.6 + (high - 2) * 0.035  # 60% for 22, scaling to 95% for AA
        
        # Non-pairs: base strength from high card, bonuses for connectivity and suits
        base = 0.1 + (high - 2) * 0.03 + (low - 2) * 0.015
        gap_bonus = max(0, 0.1 - abs(high - low) * 0.02)
        suit_bonus = 0.15 if is_suited else 0
        
        return min(0.85, base + gap_bonus + suit_bonus)
