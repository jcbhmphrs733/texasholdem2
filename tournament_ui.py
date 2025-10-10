# Tournament UI - User Interface for Texas Hold'em Tournament
"""
Tournament User Interface Module

This module handles all the visual presentation and user interaction for the tournament.
Game logic is kept separate in game.py to allow participants to study pure game mechanics.
"""

import os
from rich.console import Console
from rich.table import Table
from rich.rule import Rule
from treys import Card
from typing import List, Dict, Any, Optional
import configure_tournament as config

console = Console()

class TournamentUI:
    """
    Handles all user interface and display logic for the tournament.
    
    Separates presentation from game logic to keep game.py clean for participants
    to study and understand the core poker mechanics.
    """
    
    def __init__(self):
        """Initialize UI with tournament configuration."""
        self.console = console
    
    def clear_screen(self):
        """Clear the console screen for clean display."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """Display tournament welcome message and configuration."""
        self.console.print("[bold blue]Welcome to Texas Hold'em Bot Hackathon![/bold blue]")
        self.console.print("Bots will compete in a tournament-style elimination game.")
        self.console.print(f"Starting chips: ${config.STARTING_CHIPS} each | Blinds: ${config.SMALL_BLIND_INITIAL}/${config.BIG_BLIND_INITIAL}")
        
        # Display blind increase schedule if enabled
        if config.BLIND_INCREASE_FREQUENCY > 0:
            self.console.print(f"Blinds increase by {config.BLIND_INCREASE_FACTOR}x every {config.BLIND_INCREASE_FREQUENCY} hands")
        
        self.console.print("Press Enter after each action to continue...\n")
    
    def display_no_bots_error(self):
        """Display error when no participant bots are found."""
        self.console.print("[bold red]No participant bots found in player_pool directory![/bold red]")
        self.console.print("Please add bot .py files to the player_pool directory and restart.")
    
    def display_insufficient_players_error(self, num_players: int):
        """Display error when not enough players for tournament."""
        self.console.print(f"[bold red]Insufficient players for tournament![/bold red]")
        self.console.print(f"Found {num_players} bots, but need at least {config.MIN_PLAYERS} players.")
        self.console.print("Please add more bot .py files to the player_pool directory.")
    
    def display_too_many_players_error(self, num_players: int):
        """Display error when too many players for tournament."""
        self.console.print(f"[bold yellow]Too many players for tournament![/bold yellow]")
        self.console.print(f"Found {num_players} bots, but maximum is {config.MAX_PLAYERS} players.")
        self.console.print("Only the first {config.MAX_PLAYERS} bots will participate.")
    
    def display_tournament_participants(self, players: List[Any]):
        """Display list of tournament participants."""
        self.console.print(f"[bold green]Tournament Participants ({len(players)} bots):[/bold green]")
        for i, player in enumerate(players, 1):
            bot_type = player.__class__.__name__
            self.console.print(f"  {i}. {player.name} ({bot_type})")
        self.console.print()
    
    def display_player_pool_summary(self, summary: str):
        """Display player pool summary if bots were found."""
        if "No participant bots found" not in summary:
            self.console.print("[bold cyan]Player Pool Summary:[/bold cyan]")
            self.console.print(summary)
    
    def display_tournament_rules(self, current_small_blind: int, current_big_blind: int):
        """Display tournament rules with current blind levels."""
        self.console.print(f"[bold magenta]Tournament Rules:[/bold magenta]")
        self.console.print(f"  - Starting chips: ${config.STARTING_CHIPS} per bot")
        self.console.print(f"  - Current blinds: ${current_small_blind} small blind, ${current_big_blind} big blind")
        
        if config.BLIND_INCREASE_FREQUENCY > 0:
            self.console.print(f"  - Blind increases: {config.BLIND_INCREASE_FACTOR}x every {config.BLIND_INCREASE_FREQUENCY} hands")
        
        self.console.print("  - Elimination: When a bot reaches $0 chips")
        self.console.print("  - Winner: Last bot standing")
        self.console.print(f"  - Players: {config.MIN_PLAYERS}-{config.MAX_PLAYERS} participants")
        self.console.print("  - Press Enter between actions to continue\n")
    
    def display_hand_header(self, hand_number: int, small_blind: int, big_blind: int):
        """Display hand number and current blind levels."""
        self.console.print(f"[bold cyan]{'='*50}[/bold cyan]")
        self.console.print(f"[bold cyan]HAND #{hand_number} | Blinds: ${small_blind}/${big_blind}[/bold cyan]")
        self.console.print(f"[bold cyan]{'='*50}[/bold cyan]")
    
    def display_remaining_players(self, players: List[Any], big_blind: int):
        """Display remaining players and their chip counts with BB ratios."""
        self.console.print("Remaining players:")
        for player in players:
            bb_ratio = player.chips / big_blind if big_blind > 0 else 0
            self.console.print(f"  {player.name}: ${player.chips} ({bb_ratio:.1f} BB)")
    
    def display_elimination(self, player_name: str, chips: int):
        """Display player elimination message."""
        self.console.print(f"[bold red]{player_name} has been eliminated with ${chips} chips![/bold red]")
    
    def display_tournament_winner(self, winner_name: str, chips: int):
        """Display tournament winner announcement."""
        self.console.rule(f"[bold gold]TOURNAMENT WINNER: {winner_name} with ${chips} chips![/bold gold]")
    
    def display_all_eliminated(self):
        """Display message when all players are eliminated."""
        self.console.rule("[bold red]All players eliminated.[/bold red]")
    
    def display_tournament_interrupted(self):
        """Display message when tournament is interrupted."""
        self.console.print("\n[yellow]Tournament interrupted by user[/yellow]")
    
    def display_final_standings(self, players: List[Any]):
        """Display final tournament standings."""
        self.console.print("\n[bold blue]Final Tournament Results:[/bold blue]")
        if players:
            sorted_players = sorted(players, key=lambda p: p.chips, reverse=True)
            for i, player in enumerate(sorted_players, 1):
                self.console.print(f"  {i}. {player.name}: ${player.chips}")
    
    def display_thanks(self):
        """Display final thank you message."""
        self.console.print("\n[bold blue]Thanks for participating in the Texas Hold'em Bot Hackathon![/bold blue]")
    
    def prompt_start_hand(self):
        """Prompt user to start the hand."""
        input("Press Enter to start the hand...")
    
    def prompt_continue_tournament(self):
        """Prompt user to continue tournament or quit."""
        if config.AUTO_CONTINUE_DELAY > 0:
            return ""  # Auto-continue without prompting
        return input("Continue to next hand? (Enter/y or 'q' to quit): ")
    
    def prompt_elimination_continue(self, player_name: str):
        """Prompt user to continue after player elimination."""
        input(f"Press Enter to continue after {player_name}'s elimination...")
    
    # Game State Display Methods
    
    def display_persistent_game_state(self, players: List[Any], round_name: str, 
                                    community_cards: List[int], pot: int, 
                                    current_bet: int, dealer_pos: int):
        """Display the persistent game state that stays at the top of the screen."""
        
        # 1. GAME-WIDE STATE: Display all players table first (most persistent)
        table = Table(title="All Players")
        table.add_column("Position", style="yellow")
        table.add_column("Name", style="cyan")
        table.add_column("Hole Cards", style="green")
        table.add_column("Chips", style="white")
        table.add_column("Current Bet", style="blue")
        table.add_column("Status", style="white")
        
        # Calculate positions
        sb_pos = (dealer_pos + 1) % len(players)
        bb_pos = (dealer_pos + 2) % len(players)
        
        for i, player in enumerate(players):
            # Determine position
            position = ""
            if i == dealer_pos:
                position = "[bold yellow]D[/bold yellow]"  # Dealer
            elif i == sb_pos:
                position = "[bold blue]SB[/bold blue]"    # Small Blind
            elif i == bb_pos:
                position = "[bold red]BB[/bold red]"      # Big Blind
            else:
                position = "[dim]--[/dim]"               # Regular position
            
            status = []
            if player.folded:
                status.append("[red]Folded[/red]")
            if player.all_in:
                status.append("[magenta]All-in[/magenta]")
            if not status:
                status.append("[green]Active[/green]")
            
            # Format hole cards - show them if player has cards and hasn't folded
            if player.hand and not player.folded:
                hole_cards = " ".join([Card.int_to_str(card) for card in player.hand])
            elif player.folded:
                hole_cards = "[dim]Folded[/dim]"
            else:
                hole_cards = "[dim]--[/dim]"
            
            table.add_row(
                position,
                player.name,
                hole_cards,
                f"${player.chips}",
                f"${player.current_bet}",
                " ".join(status)
            )
        
        self.console.print(table)
        self.console.print()  # Add spacing
        
        # 2. HAND-WIDE STATE: Display stage header and community cards
        self.console.print(f"[bold cyan]=== {round_name} ===[/bold cyan]")
        
        # Display community cards table
        if community_cards:
            stage = len(community_cards)
            if stage == 3:
                stage_name = "Flop"
            elif stage == 4:
                stage_name = "Turn"
            elif stage == 5:
                stage_name = "River"
            else:
                stage_name = "Community Cards"
            
            community_str = " ".join([Card.int_to_str(card) for card in community_cards])
            community_table = Table(title="Community Cards")
            community_table.add_column(stage_name, style="green", justify="center")
            community_table.add_row(community_str)
        else:
            community_table = Table(title="Community Cards")
            community_table.add_column("Pre-flop", style="dim", justify="center")
            community_table.add_row("[dim]None dealt yet[/dim]")
        
        self.console.print(community_table)
        
        # Display pot and current bet
        self.console.print(f"Pot: [yellow]${pot}[/yellow] | Current bet: [red]${current_bet}[/red]")
        self.console.print()  # Add spacing before individual player actions
    
    def display_betting_round_header(self, round_name: str):
        """Display betting round header."""
        self.console.rule(f"[bold green]--- {round_name} Betting Round ---[/bold green]")
    
    def display_player_action_table(self, player: Any):
        """Display player's current situation for decision making."""
        action_table = Table(title=f"{player.name}'s Turn")
        action_table.add_column("Info", style="cyan")
        action_table.add_column("Value", style="white")
        
        hand_str = ' '.join([Card.int_to_str(card) for card in player.hand])
        
        action_table.add_row("Hand", f"[green]{hand_str}[/green]")
        action_table.add_row("Chips", f"[yellow]${player.chips}[/yellow]")
        action_table.add_row("Current Bet", f"[blue]${player.current_bet}[/blue]")
        
        self.console.print(action_table)
    
    def display_player_action_result(self, player_name: str, action: str, amount: int):
        """Display the result of a player's action."""
        result_table = Table(title="Action")
        result_table.add_column("Player", style="cyan")
        result_table.add_column("Decision", style="bold")
        result_table.add_column("Amount", style="yellow")
        
        if action == 'fold':
            result_table.add_row(player_name, "[yellow]FOLDS[/yellow]", "--")
        elif action == 'check':
            result_table.add_row(player_name, "[cyan]CHECKS[/cyan]", "--")
        elif action == 'call':
            result_table.add_row(player_name, "[blue]CALLS[/blue]", f"${amount}")
        elif action == 'call_all_in':
            result_table.add_row(player_name, "[magenta]CALLS ALL-IN[/magenta]", f"${amount}")
        elif action == 'raise':
            result_table.add_row(player_name, "[bold green]RAISES[/bold green]", f"${amount}")
        elif action == 'raise_all_in':
            result_table.add_row(player_name, "[magenta]RAISES ALL-IN[/magenta]", f"${amount}")
        elif action == 'invalid_check':
            result_table.add_row(player_name, "[red]INVALID CHECK[/red]", "--")
        elif action == 'invalid_raise':
            result_table.add_row(player_name, "[red]INVALID RAISE[/red]", f"${amount}")
        
        self.console.print(result_table)
    
    def display_invalid_action_message(self, message: str):
        """Display invalid action message."""
        self.console.print(f"[red]{message}[/red]")
    
    def prompt_action_continue(self, player_name: str):
        """Prompt to continue after player action."""
        input(f"Press Enter to continue after {player_name}'s action...")
    
    def display_showdown_header(self):
        """Display showdown header."""
        self.console.print("[bold green]--- Showdown ---[/bold green]")
    
    def display_showdown_results(self, active_players: List[Any], scores: List[tuple], evaluator):
        """Display showdown hand rankings."""
        table = Table(title="Showdown Results")
        table.add_column("Player", style="cyan")
        table.add_column("Hand")
        table.add_column("Rank", style="magenta")
        
        for player, score in scores:
            hand_class = evaluator.class_to_string(evaluator.get_rank_class(score))
            table.add_row(
                player.name,
                " ".join([Card.int_to_str(card) for card in player.hand]),
                hand_class
            )
        
        self.console.print(table)
    
    def display_hand_winner(self, winner_name: str, prize: int, hand_class: str):
        """Display hand winner announcement."""
        self.console.print(f"[bold yellow]{winner_name} wins {prize} chips with {hand_class}[/bold yellow]")
    
    def display_community_cards_header(self, round_name: str):
        """Display community cards dealing header."""
        self.console.print(f"[bold]=== {round_name} ===[/bold]")