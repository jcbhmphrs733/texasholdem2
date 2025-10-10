# Tournament Configuration Settings
"""
Central configuration file for Texas Hold'em Bot Hackathon Tournament.

Modify these settings to customize your tournament format:
- Blind structure and increases
- Starting conditions
- Player limits
- Tournament progression
"""

# =============================================================================
# STARTING CONDITIONS
# =============================================================================

# Starting chip count for each bot
STARTING_CHIPS = 500

# Minimum and maximum number of players allowed in tournament
MIN_PLAYERS = 2
MAX_PLAYERS = 10

# =============================================================================
# BLIND STRUCTURE
# =============================================================================

# Initial blind amounts
SMALL_BLIND_INITIAL = 10
BIG_BLIND_INITIAL = 20

# Blind increase settings
BLIND_INCREASE_FACTOR = 2  # Multiply blinds by this factor when increasing
BLIND_INCREASE_FREQUENCY = 3  # Increase blinds every N hands

# Alternative: You can also define a custom blind schedule
# Set BLIND_INCREASE_FREQUENCY to 0 to use this schedule instead
CUSTOM_BLIND_SCHEDULE = [
    (5, 10),      # Level 1: 5/10
    (10, 20),     # Level 2: 10/20
    (15, 30),     # Level 3: 15/30
    (25, 50),     # Level 4: 25/50
    (50, 100),    # Level 5: 50/100
    (75, 150),    # Level 6: 75/150
    (100, 200),   # Level 7: 100/200
    (150, 300),   # Level 8: 150/300
    (200, 400),   # Level 9: 200/400
    (300, 600),   # Level 10: 300/600
]

# =============================================================================
# TOURNAMENT PROGRESSION
# =============================================================================

# Tournament format options
TOURNAMENT_FORMAT = "elimination"  # Options: "elimination", "timed", "chip_leader"

# For timed tournaments: maximum number of hands to play
MAX_HANDS = 100

# For chip leader tournaments: stop when one player has this percentage of total chips
CHIP_LEADER_THRESHOLD = 0.75  # 75% of all chips

# =============================================================================
# GAME BEHAVIOR
# =============================================================================

# Display settings
SHOW_DETAILED_STATS = True
PAUSE_BETWEEN_HANDS = True
PAUSE_BETWEEN_ACTIONS = True

# Speed settings
AUTO_CONTINUE_DELAY = 0  # Seconds to auto-continue (0 = manual input required)

# =============================================================================
# ADVANCED SETTINGS
# =============================================================================

# Enable ante (additional forced bet from all players)
ANTE_ENABLED = False
ANTE_AMOUNT = 0  # Will be set automatically based on big blind if enabled
ANTE_START_LEVEL = 5  # Start ante at this blind level

# Tournament elimination settings
ELIMINATE_ON_ZERO_CHIPS = True
ALLOW_REBUYS = False  # Future feature
REBUY_PERIOD_HANDS = 20  # Number of hands allowing rebuys

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_blinds_for_hand(hand_number: int) -> tuple[int, int]:
    """
    Calculate the current small and big blind amounts for a given hand number.
    
    Args:
        hand_number (int): Current hand number (1-indexed)
        
    Returns:
        tuple[int, int]: (small_blind, big_blind) amounts
    """
    if BLIND_INCREASE_FREQUENCY == 0:
        # Use custom blind schedule
        level = min((hand_number - 1) // 10, len(CUSTOM_BLIND_SCHEDULE) - 1)
        return CUSTOM_BLIND_SCHEDULE[level]
    else:
        # Use automatic blind increases
        increases = (hand_number - 1) // BLIND_INCREASE_FREQUENCY
        multiplier = BLIND_INCREASE_FACTOR ** increases
        
        small_blind = int(SMALL_BLIND_INITIAL * multiplier)
        big_blind = int(BIG_BLIND_INITIAL * multiplier)
        
        return (small_blind, big_blind)

def get_ante_for_hand(hand_number: int) -> int:
    """
    Calculate the ante amount for a given hand number.
    
    Args:
        hand_number (int): Current hand number (1-indexed)
        
    Returns:
        int: Ante amount (0 if antes not enabled or not started yet)
    """
    if not ANTE_ENABLED:
        return 0
    
    # Determine current blind level
    if BLIND_INCREASE_FREQUENCY == 0:
        level = (hand_number - 1) // 10 + 1
    else:
        level = (hand_number - 1) // BLIND_INCREASE_FREQUENCY + 1
    
    if level >= ANTE_START_LEVEL:
        _, big_blind = get_blinds_for_hand(hand_number)
        return max(1, big_blind // 10)  # Ante is typically 10% of big blind
    
    return 0

def get_tournament_settings_summary() -> str:
    """
    Generate a formatted summary of current tournament settings.
    
    Returns:
        str: Formatted settings summary
    """
    summary = f"""
Tournament Configuration:
  Format: {TOURNAMENT_FORMAT.title()}
  Starting Chips: ${STARTING_CHIPS:,}
  Players: {MIN_PLAYERS}-{MAX_PLAYERS}
  
Blind Structure:
  Initial: ${SMALL_BLIND_INITIAL}/${BIG_BLIND_INITIAL}
  """
    
    if BLIND_INCREASE_FREQUENCY > 0:
        summary += f"  Increases: {BLIND_INCREASE_FACTOR}x every {BLIND_INCREASE_FREQUENCY} hands\n"
    else:
        summary += f"  Custom Schedule: {len(CUSTOM_BLIND_SCHEDULE)} levels\n"
    
    if ANTE_ENABLED:
        summary += f"  Ante: Starts at level {ANTE_START_LEVEL}\n"
    
    return summary

def validate_settings() -> list[str]:
    """
    Validate tournament settings and return any warnings or errors.
    
    Returns:
        list[str]: List of warning/error messages (empty if all valid)
    """
    warnings = []
    
    # Validate player limits
    if MIN_PLAYERS < 2:
        warnings.append("MIN_PLAYERS should be at least 2")
    if MAX_PLAYERS > 23:  # Deck limit for Texas Hold'em
        warnings.append("MAX_PLAYERS should not exceed 23 (deck size limitation)")
    if MIN_PLAYERS > MAX_PLAYERS:
        warnings.append("MIN_PLAYERS cannot be greater than MAX_PLAYERS")
    
    # Validate starting chips vs blinds
    initial_bb_ratio = STARTING_CHIPS / BIG_BLIND_INITIAL
    if initial_bb_ratio < 10:
        warnings.append(f"Starting chips may be too low (only {initial_bb_ratio:.1f} big blinds)")
    elif initial_bb_ratio > 1000:
        warnings.append(f"Starting chips may be too high ({initial_bb_ratio:.1f} big blinds - very long tournament)")
    
    # Validate blind increases
    if BLIND_INCREASE_FREQUENCY > 0 and BLIND_INCREASE_FACTOR <= 1.0:
        warnings.append("BLIND_INCREASE_FACTOR should be greater than 1.0")
    
    # Validate custom blind schedule
    if BLIND_INCREASE_FREQUENCY == 0:
        if not CUSTOM_BLIND_SCHEDULE:
            warnings.append("CUSTOM_BLIND_SCHEDULE cannot be empty when BLIND_INCREASE_FREQUENCY is 0")
        else:
            for i, (sb, bb) in enumerate(CUSTOM_BLIND_SCHEDULE):
                if bb != 2 * sb:
                    warnings.append(f"Blind level {i+1}: Big blind should typically be 2x small blind")
    
    return warnings

# Validate settings when module is imported
if __name__ == "__main__":
    print(get_tournament_settings_summary())
    
    warnings = validate_settings()
    if warnings:
        print("\nConfiguration Warnings:")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\nConfiguration looks good!")
else:
    # Auto-validate when imported
    warnings = validate_settings()
    if warnings:
        print("Tournament configuration warnings detected. Run 'python configure_tournament.py' to see details.")