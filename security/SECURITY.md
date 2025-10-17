# TOURNAMENT SECURITY SYSTEMS

## Anti-Cheat & Protection Infrastructure

### **SAFE TO MODIFY** (Your Sandbox):
```
player_pool/
├── YourBot.py          ← Create your bot here
└── existing_bots.py    ← Study these for inspiration

botDev/
├── dojo.py             ← Test your bot against scenarios
├── template.py         ← Copy this to start your bot
└── DOJO_README.md      ← Testing guide

README.md               ← Main documentation
```

### **DO NOT MODIFY** (Core Infrastructure):
```
game_logic.py           ← Poker rules and game mechanics
ParentBot.py            ← Base bot interface (READ ONLY)
main_tournament.py      ← Tournament runner

Setup/                  ← Tournament system components
├── tournament_ui.py    ← Display system
├── tournament_stats.py ← Statistics tracking
├── tournament_analysis.py ← Post-game analysis
└── configure_tournament.py ← Tournament settings

security/               ← Security & anti-cheat systems
├── PitBoss.py          ← Casino-style bot protection wrapper
├── SECURITY.md         ← This file
├── validate_tournament.py ← System validation
└── secure_repo.py      ← Security tools
```

### **READ FOR LEARNING** (Study These):
- **`game_logic.py`**: Understand poker rules, hand evaluation, betting logic
- **`ParentBot.py`**: Learn the required interface for your bot
- **`tournament_ui.py`**: See how the tournament displays information
- **Existing bots**: Study different strategies in `player_pool/`

### **Why These Restrictions?**
1. **Fair Competition**: All bots must use the same game rules
2. **No Cheating**: Prevents modification of core game mechanics
3. **Stability**: Protects against breaking the tournament system
4. **Learning**: Forces participants to work within the bot interface

### **What Happens If You Modify Protected Files?**
- Your changes will be ignored during tournament runs
- May cause your bot to fail or be disqualified
- Tournament runs from a clean version of core files

### **Recommended Workflow**:
1. **Read** `ParentBot.py` to understand the interface
2. **Study** `game_logic.py` to understand poker rules
3. **Copy** `botDev/template.py` to create `player_pool/YourBot.py`
4. **Test** with `dojo.py` to validate your strategy

---

## PitBoss Anti-Cheat System

### **What is PitBoss?**
A casino-style security wrapper that prevents bots from cheating by manipulating chips or cards.

### **How It Works:**
- **Wrapper Pattern**: Every bot is automatically wrapped with `PitBoss` protection
- **Read-Only Attributes**: Chips and hole cards become completely read-only
- **Secure Methods**: Only the tournament system can modify chips through authorized methods
- **Perfect Conservation**: Guarantees no chips are lost or gained illegally

### **Protection Features:**
```python
# ALLOWED - Reading values
bot.chips           # Returns current chip count
bot.hand           # Returns copy of hole cards

# BLOCKED - All manipulation attempts
bot.chips = 1000    # AttributeError: Direct chip access denied!
bot.chips += 200    # AttributeError: Direct chip access denied!
bot.hand = [A, A]   # AttributeError: Hole card manipulation blocked!
```

### **House-Authorized Operations:**
- `_tournament_add_chips(amount)` - Award winnings
- `_tournament_subtract_chips(amount)` - Collect bets
- `_tournament_deal_cards(cards)` - Deal hole cards
- `_tournament_clear_hand()` - Collect cards for new hand

### **Security Guarantees:**
- **Chip Conservation**: Total chips remain constant (5 players × $500 = $2,500)
- **Manipulation Prevention**: No bot can artificially inflate chip counts
- **Fair Play**: All bots operate under identical restrictions
- **Casino Oversight**: PitBoss monitors all transactions
5. **Submit** only your bot file in `player_pool/`