# Texas Hold'em Bot Hackathon

Welcome to the Texas Hold'em Bot Hackathon! Create your own poker bot to compete against other participants using our automated tournament system.

## Quick Start

1. **Create your bot file**: Add a `.py` file to the `player_pool/` directory
2. **Implement your bot**: Create a class that inherits from `ParentBot`
3. **Test your bot**: Run `python main_tournament.py` to test in the tournament
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
       def decide_action(self, game_state):
           # Your strategy here
           return ('call', game_state['current_bet'])
   ```

3. **Run the tournament**:
   ```bash
   python main_tournament.py
   ```

Your bot will be **automatically discovered and included** in the tournament!

## Bot Requirements

Your bot must inherit from `ParentBot` and implement the `decide_action` method:

```python
from ParentBot import ParentBot

class YourBot(ParentBot):
    def decide_action(self, game_state):
        # Your strategy here
        return ('call', game_state['current_bet'])  # Example
```

## Game State Information

The `game_state` dictionary contains:
- `current_bet`: Highest bet this round
- `min_raise`: Minimum raise amount
- `max_raise`: Maximum you can bet
- `pot`: Total chips in pot
- `community_cards`: Board cards (empty pre-flop)
- `player_bet`: Your current bet this round

## Valid Actions

Return a tuple `(action, amount)`:
- `('fold', 0)`: Give up your hand
- `('check', 0)`: Pass (only if no bet to call)
- `('call', amount)`: Match current bet
- `('raise', amount)`: Increase the bet

## Your Bot's State

Your bot has access to:
- `self.name`: Your bot's name
- `self.chips`: Current chip count
- `self.hand`: Your two hole cards
- `self.current_bet`: Your bet this round
- `self.folded`: Whether you've folded
- `self.all_in`: Whether you're all-in

## Example Strategies

### Conservative Bot
```python
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

Use the `treys` library for card analysis:
```python
from treys import Card, Evaluator

# Get card rank/suit
rank = Card.get_rank_int(card)  # 2-14 (2=2, 14=Ace)
suit = Card.get_suit_int(card)  # 1-4

# Convert to string
card_str = Card.int_to_str(card)  # e.g., "As" for Ace of Spades

# Evaluate hand strength with community cards
evaluator = Evaluator()
strength = evaluator.evaluate(self.hand, game_state['community_cards'])
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
   ```python
   from ParentBot import ParentBot
   
   class MyStrategyBot(ParentBot):
       def __init__(self, name="MyStrategy", chips=1000):
           super().__init__(name, chips)
       
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
   python main_tournament.py
   ```

5. **Watch your bot compete** in the automated tournament!

## Tips for Success

1. **Start simple**: Get a basic bot working first
2. **Hand evaluation**: Strong hand evaluation is crucial
5. **Bankroll management**: Don't go all-in too often
7. **Pot odds**: Calculate if calls are profitable

## File Structure

```
texasholdem/
├── main_tournament.py       # Tournament runner (run this!)
├── ParentBot.py             # Abstract base class (don't modify)
├── template.py              # Reference template for bot structure (copy into player_pool)
├── game.py                  # Game engine (don't modify)
├── player_pool/             # PUT YOUR BOT HERE!
│   ├── __init__.py          # Auto-discovery system
│   ├── Coyote.py            # Example: conservative bot
│   └── YOUR_BOT_HERE.py     # Your bot file goes here!
└── README.md                # This file
```

## Current Example Bot

The `player_pool/` directory already contains an example bot you can study:

- **Coyote**: Conservative tight play, only premium hands

## Tournament Development Features

- **Automatic Bot Discovery**: Just add your `.py` file to `player_pool/`
- **Version Testing**: You can have multiple bot versions compete in the pool
- **Real-time Tournament**: Watch bots compete with detailed game display
- **Professional Presentation**: Rich console output with tables and colors
- **Error Handling**: Clear error messages if your bot has issues
- **Scalable**: Supports unlimited number of participants

## Submission Process

**No manual submission required!** The tournament system automatically:

1. **Scans** the `player_pool/` directory for `.py` files
2. **Discovers** all classes that inherit from `ParentBot`
3. **Validates** each bot can be instantiated
4. **Includes** all valid bots in the tournament
5. **Reports** any issues with invalid bots

Just create your bot file in `player_pool/` and run the tournament!

Good luck and may the best bot win!