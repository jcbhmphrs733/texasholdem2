from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card
import random

class Coyote(ParentBot):
    """
    Coyote bot - Plays very tight and safe.
    
    Strategy: Only plays premium hands, minimizes risk, preserves chips.
    """

    def __init__(self, name: str = "Coyote", chips: int = 1000):
        
        super().__init__(name, chips)
        
        # Conservative bot parameters
        self.aggression_level = 0.2  # Very low aggression
        self.bluff_frequency = 0.05  # Rarely bluff (5%)
        self.tight_threshold = 0.7   # Only play hands with 70%+ strength
        self.raise_threshold = 0.85  # Only raise with 85%+ strength
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Conservative bot strategy: Play tight, only bet with strong hands.
        
        Strategy:
        - Only play hands with strength > 70%
        - Only raise with very strong hands (85%+)
        - Fold weak hands even if checking is free
        - Minimize risk and preserve chips
        """
        
        # Get current game situation
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength()
        pot_odds = self.calculate_pot_odds(game_state)
        
        # Calculate call amount needed
        call_amount = game_state['current_bet'] - game_state['player_bet']
        
        # Conservative thresholds based on betting round
        num_community_cards = len(game_state['community_cards'])
        
        # Adjust thresholds based on position in hand
        if num_community_cards == 0:  # Pre-flop
            strength_threshold = 0.75  # Very tight pre-flop
            raise_threshold = 0.9
        elif num_community_cards == 3:  # Flop
            strength_threshold = 0.7   # Slightly looser after seeing flop
            raise_threshold = 0.85
        else:  # Turn/River
            strength_threshold = 0.65  # Can play more hands with full info
            raise_threshold = 0.8
        
        # Decision logic: Conservative approach
        
        # 1. Very weak hands - always fold (unless free check)
        if hand_strength < 0.3:
            if can_check:
                return ('check', 0)  # Free to see more cards
            else:
                return ('fold', 0)   # Not worth any chips
        
        # 2. Weak hands - only play if very cheap or free
        elif hand_strength < strength_threshold:
            if can_check:
                return ('check', 0)  # Free to see more cards
            elif call_amount <= (self.chips * 0.02):  # Only if very cheap (2% of stack)
                return ('call', game_state['current_bet'])
            else:
                return ('fold', 0)   # Too expensive for weak hand
        
        # 3. Decent hands - call or check, rarely raise
        elif hand_strength < raise_threshold:
            # Occasionally bluff-raise with decent hands (very rare)
            if (random.random() < self.bluff_frequency and 
                can_check and 
                num_community_cards >= 3):  # Only bluff post-flop
                min_raise = game_state['current_bet'] + game_state['min_raise']
                if min_raise <= self.chips + game_state['player_bet']:
                    return ('raise', min_raise)
            
            # Standard play: call or check
            if can_check:
                return ('check', 0)
            elif call_amount <= self.chips:
                # Conservative call - only if pot odds are decent
                if pot_odds >= 2.0 or call_amount <= (self.chips * 0.1):
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)  # Poor pot odds
            else:
                return ('fold', 0)  # Can't afford
        
        # 4. Strong hands - bet for value
        else:
            min_raise = game_state['current_bet'] + game_state['min_raise']
            max_affordable = self.chips + game_state['player_bet']
            
            # Conservative value betting
            if min_raise <= max_affordable:
                # Size bet conservatively (don't scare opponents away)
                conservative_raise = min_raise
                if hand_strength >= 0.95:  # Premium hands can bet bigger
                    conservative_raise = min(min_raise * 2, max_affordable)
                
                return ('raise', conservative_raise)
            elif can_check:
                return ('check', 0)  # Can't raise, but don't fold strong hand
            elif call_amount <= self.chips:
                return ('call', game_state['current_bet'])
            else:
                return ('fold', 0)  # Forced to fold (shouldn't happen often)
    
    def get_hand_strength(self) -> float:
        """
        Conservative hand evaluation - stricter requirements for strong hands.
        
        Returns: float between 0.0 (worst) and 1.0 (best)
        """
        if not self.hand:
            return 0.0
            
        # Get card ranks and suits
        ranks = [Card.get_rank_int(card) for card in self.hand]
        suits = [Card.get_suit_int(card) for card in self.hand]
        
        # Sort ranks for easier evaluation (low to high)
        sorted_ranks = sorted(ranks)
        
        # Pocket pairs - conservatives love them
        if ranks[0] == ranks[1]:
            pair_rank = ranks[0]
            if pair_rank >= 12:  # AA, KK
                return 0.95
            elif pair_rank >= 10:  # QQ, JJ  
                return 0.85
            elif pair_rank >= 8:   # TT, 99, 88
                return 0.75
            elif pair_rank >= 6:   # 77, 66
                return 0.65
            else:                  # 55 and below
                return 0.55
        
        # Suited connectors and suited hands
        is_suited = suits[0] == suits[1]
        is_connector = abs(ranks[0] - ranks[1]) == 1
        gap = abs(ranks[0] - ranks[1])
        
        # High cards (conservative prefers premium hands)
        high_card = max(ranks)
        low_card = min(ranks)
        
        # Ace-high hands
        if high_card == 14:  # Ace
            if low_card >= 12:  # AK, AQ
                return 0.8 if is_suited else 0.75
            elif low_card >= 10:  # AJ, AT
                return 0.7 if is_suited else 0.6
            elif low_card >= 8:   # A9, A8
                return 0.55 if is_suited else 0.4
            else:                 # A7 and below
                return 0.45 if is_suited else 0.3
        
        # King-high hands
        elif high_card == 13:  # King
            if low_card >= 11:  # KQ
                return 0.7 if is_suited else 0.65
            elif low_card >= 10:  # KJ, KT
                return 0.6 if is_suited else 0.5
            else:                # K9 and below
                return 0.4 if is_suited else 0.25
        
        # Queen-high hands
        elif high_card == 12:  # Queen
            if low_card >= 10:  # QJ, QT
                return 0.55 if is_suited else 0.45
            else:               # Q9 and below
                return 0.35 if is_suited else 0.2
        
        # Jack-high and below
        elif high_card >= 10:  # Jack
            if is_suited and is_connector:  # Suited connectors
                return 0.5
            elif is_suited:
                return 0.4
            elif is_connector and low_card >= 9:  # High connectors
                return 0.35
            else:
                return 0.25
        
        # Low hands
        else:
            if is_suited and gap <= 2:  # Low suited with small gap
                return 0.3
            elif is_connector:  # Low connectors
                return 0.25
            else:
                return 0.1  # Trash hands
        
        # Fallback
        return 0.1
    
    def on_hand_complete(self, winner: str, pot_size: int, winning_hand=None):
        """Track performance and adjust conservative play."""
        super().on_hand_complete(winner, pot_size, winning_hand)
        
        # Conservative bots learn from losses
        if winner != self.name and self.hands_played > 0:
            # If we're losing too much, become even more conservative
            win_rate = self.hands_won / self.hands_played
            if win_rate < 0.15:  # Winning less than 15% of hands
                self.tight_threshold = min(0.8, self.tight_threshold + 0.05)
                self.bluff_frequency = max(0.01, self.bluff_frequency - 0.01)
        
    def on_player_action(self, player_name: str, action: str, amount: int):
        """Track opponent behavior to play even more conservatively against aggressors."""
        # Conservative bots avoid aggressive players
        if action == 'raise' and player_name != self.name:
            # Note: In a full implementation, we'd track this per player
            # For now, just be more conservative when facing raises
            pass


