# REPOSITORY SECURITY GUIDELINES

## FOR PARTICIPANTS: What You Can and Cannot Modify

### **SAFE TO MODIFY** (Your Sandbox):
```
player_pool/
├── YourBot.py          ← Create your bot here
├── template.py         ← Use this as a starting point
└── existing_bots.py    ← Study these for inspiration

dojo.py              ← Customize testing scenarios
README.md            ← Documentation
DOJO_README.md       ← Testing guide
```

### **DO NOT MODIFY** (Core Infrastructure):
```
game_logic.py         ← Poker rules and game mechanics
ParentBot.py          ← Base bot interface (READ ONLY)
main_tournament.py    ← Tournament runner
tournament_ui.py      ← Display system
tournament_stats.py   ← Statistics tracking
tournament_analysis.py ← Post-game analysis
configure_tournament.py ← Tournament settings
get_participants.py   ← Bot discovery system
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
3. **Copy** `template.py` to create `YourBot.py`
4. **Test** with `dojo.py` to validate your strategy
5. **Submit** only your bot file in `player_pool/`