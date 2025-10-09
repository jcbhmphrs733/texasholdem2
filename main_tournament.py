# Texas Hold'em Bot Hackathon Tournament
from rich.console import Console
from game import TexasHoldemGame

# Import participant bots from player pool
from player_pool import get_all_bots, get_bot_summary

# Import ParentBot for fallback bots
from ParentBot import ParentBot
import random
from typing import Dict, Any, Tuple

console = Console()

# Tournament Configuration
STARTING_CHIPS = 500



def main():
    console.print("[bold blue]Welcome to Texas Hold'em Bot Hackathon![/bold blue]")
    console.print("Bots will compete in a tournament-style elimination game.")
    console.print(f"Starting chips: ${STARTING_CHIPS} each | Blinds: $5/$10")
    console.print("Press Enter after each action to continue...\n")
    
    # Get all participant bots from player pool
    participant_bots = get_all_bots(starting_chips=STARTING_CHIPS)
    
    if not participant_bots:
        console.print("[bold red]No participant bots found in player_pool directory![/bold red]")
        console.print("Please add bot .py files to the player_pool directory and restart.")
        return
    
    players = participant_bots
    
    # Display tournament information
    console.print(f"[bold green]Tournament Participants ({len(players)} bots):[/bold green]")
    for i, player in enumerate(players, 1):
        bot_type = player.__class__.__name__
        console.print(f"  {i}. {player.name} ({bot_type})")
    console.print()
    
    # Show bot summary from player pool
    summary = get_bot_summary()
    if "No participant bots found" not in summary:
        console.print("[bold cyan]Player Pool Summary:[/bold cyan]")
        console.print(summary)
    
    console.print(f"[bold magenta]Tournament Rules:[/bold magenta]")
    console.print(f"  - Starting chips: ${STARTING_CHIPS} per bot")
    console.print("  - Blinds: $5 small blind, $10 big blind") 
    console.print("  - Elimination: When a bot reaches $0 chips")
    console.print("  - Winner: Last bot standing")
    console.print("  - Press Enter between actions to continue\n")
    
    # Create tournament game
    game = TexasHoldemGame(players, small_blind=5, big_blind=10)
    
    hand_number = 1
    
    try:
        while len(game.players) > 1:
            console.print(f"[bold cyan]{'='*50}[/bold cyan]")
            console.print(f"[bold cyan]HAND #{hand_number}[/bold cyan]")
            console.print(f"[bold cyan]{'='*50}[/bold cyan]")
            
            # Display remaining players and their chip counts
            console.print("Remaining players:")
            for player in game.players:
                console.print(f"  {player.name}: ${player.chips}")
            
            input("Press Enter to start the hand...")
            
            # Start hand and check if game can continue
            if not game.start_hand():
                break
                
            game.play_hand()
            
            # Check if game should continue
            if len(game.players) <= 1:
                if len(game.players) == 1:
                    winner = game.players[0]
                    console.rule(f"[bold gold]TOURNAMENT WINNER: {winner.name} with ${winner.chips} chips![/bold gold]")
                else:
                    console.rule("[bold red]All players eliminated.[/bold red]")
                break
            
            hand_number += 1
            
            # Ask if user wants to continue
            continue_game = input("Continue to next hand? (Enter/y or 'q' to quit): ")
            if continue_game.lower() == 'q':
                break
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Tournament interrupted by user[/yellow]")
        
    # Show final standings
    console.print("\n[bold blue]Final Tournament Results:[/bold blue]")
    if game.players:
        sorted_players = sorted(game.players, key=lambda p: p.chips, reverse=True)
        for i, player in enumerate(sorted_players, 1):
            console.print(f"  {i}. {player.name}: ${player.chips}")
    
    console.print("\n[bold blue]Thanks for participating in the Texas Hold'em Bot Hackathon![/bold blue]")

if __name__ == "__main__":
    main()