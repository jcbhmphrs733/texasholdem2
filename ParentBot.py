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
    
    def __init__(self, name: str):
        """
        Initialize the bot with a name. Chips are managed by the tournament system.
        
        Args:
            name (str): The name of your bot (will be displayed in the game)
        """
        self.name = name
        self.chips = 0  # Will be set by tournament system
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
                BASIC GAME STATE:
                - 'current_bet' (int): The current highest bet this round
                - 'min_raise' (int): Minimum amount to raise (usually big blind)
                - 'max_raise' (int): Maximum you can bet (your chips + current_bet)
                - 'pot' (int): Total chips in the pot
                - 'community_cards' (List): Community cards dealt so far (empty pre-flop)
                - 'player_bet' (int): Your current bet this round
                
                ENHANCED OPPONENT INFORMATION:
                - 'opponents' (List[Dict]): List of opponent information:
                    * 'name' (str): Opponent's name
                    * 'chips' (int): Opponent's chip count
                    * 'current_bet' (int): Opponent's bet this round
                    * 'position' (int): Opponent's table position
                    * 'is_dealer' (bool): Whether opponent is dealer
                    * 'folded' (bool): Whether opponent has folded
                    * 'all_in' (bool): Whether opponent is all-in
                    * 'active' (bool): Whether opponent can still act
                
                POSITION INFORMATION:
                - 'your_position' (int): Your position at the table
                - 'dealer_position' (int): Current dealer position
                - 'num_active_players' (int): Number of players still in hand
                - 'num_betting_players' (int): Number of players who can still bet
                
                ACTION HISTORY (resets each hand):
                - 'hand_actions' (List[Dict]): Actions taken this hand:
                    * 'player_name' (str): Who acted
                    * 'action' (str): What they did
                    * 'amount' (int): How much
                    * 'round' (str): When (Pre-flop, Flop, Turn, River)
                    * 'position' (int): Their position
                
                BLIND INFORMATION:
                - 'small_blind' (int): Small blind amount
                - 'big_blind' (int): Big blind amount
        
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
        Called when a hand is completed. Override to track statistics and learn
        from results. This is called for all players regardless of who won.
        
        Args:
            winner (str): Name of the player who won the hand
            pot_size (int): Size of the pot that was won
            winning_hand (Optional[List[int]]): The winning hand cards (if showdown occurred)
        
        Example:
            def on_hand_complete(self, winner, pot_size, winning_hand):
                super().on_hand_complete(winner, pot_size, winning_hand)
                
                if winner == self.name:
                    self.recent_wins.append(pot_size)
                else:
                    # Learn from opponent's winning strategy
                    if winning_hand:
                        self.analyze_opponent_showdown(winner, winning_hand)
        """
        if winner == self.name:
            self.hands_won += 1
            self.total_winnings += pot_size
    
    def on_player_action(self, player_name: str, action: str, amount: int) -> None:
        """
        Called when any player (including yourself) takes an action. 
        Override to track opponent behavior and build opponent models.
        
        This method is called immediately after each action is executed,
        allowing you to analyze betting patterns, aggression levels, and
        other behavioral indicators.
        
        Args:
            player_name (str): Name of the player who acted
            action (str): Action taken ('fold', 'check', 'call', 'raise', 'call_all_in', 'raise_all_in')
            amount (int): Amount of the action (0 for fold/check, bet amount for others)
        
        Example:
            def on_player_action(self, player_name, action, amount):
                if player_name != self.name:  # Track opponents only
                    if action in ['raise', 'raise_all_in']:
                        self.opponent_aggression[player_name] += 1
                    elif action == 'fold':
                        self.opponent_fold_frequency[player_name] += 1
        """
        pass
    
    def on_community_cards_dealt(self, cards: List[int], stage: str) -> None:
        """
        Called when community cards are dealt. Override to analyze board texture
        and adjust your strategy based on how the board develops.
        
        Args:
            cards (List[int]): The community cards dealt so far (complete list)
            stage (str): The current stage ('flop', 'turn', 'river')
        
        Example:
            def on_community_cards_dealt(self, cards, stage):
                if stage == 'flop':
                    # Analyze flop texture (wet vs dry, coordinated vs rainbow)
                    self.board_texture = self.analyze_flop_texture(cards)
                elif stage == 'turn':
                    # Check if turn card improved draws
                    self.turn_improved_draws = self.check_turn_draws(cards)
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
