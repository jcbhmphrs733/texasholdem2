#!/usr/bin/env python3
"""
Security setup script for Texas Hold'em Bot Hackathon
Sets appropriate file permissions to protect core game files
"""

import os
import stat
import platform

def set_file_readonly(filepath):
    """Set a file to read-only permissions."""
    if os.path.exists(filepath):
        if platform.system() == "Windows":
            # Windows: Remove write permissions
            os.chmod(filepath, stat.S_IREAD)
        else:
            # Unix/Linux/Mac: Set to read-only for user, group, other
            os.chmod(filepath, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        print(f"Protected: {filepath}")
    else:
        print(f"File not found: {filepath}")

def set_file_writable(filepath):
    """Set a file to read-write permissions."""
    if os.path.exists(filepath):
        if platform.system() == "Windows":
            # Windows: Add write permissions
            os.chmod(filepath, stat.S_IREAD | stat.S_IWRITE)
        else:
            # Unix/Linux/Mac: Set to read-write for user, read for others
            os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        print(f"Writable: {filepath}")
    else:
        print(f"File not found: {filepath}")

def secure_repository():
    """Apply security settings to the repository."""
    print("Securing Texas Hold'em Bot Hackathon Repository")
    print("=" * 60)
    
    # Core game files - make read-only
    protected_files = [
        "game_logic.py",
        "ParentBot.py", 
        "main_tournament.py",
        "tournament_ui.py",
        "tournament_stats.py",
        "tournament_analysis.py",
        "configure_tournament.py",
        "get_participants.py"
    ]
    
    print("\nProtecting core game files (READ-ONLY):")
    for filename in protected_files:
        set_file_readonly(filename)
    
    # Participant files - ensure they're writable
    participant_files = [
        "template.py",
        "dojo.py",
        "README.md",
        "DOJO_README.md"
    ]
    
    print("\nEnsuring participant files are writable:")
    for filename in participant_files:
        set_file_writable(filename)
    
    # Player pool directory - ensure it's writable
    player_pool_dir = "player_pool"
    if os.path.exists(player_pool_dir):
        print(f"\nEnsuring {player_pool_dir} directory is writable:")
        if platform.system() == "Windows":
            os.chmod(player_pool_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        else:
            os.chmod(player_pool_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        print(f"Directory permissions set: {player_pool_dir}")
        
        # Make existing bot files writable (participants may want to modify)
        for filename in os.listdir(player_pool_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(player_pool_dir, filename)
                set_file_writable(filepath)
    
    print("\nRepository security setup complete!")
    print("\nSecurity Summary:")
    print("   Protected files: Core game logic cannot be modified")
    print("   Participant files: Template, dojo, and bots can be modified")
    print("   Player pool: Full access for bot development")
    
    print("\nNote: Participants can still VIEW protected files for learning!")

if __name__ == "__main__":
    secure_repository()