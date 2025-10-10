# Bot Testing Dojo - Simple Bot Validation Tool

A lightweight testing tool for validating poker bot behavior against expected outcomes in common scenarios.

## Overview

The Dojo provides a simple command-line interface to test your bot's decision-making in predefined poker scenarios. It helps ensure your bot makes reasonable decisions and can identify areas that need improvement.

## Quick Start

1. **Ensure your bot is in the `player_pool` directory**
   ```
   player_pool/
   ├── YourBot.py
   ├── Coyote.py
   └── ...
   ```

2. **Run the Dojo with your bot name**
   ```bash
   python dojo.py YourBot
   ```

3. **Review the test results** to see how your bot performs

## Test Scenarios

The Dojo tests your bot against 10 diverse poker scenarios covering various hand types and situations:

### 1. Premium Hand Pre-flop
- **Cards**: Pocket Aces (As Ah)
- **Expected**: Raise (aggressive play with premium hand)
- **Tests**: Pre-flop aggression with strong holdings

### 2. Strong Hand Value Bet
- **Cards**: Ace-King (As Kd) on Ace-high flop (Ah 7c 3s)
- **Expected**: Raise (value betting top pair top kicker)
- **Tests**: Post-flop value betting

### 3. Drawing Hand Decision
- **Cards**: King-Queen of hearts (Kh Qh) on Jack-high board (Jh 9s 2c)
- **Expected**: Call (drawing to straight with good pot odds)
- **Tests**: Drawing hand evaluation and pot odds

### 4. Weak Hand Fold
- **Cards**: Seven-deuce (7h 2s) on King-Queen-Jack board (Kc Qd Js)
- **Expected**: Fold (weak hand facing pressure)
- **Tests**: Proper folding with weak holdings

### 5. Made Hand River Value
- **Cards**: Pocket Aces (As Ah) on safe river (Kd Qc 7h 3s 2h)
- **Expected**: Raise (value betting strong hand on river)
- **Tests**: River value betting

### 6. Suited Connectors Pre-flop
- **Cards**: Eight-seven suited (8s 7s) pre-flop
- **Expected**: Call (speculative hand with drawing potential)
- **Tests**: Playing drawing hands for implied odds

### 7. Pocket Pair vs Overcard
- **Cards**: Pocket Jacks (Jh Js) on King-high flop (Kc 9d 4h)
- **Expected**: Call (pocket pair needs caution against overcard)
- **Tests**: Conservative play when facing danger

### 8. Flush Draw on Turn
- **Cards**: Ace-six diamonds (Ad 6d) with diamond draw (Kd 9d 4h 2s)
- **Expected**: Call (nut flush draw with good pot odds)
- **Tests**: Turn drawing decisions

### 9. Trash Hand Pre-flop
- **Cards**: Nine-three offsuit (9h 3c) facing large bet
- **Expected**: Fold (weak hand should fold to aggression)
- **Tests**: Discipline with weak holdings

### 10. Two Pair Value Bet
- **Cards**: Ace-eight (Ah 8c) making two pair (As 8h 3d 7s)
- **Expected**: Raise (strong two pair should bet for value)
- **Tests**: Turn value betting with strong hands

## Understanding Results

### Test Output
```
Testing Bot: YourBot

YourBot Test Results:
┌──────────────────────┬────────────┬─────────┬──────────┬─────────────┬───────┬──────────────┐
│ Scenario             │ Hole Cards │ Board   │ Expected │ Actual      │ Match │ Hand Strength│
├──────────────────────┼────────────┼─────────┼──────────┼─────────────┼───────┼──────────────┤
│ Premium Hand Pre-flop│ As Ah      │ Pre-flop│ RAISE    │ RAISE $60   │ YES   │ 0.950        │
│ Strong Hand Value Bet│ As Kd      │ Ah 7c 3s│ RAISE    │ RAISE $40   │ YES   │ 0.857        │
│ Drawing Hand Decision│ Kh Qh      │ Jh 9s 2c│ CALL     │ CALL        │ YES   │ 0.423        │
│ Weak Hand Fold       │ 7h 2s      │ Kc Qd Js│ FOLD     │ FOLD        │ YES   │ 0.051        │
│ Made Hand River Value│ As Ah      │ ... 2h  │ RAISE    │ RAISE $75   │ YES   │ 0.892        │
└──────────────────────┴────────────┴─────────┴──────────┴─────────────┴───────┴──────────────┘

Test Summary:
Total Tests: 10
Passed: 9
Failed: 1
Success Rate: 90.0%

EXCELLENT: Bot passed all tests!
```

### Success Ratings
- **EXCELLENT (100%)**: Bot passed all tests
- **GOOD (80%+)**: Bot shows solid strategic understanding
- **FAIR (60%+)**: Bot needs some strategic adjustments  
- **POOR (<60%)**: Bot requires significant strategy improvements

## Bot Requirements

Your bot must be compatible with the tournament system:

```python
class YourBot(ParentBot):
    def decide_action(self, game_state):
        """
        Make a decision based on the current game state.
        
        Args:
            game_state (dict): Current game information
            
        Returns:
            tuple: (action, amount) where action is 'fold'/'check'/'call'/'raise'
        """
        # Your decision logic here
        return action, amount
        
    def get_hand_strength(self):  # Optional but recommended
        """
        Calculate hand strength for analysis.
        
        Returns:
            float: Hand strength value between 0 and 1
        """
        # Your hand evaluation logic here
        return strength_value
```

## Development Workflow

### 1. Initial Testing
```bash
python dojo.py YourBot
```
Run this frequently during development to catch issues early.

### 2. Analyze Failures
When tests fail, the output shows:
- What decision was expected vs actual
- The reasoning behind the expected decision
- Your bot's hand strength evaluation (if available)

### 3. Iterate and Improve
Focus on failed scenarios:
- Review your decision logic for those situations
- Adjust hand evaluation or betting logic
- Re-test to confirm improvements

### 4. Aim for Consistency
A good bot should consistently pass these fundamental tests.

## Tips for Success

### 1. Start with Hand Evaluation
Ensure your bot can properly evaluate hand strength. The hand strength column helps verify this.

### 2. Understand Basic Strategy
- Premium hands (AA, KK) should be played aggressively
- Strong made hands should bet for value
- Drawing hands with good odds should call
- Weak hands facing pressure should fold

### 3. Test Frequently
Run the dojo after any significant changes to your bot's logic.

### 4. Focus on Failed Scenarios
When tests fail, understand why the expected action makes sense from a poker strategy perspective.

## Troubleshooting

### Bot Not Found
```
Error: Could not import bot 'YourBot'
Make sure YourBot.py exists in the player_pool directory
```
- Check that your bot file exists in `player_pool/`
- Verify the filename matches the class name

### Import Errors
```
Error: No class 'YourBot' found in YourBot.py
```
- Ensure your class name matches the filename
- Check that your bot inherits from `ParentBot`

### Runtime Errors
If a scenario shows "ERROR" as the actual action:
- Check for syntax errors in your `decide_action` method
- Verify you're handling the `game_state` dictionary correctly
- Ensure you return a valid (action, amount) tuple

## Available Bots

Run without arguments to see available bots:
```bash
python dojo.py

Usage: python dojo.py <BotName>

Example: python dojo.py Coyote

Available bots:
  - Coyote
  - YourBot
```

---

**Quick validation for better bots!** 

Use this tool regularly during development to ensure your bot makes sound fundamental decisions.