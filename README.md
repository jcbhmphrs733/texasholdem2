# Texas Hold'em Bot Hackathon

Welcome to the Texas Hold'em Bot Hackathon! Create your own poker bot to compete against other participants using our automated tournament system. If this is your first time playing Texas Hold'em or you if would like a quick refresher, click here -> [Texas Hold'em](https://en.wikipedia.org/wiki/Texas_hold_%27em)


## Quick Start

1. **Add dependancies**
    ```bash
    python -m pip install rich treys
    ```
2. **Create your bot file**: Add a `.py` file to the `player_pool/` directory
2. **Implement your bot**: Create a class that inherits from `ParentBot`
3. **Test your bot**: Use the Dojo in `botDev/` or run `python main_tournament.py`
4. **Your bot is automatically included**: The system discovers and includes all valid bots!

## Player Pool System

The tournament uses an **automatic bot discovery system**. Simply:

1. **Create your bot file** in the `player_pool/` directory:
   ```
   player_pool/my_awesome_bot.py
   ```

2. **Implement your bot class**:
   ```python
   from ParentBot import ParentBot
   
   class MyAwesomeBot(ParentBot):
       def __init__(self, name="MyAwesomeBot"):
           super().__init__(name)
           
       def decide_action(self, game_state):
           # Your strategy here
           return ('call', game_state['current_bet'])
   ```

3. **Run the tournament**:
   ```bash
   python main_tournament.py
   ```

Your bot will be **automatically discovered and included** in the tournament after a quick validation to ensure neccesary requirements have been met!

## Bot Requirements

Your bot must inherit from `ParentBot` and implement the `decide_action` method:

```python
from ParentBot import ParentBot

class YourBot(ParentBot):
    def __init__(self, name="YourBot"):
        super().__init__(name)
        
    def decide_action(self, game_state):
        # Your strategy here
        return ('call', game_state['current_bet'])  # Example
```

## Game State Information

The `game_state` dictionary contains all the information you need:

### Basic Game Info
- `current_bet`: Highest bet this round
- `min_raise`: Minimum raise amount  
- `pot`: Total chips in pot
- `community_cards`: Board cards (empty pre-flop)
- `player_bet`: Your current bet this round
- `small_blind`: Current small blind amount
- `big_blind`: Current big blind amount

### Enhanced Opponent Information
- `players`: List of all players with their current status
- `opponent_chips`: Dictionary of opponent chip counts
- `opponent_positions`: Dictionary of opponent positions
- `action_history`: Recent actions taken by all players this hand
- `betting_patterns`: Track opponent betting tendencies

Your bot also receives callbacks for advanced strategy:
- `on_player_action(player_name, action, amount)`: When any player acts
- `on_community_cards_dealt(cards, stage)`: When flop/turn/river dealt
- `on_hand_complete(winner, pot_size, winning_hand)`: When hand ends

## Valid Actions

Return a tuple `(action, amount)`:
- `('fold', 0)`: Give up your hand
- `('check', 0)`: Pass (only if no bet to call)
- `('call', amount)`: Match current bet
- `('raise', amount)`: Increase the bet

## Your Bot's State

Your bot has access to:
- `self.name`: Your bot's name
- `self.chips`: Current chip count (managed automatically by tournament)
- `self.hand`: Your two hole cards
- `self.current_bet`: Your bet this round
- `self.folded`: Whether you've folded
- `self.all_in`: Whether you're all-in

**Note**: You don't need to manage chips in your constructor - the tournament system handles starting chips and updates automatically!

## Example Strategies

### Conservative Bot
```python
class ConservativeBot(ParentBot):
    def __init__(self, name="Conservative"):
        super().__init__(name)
        
    def decide_action(self, game_state):
        hand_strength = self.get_hand_strength()
        can_check = game_state['current_bet'] == game_state['player_bet']
        
        if hand_strength < 0.7:  # Only play strong hands
            return ('check', 0) if can_check else ('fold', 0)
        else:
            min_raise = game_state['current_bet'] + game_state['min_raise']
            return ('raise', min_raise) if min_raise <= self.chips else ('call', game_state['current_bet'])
```

### Aggressive Bot
```python
class AggressiveBot(ParentBot):
    def __init__(self, name="Aggressive"):
        super().__init__(name)
        
    def decide_action(self, game_state):
        if random.random() < 0.6:  # 60% chance to raise
            min_raise = game_state['current_bet'] + game_state['min_raise']
            if min_raise <= self.chips + game_state['player_bet']:
                return ('raise', min_raise)
        
        can_check = game_state['current_bet'] == game_state['player_bet']
        return ('check', 0) if can_check else ('call', game_state['current_bet'])
```

## Advanced Bot Features

You can override these optional methods for sophisticated behavior:

### Hand Evaluation
```python
def get_hand_strength(self):
    # Implement sophisticated hand evaluation
    # Return float 0.0 (worst) to 1.0 (best)
    pass
```

### Performance Tracking
```python
def on_hand_complete(self, winner, pot_size, winning_hand=None):
    super().on_hand_complete(winner, pot_size, winning_hand)
    # Your tracking logic here
```

### Community Cards Analysis
```python
def on_community_cards_dealt(self, cards, stage):
    # Analyze board texture (flop, turn, river)
    pass
```

## Helper Methods

The `ParentBot` class provides useful helpers:
- `get_hand_strength()`: Basic hand evaluation
- `calculate_pot_odds(game_state)`: Pot odds calculation

## Card Utilities

Use the `treys` library for card utilities:
```python
from treys import Card

# Get card rank/suit
rank = Card.get_rank_int(card)  # 2-14 (2=2, 14=Ace)
suit = Card.get_suit_int(card)  # 1-4

# Convert to string
card_str = Card.int_to_str(card)  # e.g., "As" for Ace of Spades

# Implement your own hand evaluation logic using community cards!
# Your creativity in hand evaluation will determine your bot's success
```

## Testing Your Bot

The tournament system automatically discovers your bot when you run:

```bash
python main_tournament.py
```

You'll see output like:
```
Discovering participant bots...
Discovered bot: MyAwesomeBot from my_awesome_bot.py
Discovered bot: AliceBot from alice_bot.py
Found 2 participant bot(s) ready for tournament!

Tournament Participants (2 bots):
  1. MyAwesomeBot (MyAwesomeBot)
  2. Coyote (Coyote)
```

No manual registration required!

## Tournament Rules

- Starting chips: 500
- Blind structure: 5/10
- Elimination: When you reach 0 chips
- Winner: Last bot standing

## Getting Started - Step by Step

1. **Navigate to the project directory**:
   ```bash
   cd texasholdem
   ```

2. **Create your bot file**:
   ```bash
   # Create your bot in the player_pool directory
   # Example: player_pool/my_strategy_bot.py
   ```

3. **Copy the basic template**:
   ```bash
   cp botDev/template.py player_pool/my_strategy_bot.py
   ```
   
   Then edit `player_pool/my_strategy_bot.py`:
   ```python
   from ParentBot import ParentBot
   
   class MyStrategyBot(ParentBot):
       def __init__(self, name="MyStrategy"):
           super().__init__(name)
       
       def decide_action(self, game_state):
           # Your poker strategy here
           can_check = game_state['current_bet'] == game_state['player_bet']
           if can_check:
               return ('check', 0)
           else:
               return ('call', game_state['current_bet'])
   ```

4. **Test your bot**:
   ```bash
   # Test against scenarios
   cd botDev
   python dojo.py MyStrategyBot
   
   # Or run full tournament
   cd ..
   python main_tournament.py
   ```

5. **Watch your bot compete** in the automated tournament!

## Tips for Success

1. **Start simple**: Copy `botDev/template.py` to get a working bot first
2. **Study Coyote**: The 94-line reference bot shows clean hand evaluation and position play
3. **Use the Dojo**: Test your bot with `cd botDev && python dojo.py YourBot`
4. **Hand evaluation**: Strong hand evaluation is crucial for good play
5. **Position awareness**: Use the `opponent_positions` data for better decisions
6. **Opponent modeling**: Track betting patterns with `action_history`
7. **Bankroll management**: Don't go all-in too often

## Enhanced Features (New!)

This tournament system includes advanced features for sophisticated bots:

- **Opponent Analysis**: Track chip counts, positions, and betting patterns
- **Action History**: See what actions players took this hand
- **Callback System**: React to community cards and hand completions  
- **Real-time Updates**: Get notified when opponents act
- **Professional UI**: Rich tournament display with detailed statistics
- **Bot Testing**: Dedicated dojo for scenario-based testing

## File Structure

```
texasholdem/
├── main_tournament.py          # Tournament runner (run this!)
├── ParentBot.py                # Abstract base class (don't modify)
├── game_logic.py               # Game engine (don't modify)
├── player_pool/     <------    # PUT YOUR BOT HERE!
│   ├── __init__.py             # Auto-discovery system
│   ├── Coyote.py               # Example: lean balanced bot
│   └── YOUR_BOT_HERE.py        # Your bot file goes here!
├── botDev/                     # Bot development tools
│   ├── dojo.py                 # Test your bot
│   ├── template.py             # Copy this to start your bot
│   └── DOJO_README.md          # Dojo documentation
├── Setup/                      # Tournament configuration (advanced)
│   ├── tournament_ui.py        # UI components
│   ├── tournament_stats.py     # Statistics tracking
│   └── configure_tournament.py # Tournament settings
├── security/                   # Security & anti-cheat systems
│   ├── SECURITY.md             # Security guidelines
│   └── validate_tournament.py  # Tournament validation
└── README.md                   # This file
```

## Current Example Bot

The `player_pool/` directory contains a reference implementation:

- **Coyote**: Lean, balanced bot demonstrating hand evaluation, position play, and betting logic. Perfect reference for beginners!

## Bot Development Tools

### Testing Dojo (`botDev/dojo.py`)
Test your bot against 10 challenging scenarios:
```bash
cd botDev
python dojo.py YourBotName
```

### Bot Template (`botDev/template.py`)
Copy this template to create your own bot:
```bash
cp botDev/template.py player_pool/my_awesome_bot.py
```

## Tournament Development Features

- **Automatic Bot Discovery**: Just add your `.py` file to `player_pool/`
- **Enhanced Game State**: Access opponent information and betting history
- **Bot Testing Dojo**: Test against 10 challenging scenarios in `botDev/`
- **Template System**: Copy `botDev/template.py` to quick-start your bot
- **Version Testing**: You can have multiple bot versions compete
- **Real-time Tournament**: Watch bots compete with detailed game display
- **Comprehensive Analysis**: Detailed post-tournament statistics and performance metrics
- **Professional Presentation**: Rich console output with tables and colors
- **Error Handling**: Clear error messages if your bot has issues
- **Organized Structure**: Clean separation of bots, tools, and configuration
- **Scalable**: Supports unlimited number of participants

## Running the tournament

1. **Scans** the `player_pool/` directory for `.py` files
2. **Discovers** all classes that inherit from `ParentBot`
3. **Validates** each bot can be instantiated
4. **Includes** all valid bots in the tournament
5. **Reports** any issues with invalid bots

Just create your bot file in `player_pool/` and run the tournament!

Good luck and may the best bot win!