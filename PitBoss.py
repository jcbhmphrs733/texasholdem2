"""
PitBoss Security System for Tournament Bots
Casino-style oversight that prevents bots from cheating with chips and cards.

The PitBoss acts as a security wrapper around participant bots, ensuring game integrity
by monitoring and preventing unauthorized manipulation of chips and hole cards.
Only house-authorized operations (tournament system) can modify protected values.

Features:
- Chip protection with call stack validation
- Hole card security with copy-safe access
- Real-time cheating detection and blocking
- Casino-themed security messaging
- House-always-wins enforcement

The house always wins - no exceptions!
"""

import inspect

class ProtectedDict(dict):
    """
    A dictionary wrapper that prevents chip manipulation while allowing other operations.
    """
    def __init__(self, original_dict, bot_name, pitboss_instance=None):
        super().__init__(original_dict)
        self._bot_name = bot_name
        self._pitboss = pitboss_instance
    
    def __setitem__(self, key, value):
        """Block chip manipulation through dictionary access"""
        if key == 'chips':
            raise AttributeError(
                f"PIT BOSS SECURITY ALERT\n"
                f"BLOCKED: Dictionary chip manipulation attempt!\n"
                f"Bot: '{self._bot_name}'\n" 
                f"Attempted: __dict__['{key}'] = {value}\n"
                f"DICTIONARY ACCESS TO CHIPS IS FORBIDDEN!"
            )
        super().__setitem__(key, value)
    
    def update(self, *args, **kwargs):
        """Block batch updates that include chip manipulation"""
        # Check if chips is in the update
        update_dict = {}
        if args:
            update_dict.update(args[0])
        update_dict.update(kwargs)
        
        if 'chips' in update_dict:
            # Record strike if we have access to PitBoss instance
            if self._pitboss:
                self._pitboss._record_cheat_strike("BULK_MANIPULATION", f"Attempted bulk update with chips")
                
            raise AttributeError(
                f"PIT BOSS: Bulk dictionary update blocked! "
                f"Bot '{self._bot_name}' cannot modify chips via update()."
            )
        super().update(*args, **kwargs)

class PitBoss:
    """
    Casino-style pit boss that watches over bots and prevents cheating.
    Only the house (tournament system) can modify chips and cards through controlled methods.
    """
    
    def __init__(self, bot_instance, starting_chips: int):
        """
        Initialize chip protection for a bot.
        
        Args:
            bot_instance: The actual bot instance
            starting_chips: Starting chip count for tournament
        """
        # Store the original bot
        self._bot = bot_instance
        
        # Protected chip management
        self._legitimate_chips = starting_chips
        self._starting_chips = starting_chips
        
        # Protected hole card management  
        self._legitimate_hand = []
        
        # Store original bot chip value for reference but don't allow direct access
        self._bot_original_chips = getattr(bot_instance, 'chips', 0)
        
        # Block direct __dict__ access to prevent bypassing protection
        self._protected_dict = True
        
        # Security violation tracking
        self._cheat_strikes = 0
        self._max_strikes = 3
        self._is_eliminated = False
        self._cheat_log = []
        
        # Don't copy attributes - use pure delegation through __getattr__
    
    @property
    def chips(self) -> int:
        """Read-only access to chip count."""
        return self._legitimate_chips
    
    @chips.setter
    def chips(self, value: int):
        """
        Completely prevent direct chip manipulation - chips are READ-ONLY!
        Any attempt to modify chips will raise an AttributeError.
        Only the house (tournament system) can modify chips through secure methods.
        """
        raise AttributeError(
            f"PIT BOSS: Chip manipulation blocked! "
            f"Bot '{self.name}' cannot directly modify chips. "
            f"Current chips: {self._legitimate_chips}. "
            f"Only the house controls chip counts."
        )
    
    def __setattr__(self, name, value):
        """
        Intercept ALL attribute setting to prevent ANY chip manipulation.
        """
        # Allow setting of internal PitBoss attributes during initialization
        if name.startswith('_') or name in ['name']:
            super().__setattr__(name, value)
            return
        
        # ABSOLUTELY BLOCK ALL CHIP MANIPULATION ATTEMPTS
        if name == 'chips':
            # Record strike for direct manipulation
            self._record_cheat_strike("DIRECT_MANIPULATION", f"Attempted to set chips to {value}")
            
            raise AttributeError(
                f"PIT BOSS: Chip manipulation blocked! "
                f"Bot '{getattr(self, 'name', 'Unknown')}' cannot modify chips. "
                f"Strikes: {self._cheat_strikes}/{self._max_strikes}"
            )
        
        # For other attributes, delegate to the wrapped bot but NOT chips
        if hasattr(self, '_bot'):
            setattr(self._bot, name, value)
        else:
            super().__setattr__(name, value)
    
    def _tournament_add_chips(self, amount: int):
        """House-authorized method to add chips (winnings approved by pit boss)."""
        self._legitimate_chips += amount
    
    def _tournament_subtract_chips(self, amount: int):
        """House-authorized method to subtract chips (bets collected by house)."""
        self._legitimate_chips = max(0, self._legitimate_chips - amount)
    
    def _tournament_set_chips(self, amount: int):
        """House-authorized method to set exact chip amount (pit boss override)."""
        self._legitimate_chips = amount
        
    @property 
    def folded(self):
        """Check if bot should be folded (either naturally or due to elimination)"""
        if self._is_eliminated:
            return True
        return getattr(self._bot, 'folded', False)
    
    @folded.setter
    def folded(self, value):
        """Allow setting folded status"""
        if hasattr(self._bot, 'folded'):
            self._bot.folded = value
    
    @property
    def hand(self):
        """Read-only access to hole cards - managed by tournament system only."""
        return self._legitimate_hand.copy()  # Return copy to prevent modification
    
    @hand.setter
    def hand(self, value):
        """
        Prevent direct hand manipulation by bots.
        Only allows tournament system to modify hole cards.
        """
        # Get call stack to verify caller
        frame = None
        try:
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            
            # Check if call comes from tournament system
            while caller_frame:
                caller_filename = caller_frame.f_code.co_filename.lower()
                caller_function = caller_frame.f_code.co_name
                
                # Allow tournament system files to modify hands
                if ('game_logic.py' in caller_filename and 
                    caller_function in ['_deal_hole_cards', 'receive_cards', '_tournament_deal_cards']) or \
                   ('main_tournament.py' in caller_filename) or \
                   ('__init__' in caller_function):  # Allow initialization
                    self._legitimate_hand = list(value) if value else []
                    return
                
                caller_frame = caller_frame.f_back
            
            # If we get here, it's an unauthorized hand modification attempt
            print(f"BLOCKED: Bot {self.name} attempted to modify hole cards")
            print(f"   Cards remain at legitimate value: {self._legitimate_hand}")
            
        finally:
            del frame
    
    def _tournament_deal_cards(self, cards: list):
        """House-authorized method to deal cards (dealer supervised by pit boss)."""
        self._legitimate_hand = list(cards) if cards else []
    
    def _tournament_clear_hand(self):
        """House-authorized method to collect cards for new hand (pit boss oversight)."""
        self._legitimate_hand = []
    
    def _record_cheat_strike(self, cheat_type: str, details: str):
        """Record a cheating violation and apply strikes system"""
        # If already eliminated, don't process more strikes or show alerts
        if self._is_eliminated:
            return
            
        self._cheat_strikes += 1
        self._cheat_log.append({
            'strike': self._cheat_strikes,
            'type': cheat_type,
            'details': details
        })
        
        # Compact security alert
        if self._cheat_strikes >= self._max_strikes:
            print(f"SECURITY ALERT - {self.name}: CHEATING STRIKE {self._cheat_strikes}/{self._max_strikes} - {cheat_type} - ELIMINATED!")
            self._is_eliminated = True
            # Set chips to 0 to trigger tournament elimination
            self._legitimate_chips = 0
        else:
            print(f"SECURITY ALERT - {self.name}: CHEATING STRIKE {self._cheat_strikes}/{self._max_strikes} - {cheat_type}")
    
    @property
    def is_eliminated_for_cheating(self) -> bool:
        """Check if bot has been eliminated for excessive cheating"""
        return self._is_eliminated
    
    def decide_action(self, game_state):
        """Override decision making for eliminated bots"""
        if self._is_eliminated:
            # Eliminated bots should not make decisions
            return ('fold', 0)
        
        # Call the wrapped bot's decision method
        if hasattr(self._bot, 'decide_action'):
            return self._bot.decide_action(game_state)
        else:
            return ('fold', 0)
    
    def get_cheat_report(self) -> dict:
        """Get comprehensive cheating report"""
        return {
            'name': self.name,
            'strikes': self._cheat_strikes,
            'max_strikes': self._max_strikes,
            'eliminated': self._is_eliminated,
            'cheat_log': self._cheat_log
        }
        
    def receive_cards(self, cards: list):
        """
        Secure method for receiving cards - only allows tournament system calls.
        This replaces the bot's original receive_cards method.
        """
        # Check call stack to ensure this is from tournament system
        frame = None
        try:
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            
            # Check if call comes from tournament system
            while caller_frame:
                caller_filename = caller_frame.f_code.co_filename.lower()
                caller_function = caller_frame.f_code.co_name
                
                # Allow tournament system files to deal cards
                if 'game_logic.py' in caller_filename and caller_function == '_deal_hole_cards':
                    self._tournament_deal_cards(cards)
                    return
                
                caller_frame = caller_frame.f_back
            
            # If we get here, it's unauthorized
            print(f"BLOCKED: Unauthorized receive_cards call for bot {self.name}")
            
        finally:
            del frame
    
    def reset_for_new_hand(self):
        """
        Reset both PitBoss protection state and delegate to underlying bot.
        This ensures proper synchronization between PitBoss and wrapped bot.
        """
        # Clear PitBoss's protected hand for new hand
        self._legitimate_hand = []
        
        # Delegate to underlying bot's reset method
        if hasattr(self._bot, 'reset_for_new_hand'):
            self._bot.reset_for_new_hand()
    
    def get_chip_integrity_report(self) -> dict:
        """Get integrity report for debugging."""
        return {
            'name': self.name,
            'legitimate_chips': self._legitimate_chips,
            'starting_chips': self._starting_chips,
            'bot_reported_chips': getattr(self._bot, 'chips', 'N/A') if hasattr(self._bot, 'chips') else 'N/A'
        }
    
    def on_player_action(self, player_name: str, action: str, amount: int):
        """
        Intercept callback to prevent cheating during other players' turns.
        Monitor for chip manipulation attempts during distractions.
        """
        # If eliminated for cheating, don't process any callbacks
        if self._is_eliminated:
            return
            
        original_bot_chips = getattr(self._bot, 'chips', 0) if hasattr(self._bot, 'chips') else 0
        
        # Call the bot's callback method
        if hasattr(self._bot, 'on_player_action'):
            try:
                self._bot.on_player_action(player_name, action, amount)
            except Exception as e:
                # Ignore callback errors but log security violations
                pass
        
        # Smart opportunistic monitoring - only flag suspicious increases
        if hasattr(self._bot, 'chips'):
            new_bot_chips = getattr(self._bot, 'chips', 0)
            chip_change = new_bot_chips - original_bot_chips
            
            # Only flag if chips INCREASED during someone else's turn (suspicious)
            # Decreases are normal (blinds, bets, etc.)
            if chip_change > 0:
                self._record_cheat_strike("OPPORTUNISTIC", f"Added {chip_change} chips during {player_name}'s turn")
                
                # Force bot's chips back to legitimate value
                try:
                    self._bot.__dict__['chips'] = self._legitimate_chips
                except:
                    pass  # If we can't set it, PitBoss still overrides it

    def __getattr__(self, name):
        """Delegate other attribute access to the wrapped bot, except for protected attributes."""
        # Block access to chips completely - force use of PitBoss property
        if name == 'chips':
            raise AttributeError(
                f"PIT BOSS: Bot '{getattr(self, 'name', 'Unknown')}' cannot access chips through delegation. "
                f"Use PitBoss.chips property only."
            )
        
        return getattr(self._bot, name)
    
    def __setitem__(self, key, value):
        """Block dictionary-style access to prevent security bypass"""
        if key == 'chips':
            # Record strike if we have access to PitBoss instance
            if self._pitboss:
                self._pitboss._record_cheat_strike("DICT_MANIPULATION", f"Attempted __dict__['chips'] = {value}")
            
            raise AttributeError(
                f"PIT BOSS: Dictionary chip manipulation blocked! "
                f"Bot '{self._bot_name}' cannot modify chips via __dict__."
            )
        super().__setitem__(key, value)
    
    def __getattribute__(self, name):
        """Override attribute access to provide additional protection"""
        if name == '__dict__':
            # Return a protected dictionary that blocks chip manipulation
            original_dict = super().__getattribute__('__dict__')
            return ProtectedDict(original_dict, getattr(self, 'name', 'Unknown'), self)
        return super().__getattribute__(name)
    
    def __str__(self):
        return f"PitBoss[{self.name}]"
    
    def __repr__(self):
        return f"PitBoss(watching={self.name}, chips={self._legitimate_chips})"