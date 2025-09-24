# Texas Hold'em Simulator with Bot Framework
from rich.console import Console
from bot import AggressiveBot
from game import TexasHoldemGame

console = Console()

def main():
    console.print("[bold blue]Welcome to Texas Hold'em Bot Simulator![/bold blue]")
    console.print("Four bots will compete: Alice (Aggressive), Bob (Random), Claire (Aggressive), David (Random)")
    console.print("Starting chips: $500 each")
    console.print("Press Enter after each action to continue...\n")
    
    # Create the four bots with different strategies
    alice = AggressiveBot("Alice", chips=500)
    bob = AggressiveBot("Bob", chips=500)  
    claire = AggressiveBot("Claire", chips=500)
    david = AggressiveBot("David", chips=500)
    
    players = [alice, bob, claire, david]
    
    # Create game with appropriate blinds for starting stack
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
            
            game.play_hand()
            
            # Check if game should continue
            if len(game.players) <= 1:
                if len(game.players) == 1:
                    winner = game.players[0]
                    console.rule(f"[bold gold] GAME OVER {winner.name} wins with ${winner.chips} chips.[/bold gold]")
                else:
                    console.rule("[bold red]All players eliminated.[/bold red]")
                break
            
            hand_number += 1
            
            # Ask if user wants to continue
            continue_game = input("Continue to next hand? (Enter/y or 'q' to quit): ")
            if continue_game.lower() == 'q':
                break
                
    except KeyboardInterrupt:
        console.print("[yellow]Simulation interrupted by user[/yellow]")
        
    console.print("[bold blue]Thanks for watching the Texas Hold'em simulation![/bold blue]")

if __name__ == "__main__":
    main()