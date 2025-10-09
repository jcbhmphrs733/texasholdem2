# Texas Hold'em Bot Parent Class for Hackathon
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from treys import Card

class ParentBot(ABC):
    """
    Abstract base class for Texas Hold'em poker bots.
    
    All participant bots must inherit from this class and implement the required abstract methods.
    This ensures a consistent interface for the tournament system.
    
    Basic Usage:
        class MyBot(ParentBot):
            def decide_action(self, game_state):
                # Your bot logic here
                return ('call', 0)  # action and amount
    """
    
    def __init__(self, name: str, chips: int = 1000):
        """
        Initialize the bot with a name and starting chip count.
        
        Args:
            name (str): The name of your bot (will be displayed in the game)
            chips (int): Starting chip count (default: 1000)
        """
        self.name = name
        self.chips = chips
        self.hand = []  # Your two hole cards (will be set by the game)
        self.current_bet = 0  # Your current bet in this round
        self.folded = False  # Whether you've folded this hand
        self.all_in = False  # Whether you're all-in
        
        # Additional state tracking (optional to use)
        self.hands_played = 0
        self.hands_won = 0
        self.total_winnings = 0
    
    @abstractmethod
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """
        REQUIRED: Decide what action to take given the current game state.
        
        This is the main method your bot needs to implement. It will be called
        whenever it's your bot's turn to act.
        
        Args:
            game_state (Dict): Dictionary containing current game information:
                - 'current_bet' (int): The current highest bet this round
                - 'min_raise' (int): Minimum amount to raise (usually big blind)
                - 'max_raise' (int): Maximum you can bet (your chips + current_bet)
                - 'pot' (int): Total chips in the pot
                - 'community_cards' (List): Community cards dealt so far (empty pre-flop)
                - 'player_bet' (int): Your current bet this round
        
        Returns:
            Tuple[str, int]: (action, amount) where:
                - action: 'fold', 'check', 'call', or 'raise'
                - amount: bet amount (0 for fold/check, call amount for call, raise amount for raise)
        
        Valid Actions:
            - ('fold', 0): Give up your hand
            - ('check', 0): Pass if no bet to call (only if current_bet == player_bet)
            - ('call', call_amount): Match the current bet
            - ('raise', raise_amount): Increase the bet (must be >= min_raise)
        
        Example:
            if game_state['current_bet'] == game_state['player_bet']:
                return ('check', 0)  # No bet to call, so check
            elif self.chips < game_state['current_bet'] - game_state['player_bet']:
                return ('fold', 0)  # Can't afford to call
            else:
                return ('call', game_state['current_bet'])  # Call the bet
        """
        pass
    
    def receive_cards(self, cards: List[int]) -> None:
        """
        Receive your hole cards at the start of a hand.
        
        Called automatically by the game engine. You can override this if you want
        to perform any analysis when you receive your cards.
        
        Args:
            cards (List[int]): List of two card integers (use treys library to decode)
        
        Example:
            def receive_cards(self, cards):
                super().receive_cards(cards)  # Call parent method
                # Your analysis here
                card_strings = [Card.int_to_str(card) for card in cards]
                print(f"Got cards: {card_strings}")
        """
        self.hand = cards
    
    def reset_for_new_hand(self) -> None:
        """
        Reset bot state for a new hand.
        
        Called automatically at the start of each hand. You can override this
        to reset any hand-specific tracking variables.
        """
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.hands_played += 1
    
    # Optional methods to override for advanced functionality
    
    def on_hand_complete(self, winner: str, pot_size: int, winning_hand: Optional[List[int]] = None) -> None:
        """
        Called when a hand is completed. Override to track statistics.
        
        Args:
            winner (str): Name of the player who won the hand
            pot_size (int): Size of the pot that was won
            winning_hand (Optional[List[int]]): The winning hand cards (if shown)
        """
        if winner == self.name:
            self.hands_won += 1
            self.total_winnings += pot_size
    
    def on_player_action(self, player_name: str, action: str, amount: int) -> None:
        """
        Called when any player takes an action. Override to track opponent behavior.
        
        Args:
            player_name (str): Name of the player who acted
            action (str): Action taken ('fold', 'check', 'call', 'raise')
            amount (int): Amount of the action
        """
        pass
    
    def on_community_cards_dealt(self, cards: List[int], stage: str) -> None:
        """
        Called when community cards are dealt. Override to analyze board texture.
        
        Args:
            cards (List[int]): The community cards dealt so far
            stage (str): The current stage ('flop', 'turn', 'river')
        """
        pass
    
    def get_hand_strength(self) -> float:
        """
        Helper method to evaluate hand strength. Override with your own evaluation.
        
        Returns:
            float: Hand strength from 0.0 (worst) to 1.0 (best)
        """
        # Basic implementation - you should override this with better logic
        if not self.hand:
            return 0.0
        
        # Simple high card evaluation
        high_card = max(Card.get_rank_int(card) for card in self.hand)
        return high_card / 12.0  # Normalize to 0-1 range
    
    def calculate_pot_odds(self, game_state: Dict[str, Any]) -> float:
        """
        Helper method to calculate pot odds.
        
        Args:
            game_state (Dict): Current game state
            
        Returns:
            float: Pot odds ratio (pot size / call amount)
        """
        call_amount = game_state['current_bet'] - game_state['player_bet']
        if call_amount <= 0:
            return float('inf')  # No cost to call
        return game_state['pot'] / call_amount
    
    def __str__(self) -> str:
        """String representation of the bot."""
        return f"{self.name} (${self.chips})"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"ParentBot(name='{self.name}', chips={self.chips}, hands_played={self.hands_played})"


# Example implementation for reference
class ExampleBot(ParentBot):
    """
    Example bot implementation showing how to use the ParentBot class.
    This bot uses simple logic and can serve as a starting point.
    """
    
    def decide_action(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """Simple example bot logic."""
        # Can we check?
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        # Get basic hand strength
        hand_strength = self.get_hand_strength()
        
        # Simple decision logic
        if hand_strength < 0.3:  # Weak hand
            if can_check:
                return ('check', 0)
            else:
                return ('fold', 0)
        elif hand_strength < 0.6:  # Medium hand
            if can_check:
                return ('check', 0)
            else:
                call_amount = game_state['current_bet'] - game_state['player_bet']
                if call_amount <= self.chips:
                    return ('call', game_state['current_bet'])
                else:
                    return ('fold', 0)
        else:  # Strong hand
            # Try to raise
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
            elif game_state['current_bet'] <= self.chips + game_state['player_bet']:
                return ('call', game_state['current_bet'])
            else:
                return ('fold', 0)

