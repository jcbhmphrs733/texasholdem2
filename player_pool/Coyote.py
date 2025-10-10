from ParentBot import ParentBot
from typing import Dict, Any, Tuple
from treys import Card
import random

class Coyote(ParentBot):
    """
    Coyote bot - Well-rounded strategic player.
    
    Strategy: Balanced aggressive/conservative play based on hand strength and position.
    Exploits passive players and outplays random opponents through solid fundamentals.
    """

    def __init__(self, name: str = "Coyote", chips: int = 1000):
        super().__init__(name, chips)
        
        # Balanced bot parameters
        self.aggression_level = 0.6      # Moderate aggression
        self.bluff_frequency = 0.15      # Selective bluffing (15%)
        self.value_bet_threshold = 0.65  # Bet for value with 65%+ hands
        self.call_threshold = 0.4        # Call with 40%+ hands
        self.raise_threshold = 0.7       # Raise with 70%+ hands
        
        # Opponent tracking
        self.opponent_aggression = {}    # Track how aggressive opponents are
        self.opponent_fold_rate = {}     # Track how often opponents fold
        
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        Balanced strategy: Adapt to opponents while playing solid fundamentals.
        
        Strategy:
        - Play tight-aggressive with position awareness
        - Value bet strong hands, selectively bluff weak opponents
        - Exploit passive players by betting more often
        - Play tighter against aggressive opponents
        """
        
        # Get current game situation
        can_check = game_state['current_bet'] == game_state['player_bet']
        hand_strength = self.get_hand_strength()
        pot_odds = self.calculate_pot_odds(game_state)
        
        # Calculate call amount needed
        call_amount = game_state['current_bet'] - game_state['player_bet']
        
        # Adjust strategy based on community cards
        num_community_cards = len(game_state['community_cards'])
        
        # Pre-flop suited bonus: Never fold suited hands pre-flop
        is_preflop = num_community_cards == 0
        if is_preflop and len(self.hand) == 2:
            suits = [Card.get_suit_int(card) for card in self.hand]
            is_suited = suits[0] == suits[1]
            if is_suited:
                # Boost hand strength for any suited holding pre-flop
                hand_strength = max(hand_strength, 0.35)  # Minimum 35% for any suited hand
                
        # Position-aware thresholds
        position_factor = self._get_position_factor(game_state)
        adjusted_call_threshold = self.call_threshold - (position_factor * 0.1)
        adjusted_raise_threshold = self.raise_threshold - (position_factor * 0.1)
        
        # Opponent adjustment
        opponent_factor = self._assess_opponents(game_state)
        adjusted_call_threshold += opponent_factor * 0.15
        adjusted_raise_threshold += opponent_factor * 0.1
        
        # Decision logic: Balanced approach with pre-flop aggression
        
        # Pre-flop: Rarely fold, play most hands
        if is_preflop:
            # 1. Very weak hands (< 15%) - fold only the worst trash
            if hand_strength < 0.15:
                if can_check:
                    return ('check', 0)
                elif call_amount <= (self.chips * 0.03):  # Very small bet
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 2. Weak-playable hands (15-40%) - call or limp
            elif hand_strength < adjusted_call_threshold:
                if can_check:
                    return ('check', 0)
                elif call_amount <= (self.chips * 0.08) or pot_odds >= 2.5:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 3. Good hands (40-70%) - value play
            elif hand_strength < adjusted_raise_threshold:
                if can_check:
                    return ('check', 0)
                elif call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 4. Strong hands (70%+) - aggressive
            else:
                min_raise = game_state['current_bet'] + game_state['min_raise']
                max_affordable = self.chips + game_state['player_bet']
                
                if min_raise <= max_affordable:
                    bet_size = min_raise * (1.5 + hand_strength)
                    bet_size = min(bet_size, max_affordable)
                    return ('raise', int(bet_size))
                elif can_check:
                    return ('check', 0)
                elif call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
        
        # Decision logic: Balanced approach with pre-flop aggression
        
        # Pre-flop: Rarely fold, play most hands
        if is_preflop:
            # 1. Very weak hands (< 15%) - fold only the worst trash
            if hand_strength < 0.15:
                if can_check:
                    return ('check', 0)
                elif call_amount <= (self.chips * 0.03):  # Very small bet
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 2. Weak-playable hands (15-40%) - call or limp
            elif hand_strength < adjusted_call_threshold:
                if can_check:
                    return ('check', 0)
                elif call_amount <= (self.chips * 0.08) or pot_odds >= 2.5:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 3. Good hands (40-70%) - value play
            elif hand_strength < adjusted_raise_threshold:
                if can_check:
                    return ('check', 0)
                elif call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 4. Strong hands (70%+) - aggressive
            else:
                min_raise = game_state['current_bet'] + game_state['min_raise']
                max_affordable = self.chips + game_state['player_bet']
                
                if min_raise <= max_affordable:
                    bet_size = min_raise * (1.5 + hand_strength)
                    bet_size = min(bet_size, max_affordable)
                    return ('raise', int(bet_size))
                elif can_check:
                    return ('check', 0)
                elif call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
        
        # Post-flop: More conservative play
        else:
            # 1. Very weak hands (< 25%) - fold unless free
            if hand_strength < 0.25:
                if can_check:
                    return ('check', 0)
                else:
                    return ('fold', 0)
            
            # 2. Weak hands (25-40%) - selective play
            elif hand_strength < adjusted_call_threshold:
                if can_check:
                    # Sometimes bluff with weak hands in good position
                    if (random.random() < self.bluff_frequency * position_factor and 
                        num_community_cards >= 3 and position_factor > 0.3):
                        min_raise = game_state['current_bet'] + game_state['min_raise']
                        if min_raise <= self.chips + game_state['player_bet']:
                            return ('raise', min_raise)
                    return ('check', 0)
                elif call_amount <= (self.chips * 0.05) and pot_odds >= 3.0:
                    # Call very cheap with good pot odds
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
            
            # 3. Playable hands (40-70%) - value-oriented play
            elif hand_strength < adjusted_raise_threshold:
                if can_check:
                    # Bet for value if we have position and good hand
                    if (hand_strength >= 0.55 and position_factor > 0.2 and
                        random.random() < 0.7):
                        min_raise = game_state['current_bet'] + game_state['min_raise']
                        if min_raise <= self.chips + game_state['player_bet']:
                            # Size bet based on hand strength
                            bet_size = min_raise if hand_strength < 0.65 else min_raise * 1.5
                            bet_size = min(bet_size, self.chips + game_state['player_bet'])
                            return ('raise', int(bet_size))
                    return ('check', 0)
                elif call_amount <= self.chips:
                    # Call with decent hands if price is right
                    max_call_percent = 0.15 if hand_strength >= 0.5 else 0.1
                    if call_amount <= (self.chips * max_call_percent) or pot_odds >= 2.5:
                        return ('call', game_state['current_bet'])
                    else:
                        return ('fold', 0)
                else:
                    return ('fold', 0)
            
            # 4. Strong hands (70%+) - aggressive value betting
            else:
                min_raise = game_state['current_bet'] + game_state['min_raise']
                max_affordable = self.chips + game_state['player_bet']
                
                if min_raise <= max_affordable:
                    # Value bet sizing based on hand strength and opponents
                    if hand_strength >= 0.9:  # Premium hands
                        bet_size = min_raise * 2.5
                    elif hand_strength >= 0.8:  # Very strong
                        bet_size = min_raise * 2.0
                    else:  # Strong
                        bet_size = min_raise * 1.5
                    
                    # Reduce bet size against tight opponents, increase against loose
                    bet_size *= (1.0 - opponent_factor * 0.3)
                    bet_size = min(bet_size, max_affordable)
                    
                    return ('raise', int(bet_size))
                elif can_check:
                    return ('check', 0)
                elif call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
    
    
    def _get_position_factor(self, game_state: Dict[str, Any]) -> float:
        """
        Calculate position factor (0.0 = early position, 1.0 = late position).
        Later position allows for more aggressive play.
        """
        # Simple position calculation - in a full implementation, this would
        # track actual position relative to button
        active_players = len([p for p in game_state.get('players', []) if not getattr(p, 'folded', False)])
        if active_players <= 2:
            return 0.8  # Heads-up, position is very important
        elif active_players <= 4:
            return 0.6  # Good position in short-handed
        else:
            return 0.3  # Assume early-middle position in full table
    
    def _assess_opponents(self, game_state: Dict[str, Any]) -> float:
        """
        Assess opponent tendencies. Returns adjustment factor:
        -0.5 = very loose opponents (play more hands)
        0.0 = balanced opponents
        +0.5 = very tight opponents (play fewer hands)
        """
        # In a full implementation, this would track actual opponent stats
        # For now, make educated guesses based on known bot behaviors
        
        # Check for known passive players (like TestPassiveBot)
        players = game_state.get('players', [])
        passive_count = 0
        aggressive_count = 0
        
        for player in players:
            if hasattr(player, 'name'):
                name = player.name.lower()
                if 'passive' in name or 'test' in name:
                    passive_count += 1
                elif 'allin' in name or 'aggressive' in name:
                    aggressive_count += 1
        
        total_opponents = len(players) - 1  # Exclude ourselves
        if total_opponents == 0:
            return 0.0
        
        # More passive opponents = play more aggressively
        # More aggressive opponents = play more conservatively  
        net_factor = (passive_count - aggressive_count) / max(total_opponents, 1)
        return -net_factor * 0.4  # Scale the adjustment
    
    def get_hand_strength(self) -> float:
        """
        Improved hand evaluation with more balanced assessments.
        
        Returns: float between 0.0 (worst) and 1.0 (best)
        """
        if not self.hand:
            return 0.0
            
        # Get card ranks and suits
        ranks = [Card.get_rank_int(card) for card in self.hand]
        suits = [Card.get_suit_int(card) for card in self.hand]
        
        # Sort ranks for easier evaluation (low to high)
        sorted_ranks = sorted(ranks)
        
        # Pocket pairs
        if ranks[0] == ranks[1]:
            pair_rank = ranks[0]
            if pair_rank >= 12:  # AA, KK
                return 0.95
            elif pair_rank >= 10:  # QQ, JJ  
                return 0.88
            elif pair_rank >= 8:   # TT, 99, 88
                return 0.78
            elif pair_rank >= 6:   # 77, 66
                return 0.68
            elif pair_rank >= 4:   # 55, 44
                return 0.58
            else:                  # 33, 22
                return 0.48
        
        # Non-pair hands
        is_suited = suits[0] == suits[1]
        gap = abs(ranks[0] - ranks[1])
        high_card = max(ranks)
        low_card = min(ranks)
        
        # Premium non-pair hands
        if high_card == 14:  # Ace
            if low_card >= 12:  # AK, AQ  
                return 0.85 if is_suited else 0.78
            elif low_card >= 10:  # AJ, AT
                return 0.72 if is_suited else 0.65
            elif low_card >= 8:   # A9, A8
                return 0.62 if is_suited else 0.52
            elif low_card >= 6:   # A7, A6
                return 0.58 if is_suited else 0.42
            elif low_card >= 4:   # A5, A4 (wheel potential)
                return 0.52 if is_suited else 0.35
            else:                 # A3, A2
                return 0.46 if is_suited else 0.28
        
        # King-high hands
        elif high_card == 13:  # King
            if low_card >= 11:  # KQ
                return 0.75 if is_suited else 0.68
            elif low_card >= 10:  # KJ, KT
                return 0.65 if is_suited else 0.55
            elif low_card >= 8:   # K9, K8
                return 0.52 if is_suited else 0.38
            else:                # K7 and below
                return 0.48 if is_suited else 0.28
        
        # Queen-high hands
        elif high_card == 12:  # Queen
            if low_card >= 10:  # QJ, QT
                return 0.62 if is_suited else 0.52
            elif low_card >= 8:  # Q9, Q8
                return 0.48 if is_suited else 0.35
            else:               # Q7 and below
                return 0.42 if is_suited else 0.25
        
        # Jack-high and medium hands
        elif high_card >= 10:  # Jack, Ten
            if gap == 1:  # Connectors like JT, T9
                return 0.58 if is_suited else 0.45
            elif gap == 2 and is_suited:  # One-gap suited like J9s, T8s
                return 0.52
            elif is_suited:
                return 0.46  # Boost any suited Jack/Ten high hand
            elif gap <= 1 and low_card >= 8:  # High connectors
                return 0.38
            else:
                return 0.28
        
        # Lower hands - focus on suitedness and connectivity  
        else:
            if is_suited and gap <= 2 and high_card >= 7:  # Mid suited connectors
                return 0.48
            elif is_suited and gap <= 1:  # Any suited connector
                return 0.42
            elif gap == 1 and low_card >= 6:  # Higher connectors
                return 0.32
            elif is_suited:  # Any suited - boost significantly
                return 0.38  # Never let suited hands fall below playable threshold
            else:
                return 0.15  # Trash
    
    def on_hand_complete(self, winner: str, pot_size: int, winning_hand=None):
        """Track performance and adapt strategy."""
        super().on_hand_complete(winner, pot_size, winning_hand)
        
        # Adapt aggression based on performance
        if self.hands_played > 5:  # Need some data first
            win_rate = self.hands_won / self.hands_played
            
            if win_rate < 0.2:  # Losing too much, tighten up
                self.call_threshold = min(0.5, self.call_threshold + 0.05)
                self.raise_threshold = min(0.8, self.raise_threshold + 0.05)
            elif win_rate > 0.4:  # Winning a lot, can loosen up
                self.call_threshold = max(0.35, self.call_threshold - 0.03)
                self.raise_threshold = max(0.65, self.raise_threshold - 0.03)
    
    def on_player_action(self, player_name: str, action: str, amount: int):
        """Track opponent behavior for future exploitation."""
        super().on_player_action(player_name, action, amount)
        
        # Initialize tracking for new players
        if player_name not in self.opponent_aggression:
            self.opponent_aggression[player_name] = 0.5  # Neutral starting point
            self.opponent_fold_rate[player_name] = 0.3   # Assume moderate folding
        
        # Update aggression tracking
        if action == 'raise':
            self.opponent_aggression[player_name] = min(1.0, 
                self.opponent_aggression[player_name] + 0.1)
        elif action == 'fold':
            self.opponent_fold_rate[player_name] = min(1.0,
                self.opponent_fold_rate[player_name] + 0.05)
        elif action in ['call', 'check']:
            self.opponent_aggression[player_name] = max(0.0,
                self.opponent_aggression[player_name] - 0.02)


