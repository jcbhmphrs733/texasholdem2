# Texas Hold'em Game Logic (Pure Game Mechanics)
"""
Texas Hold'em Game Engine - Pure Game Logic

This module contains only the core game mechanics and logic for Texas Hold'em poker.
All UI/display code has been moved to tournament_ui.py to keep this module clean
for participants to study and understand the game rules and mechanics.

Key Game Components:
- Hand dealing and card management
- Betting rounds and action validation
- Pot management and side pot calculations
- Hand evaluation and winner determination
- Player state management (chips, bets, all-in, folded)

This separation allows participants to focus on understanding the core poker
mechanics without UI clutter when developing their bots.
"""

from treys import Card, Evaluator, Deck
from typing import List, Dict, Any, Tuple, Optional

class TexasHoldemGame:
    """
    Pure Texas Hold'em game logic without any UI dependencies.
    
    This class handles all the core game mechanics:
    - Card dealing and deck management
    - Betting rounds and action validation
    - Pot calculation and distribution
    - Hand evaluation and winner determination
    - Player state management
    
    UI responsibilities are handled separately in tournament_ui.py
    """
    
    def __init__(self, players: List[Any], small_blind: int = 10, big_blind: int = 20):
        """
        Initialize a new Texas Hold'em game.
        
        Args:
            players: List of player objects (bots)
            small_blind: Small blind amount
            big_blind: Big blind amount
        """
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_pos = 0
        self.evaluator = Evaluator()
        self.hand_history = []
        
        # Side pot management
        self.side_pots = []  # List of (amount, eligible_players) tuples
        self.main_pot = 0
        
        # Game state for external access (UI, statistics, etc.)
        self.last_action = None
        self.betting_round_complete = False
        self.hand_complete = False
    
    def update_blinds(self, small_blind: int, big_blind: int):
        """Update blind amounts (for blind level increases)."""
        self.small_blind = small_blind
        self.big_blind = big_blind
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get current game state for external systems (UI, logging, etc.).
        
        Returns:
            Dict containing all relevant game state information
        """
        return {
            'players': self.players,
            'community_cards': self.community_cards,
            'pot': self.main_pot + sum(pot['amount'] for pot in self.side_pots),  # Total pot for display
            'current_bet': self.current_bet,
            'dealer_pos': self.dealer_pos,
            'small_blind': self.small_blind,
            'big_blind': self.big_blind,
            'hand_complete': self.hand_complete,
            'betting_round_complete': self.betting_round_complete,
            'side_pots': self.side_pots,
            'main_pot': self.main_pot
        }
    
    def _create_side_pots(self):
        """
        Create side pots when players are all-in with different amounts.
        
        This method should be called after betting is complete to properly
        distribute the pot among eligible players based on their investments.
        """
        # Get all players who contributed to the pot (not folded)
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) <= 1:
            self.main_pot = self.pot
            return
        
        # Clear existing side pots
        self.side_pots = []
        self.main_pot = 0
        
        # Get unique bet levels, sorted from lowest to highest
        bet_levels = sorted(set(p.current_bet for p in active_players))
        
        current_level = 0
        total_distributed = 0
        
        for bet_level in bet_levels:
            if bet_level > current_level:
                # Players who contributed at least this amount
                eligible_players = [p for p in active_players if p.current_bet >= bet_level]
                
                # Calculate pot size for this level
                pot_size = (bet_level - current_level) * len(eligible_players)
                total_distributed += pot_size
                
                if len(self.side_pots) == 0:
                    # This is the main pot (lowest level that everyone contributed to)
                    self.main_pot = pot_size
                else:
                    # This is a side pot
                    self.side_pots.append({
                        'amount': pot_size,
                        'eligible_players': eligible_players.copy(),
                        'level': bet_level
                    })
                
                current_level = bet_level
        
        # Ensure we've distributed the entire pot
        if total_distributed != self.pot:
            # Add any remaining amount to the main pot
            self.main_pot += (self.pot - total_distributed)
    
    def get_pot_info(self) -> Dict[str, Any]:
        """
        Get detailed pot information including side pots.
        
        Returns:
            Dict with pot information for display
        """
        total_pot = self.main_pot + sum(pot['amount'] for pot in self.side_pots)
        
        return {
            'total_pot': total_pot,
            'main_pot': self.main_pot,
            'side_pots': self.side_pots,
            'num_side_pots': len(self.side_pots)
        }
    
    def remove_bankrupt_players(self) -> List[Any]:
        """
        Remove players with 0 chips and return list of eliminated players.
        
        Returns:
            List of eliminated players
        """
        bankrupt_players = [player for player in self.players if player.chips <= 0]
        
        for player in bankrupt_players:
            self.players.remove(player)
        
        # Adjust dealer position if needed after eliminations
        if self.dealer_pos >= len(self.players) and len(self.players) > 0:
            self.dealer_pos = 0
        
        return bankrupt_players
    
    def can_start_hand(self) -> bool:
        """Check if a hand can be started (enough players)."""
        return len(self.players) > 1
    
    def start_hand(self) -> bool:
        """
        Start a new hand of Texas Hold'em.
        
        Returns:
            bool: True if hand started successfully, False if not enough players
        """
        # Remove bankrupt players first
        self.remove_bankrupt_players()
        
        if not self.can_start_hand():
            return False
        
        # Reset game state
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.hand_complete = False
        self.betting_round_complete = False
        
        # Reset side pot management
        self.side_pots = []
        self.main_pot = 0
        
        # Reset all players for new hand
        for player in self.players:
            player.reset_for_new_hand()
        
        # Post blinds
        self._post_blinds()
        
        # Deal hole cards
        self._deal_hole_cards()
        
        return True
    
    def _post_blinds(self):
        """Post small and big blinds."""
        if len(self.players) < 2:
            return
        
        sb_pos = (self.dealer_pos + 1) % len(self.players)
        bb_pos = (self.dealer_pos + 2) % len(self.players)
        
        # Small blind
        sb_amount = min(self.small_blind, self.players[sb_pos].chips)
        self.players[sb_pos].chips -= sb_amount
        self.players[sb_pos].current_bet = sb_amount
        
        # Big blind
        bb_amount = min(self.big_blind, self.players[bb_pos].chips)
        self.players[bb_pos].chips -= bb_amount
        self.players[bb_pos].current_bet = bb_amount
        
        self.pot = sb_amount + bb_amount
        self.current_bet = max(sb_amount, bb_amount)
    
    def _deal_hole_cards(self):
        """Deal two hole cards to each player."""
        for player in self.players:
            card1 = self.deck.draw(1)[0]
            card2 = self.deck.draw(1)[0]
            player.receive_cards([card1, card2])
    
    def get_active_players(self) -> List[Any]:
        """Get players who haven't folded."""
        return [p for p in self.players if not p.folded]
    
    def get_betting_players(self) -> List[Any]:
        """Get players who can still bet (not folded, not all-in)."""
        return [p for p in self.players if not p.folded and not p.all_in]
    
    def validate_action(self, player: Any, action: str, amount: int) -> Tuple[bool, str]:
        """
        Validate if a player's action is legal.
        
        Args:
            player: The player taking the action
            action: The action ('fold', 'check', 'call', 'raise')
            amount: The amount for the action
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if action == 'fold':
            return True, ""
        
        elif action == 'check':
            if player.current_bet < self.current_bet:
                return False, "Must call or fold - cannot check when there's a bet to call"
            return True, ""
        
        elif action == 'call':
            call_amount = self.current_bet - player.current_bet
            if call_amount <= 0:
                return False, "No bet to call - should check instead"
            # Allow calling even if not enough chips (will go all-in)
            return True, ""
        
        elif action == 'raise':
            if amount <= player.current_bet:
                return False, "Raise amount must be greater than current bet"
            
            additional_chips_needed = amount - player.current_bet
            if additional_chips_needed > player.chips:
                return False, "Not enough chips for this raise"
            
            min_raise = self.current_bet + self.big_blind
            if amount < min_raise and additional_chips_needed < player.chips:
                return False, f"Minimum raise is ${min_raise}"
            
            return True, ""
        
        else:
            return False, f"Invalid action: {action}"
    
    def execute_action(self, player: Any, action: str, amount: int) -> Dict[str, Any]:
        """
        Execute a validated player action and return result details.
        
        Args:
            player: The player taking the action
            action: The action to execute
            amount: The amount for the action
            
        Returns:
            Dict with action results for UI display
        """
        result = {
            'player_name': player.name,
            'action': action,
            'amount': amount,
            'display_action': action,
            'display_amount': amount
        }
        
        if action == 'fold':
            player.folded = True
            result['display_action'] = 'fold'
            
        elif action == 'check':
            result['display_action'] = 'check'
            
        elif action == 'call':
            call_amount = self.current_bet - player.current_bet
            
            if call_amount >= player.chips:
                # All-in call
                call_amount = player.chips
                player.all_in = True
                result['display_action'] = 'call_all_in'
            else:
                result['display_action'] = 'call'
            
            player.chips -= call_amount
            player.current_bet += call_amount
            self.pot += call_amount
            result['display_amount'] = call_amount
            
        elif action == 'raise':
            additional_chips_needed = amount - player.current_bet
            
            if additional_chips_needed >= player.chips:
                # All-in raise
                additional_chips_needed = player.chips
                amount = player.current_bet + additional_chips_needed
                player.all_in = True
                result['display_action'] = 'raise_all_in'
            else:
                result['display_action'] = 'raise'
            
            player.chips -= additional_chips_needed
            player.current_bet = amount
            self.pot += additional_chips_needed
            self.current_bet = amount
            result['display_amount'] = amount
        
        return result
    
    def get_betting_order(self, round_name: str) -> List[int]:
        """
        Get the betting order for a given round.
        
        Args:
            round_name: 'Pre-flop', 'Flop', 'Turn', or 'River'
            
        Returns:
            List of player indices in betting order
        """
        if round_name == "Pre-flop":
            # Pre-flop: Start with player after big blind (UTG)
            start_pos = (self.dealer_pos + 3) % len(self.players)
        else:
            # Post-flop: Start with small blind (or first active player after dealer)
            start_pos = (self.dealer_pos + 1) % len(self.players)
        
        # Create betting order starting from start_pos
        order = []
        for i in range(len(self.players)):
            pos = (start_pos + i) % len(self.players)
            if not self.players[pos].folded and not self.players[pos].all_in:
                order.append(pos)
        
        return order
    
    def is_betting_round_complete(self, last_raiser_pos: Optional[int] = None) -> bool:
        """
        Check if the current betting round is complete.
        
        Args:
            last_raiser_pos: Position of the last player who raised
            
        Returns:
            bool: True if betting round is complete
        """
        active_players = self.get_active_players()
        betting_players = self.get_betting_players()
        
        # If only one player left, round is complete
        if len(active_players) <= 1:
            return True
        
        # If no one can bet, round is complete
        if len(betting_players) == 0:
            return True
        
        # Check if all betting players have equal bets
        if len(betting_players) > 0:
            current_bets = [p.current_bet for p in betting_players]
            if not all(bet == self.current_bet for bet in current_bets):
                return False
        
        return True
    
    def reset_bets_for_new_round(self):
        """Reset player bets for a new betting round (post-flop)."""
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
    
    def deal_community_cards(self, num_cards: int):
        """
        Deal community cards.
        
        Args:
            num_cards: Number of cards to deal (3 for flop, 1 for turn/river)
        """
        for _ in range(num_cards):
            card = self.deck.draw(1)[0]
            self.community_cards.append(card)
    
    def evaluate_hands(self) -> List[Tuple[Any, int]]:
        """
        Evaluate all active player hands.
        
        Returns:
            List of (player, score) tuples sorted by best hand (lower score = better)
        """
        active_players = self.get_active_players()
        scores = []
        
        for player in active_players:
            if len(self.community_cards) >= 3:
                score = self.evaluator.evaluate(self.community_cards, player.hand)
            else:
                # Pre-flop or early evaluation - use basic high card
                score = 7462 - max(Card.get_rank_int(card) for card in player.hand)
            scores.append((player, score))
        
        # Sort by best hand (lower score is better in treys)
        scores.sort(key=lambda x: x[1])
        return scores
    
    def determine_winners(self, scores: List[Tuple[Any, int]]) -> List[Any]:
        """
        Determine winners from evaluated hands.
        
        Args:
            scores: List of (player, score) tuples from evaluate_hands()
            
        Returns:
            List of winning players (can be multiple for ties)
        """
        if not scores:
            return []
        
        winning_score = scores[0][1]
        winners = [player for player, score in scores if score == winning_score]
        return winners
    
    def distribute_pot(self, winners: List[Any]) -> int:
        """
        Distribute the pot to winners, handling side pots properly.
        
        Args:
            winners: List of winning players
            
        Returns:
            Total amount distributed
        """
        if not winners:
            return 0
        
        # First create side pots based on current bets
        self._create_side_pots()
        
        total_distributed = 0
        
        # Distribute main pot
        if self.main_pot > 0:
            # All non-folded players are eligible for main pot
            eligible_winners = [w for w in winners if not w.folded]
            if eligible_winners:
                prize_per_winner = self.main_pot // len(eligible_winners)
                for winner in eligible_winners:
                    winner.chips += prize_per_winner
                    total_distributed += prize_per_winner
        
        # Distribute side pots
        for side_pot in self.side_pots:
            # Find winners who are eligible for this side pot
            eligible_winners = [w for w in winners if w in side_pot['eligible_players']]
            
            if eligible_winners:
                prize_per_winner = side_pot['amount'] // len(eligible_winners)
                for winner in eligible_winners:
                    winner.chips += prize_per_winner
                    total_distributed += prize_per_winner
        
        return total_distributed
    
    def get_side_pot_winners(self, all_scores: List[Tuple[Any, int]]) -> List[Dict[str, Any]]:
        """
        Determine winners for each side pot separately.
        
        Args:
            all_scores: List of (player, score) tuples from hand evaluation
            
        Returns:
            List of side pot results with winners and amounts
        """
        # Create side pots first
        self._create_side_pots()
        
        results = []
        
        # Main pot
        if self.main_pot > 0:
            # All non-folded players compete for main pot
            active_players = [p for p in self.players if not p.folded]
            eligible_scores = [(p, s) for p, s in all_scores if p in active_players]
            
            if eligible_scores:
                winners = self.determine_winners(eligible_scores)
                prize_per_winner = self.main_pot // len(winners) if winners else 0
                
                results.append({
                    'pot_type': 'Main Pot',
                    'amount': self.main_pot,
                    'winners': winners,
                    'prize_per_winner': prize_per_winner
                })
        
        # Side pots
        for i, side_pot in enumerate(self.side_pots):
            eligible_scores = [(p, s) for p, s in all_scores if p in side_pot['eligible_players']]
            
            if eligible_scores:
                winners = self.determine_winners(eligible_scores)
                prize_per_winner = side_pot['amount'] // len(winners) if winners else 0
                
                results.append({
                    'pot_type': f'Side Pot {i + 1}',
                    'amount': side_pot['amount'],
                    'winners': winners,
                    'prize_per_winner': prize_per_winner
                })
        
        return results
    
    def advance_dealer_button(self):
        """Move the dealer button to the next position."""
        if len(self.players) > 1:
            self.dealer_pos = (self.dealer_pos + 1) % len(self.players)
    
    def get_winner_hand_description(self, winner: Any, scores: List[Tuple[Any, int]]) -> str:
        """
        Get a description of the winning hand.
        
        Args:
            winner: The winning player
            scores: List of (player, score) tuples
            
        Returns:
            String description of the winning hand
        """
        for player, score in scores:
            if player == winner:
                if len(self.community_cards) >= 3:
                    return self.evaluator.class_to_string(self.evaluator.get_rank_class(score))
                else:
                    return "High Card"
        return "Unknown"
    
    def play_hand(self) -> Dict[str, Any]:
        """
        Play a complete hand of Texas Hold'em.
        
        This method orchestrates the entire hand but delegates UI responsibilities
        to external systems. Returns hand results for logging/analysis.
        
        Returns:
            Dict with hand results including winner, pot size, etc.
        """
        hand_results = {
            'winner': None,
            'pot_size': self.pot,
            'winning_hand': None,
            'eliminated_players': []
        }
        
        # The actual hand playing logic would be called from main_tournament.py
        # with UI coordination. This method provides the framework for hand results.
        
        return hand_results