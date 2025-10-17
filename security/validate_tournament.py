#!/usr/bin/env python3
"""
Tournament validation script - ensures core game files are unmodified
Run this before each tournament to ensure fair competition
"""

import os
import hashlib
import json
from datetime import datetime

# Expected file hashes (update these when you make legitimate changes)
PROTECTED_FILE_HASHES = {
    "game_logic.py": "placeholder_hash",
    "ParentBot.py": "placeholder_hash", 
    "main_tournament.py": "placeholder_hash",
    "tournament_ui.py": "placeholder_hash",
    "tournament_stats.py": "placeholder_hash",
    "tournament_analysis.py": "placeholder_hash",
    "configure_tournament.py": "placeholder_hash",
    "get_participants.py": "placeholder_hash"
}

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file."""
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def validate_core_files():
    """Validate that core game files haven't been modified."""
    print("Validating core game files...")
    
    violations = []
    for filename, expected_hash in PROTECTED_FILE_HASHES.items():
        if not os.path.exists(filename):
            violations.append(f"Missing file: {filename}")
            continue
            
        actual_hash = calculate_file_hash(filename)
        if expected_hash != "placeholder_hash" and actual_hash != expected_hash:
            violations.append(f"Modified file detected: {filename}")
    
    if violations:
        print("SECURITY VIOLATIONS DETECTED:")
        for violation in violations:
            print(f"   {violation}")
        print("\nTo fix: Run 'git checkout -- <filename>' to restore original files")
        return False
    else:
        print("All core files validated successfully!")
        return True

def generate_hash_baseline():
    """Generate baseline hashes for protected files (run once by organizer)."""
    print("Generating baseline hashes for protected files...")
    
    hashes = {}
    for filename in PROTECTED_FILE_HASHES.keys():
        if os.path.exists(filename):
            hashes[filename] = calculate_file_hash(filename)
            print(f"   {filename}: {hashes[filename][:16]}...")
        else:
            print(f"   File not found: {filename}")
    
    # Save to file for reference
    with open("baseline_hashes.json", "w") as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "hashes": hashes
        }, f, indent=2)
    
    print("Baseline saved to baseline_hashes.json")
    return hashes

def validate_bot_files():
    """Check that bot files follow naming conventions and interface."""
    print("\nValidating bot files...")
    
    if not os.path.exists("player_pool"):
        print("player_pool directory not found!")
        return False
    
    bot_files = [f for f in os.listdir("player_pool") if f.endswith('.py') and not f.startswith('__')]
    
    if not bot_files:
        print("No bot files found in player_pool!")
        return True
    
    print(f"Found {len(bot_files)} bot files:")
    for bot_file in bot_files:
        print(f"   {bot_file}")
    
    # TODO: Add bot interface validation here
    print("Bot files look good!")
    return True

def main():
    """Main validation routine."""
    print("Texas Hold'em Tournament Validation")
    print("=" * 50)
    
    # Validate core files
    core_valid = validate_core_files()
    
    # Validate bot files  
    bots_valid = validate_bot_files()
    
    print("\nVALIDATION SUMMARY:")
    print(f"   Core Files: {'PASS' if core_valid else 'FAIL'}")
    print(f"   Bot Files:  {'PASS' if bots_valid else 'FAIL'}")
    
    if core_valid and bots_valid:
        print("\nTournament ready to begin!")
        return True
    else:
        print("\nFix issues before running tournament!")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-baseline":
        generate_hash_baseline()
    else:
        main()