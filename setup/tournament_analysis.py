# Tournament Analysis and Podium Display

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from typing import List, Dict, Any
from .tournament_stats import TournamentStats
from .tournament_ui import cards_to_pretty_str, card_to_pretty_str
from treys import Card

class TournamentAnalyzer:
    """Generates and displays comprehensive post-tournament analysis."""
    
    def __init__(self, console: Console):
        """Initialize the tournament analyzer."""
        self.console = console
    
    def display_podium(self, final_players: List[Any]):
        """Display podium ceremony for top finishers."""
        # Podium removed - using final results display instead
        pass
    
    def display_comprehensive_analysis(self, stats: TournamentStats, final_players: List[Any]):
        """Display comprehensive tournament analysis."""
        self.console.rule("[bold blue]COMPREHENSIVE TOURNAMENT ANALYSIS[/bold blue]")
        
        # Tournament Overview with Records
        self._display_tournament_overview_with_records(stats)
        
        # Individual Player Analysis for ALL players
        self._display_all_player_analyses(stats, final_players)
    
    def _display_tournament_overview_with_records(self, stats: TournamentStats):
        """Display comprehensive tournament summary combining overview and records."""
        summary = stats.get_tournament_summary()
        best_hand = summary['best_hand_seen']
        
        # Combined Tournament Summary Table
        summary_table = Table(title="Tournament Summary", show_header=False)
        summary_table.add_column("Metric", style="cyan", width=25)
        summary_table.add_column("Value", style="white", width=50)
        
        # Basic tournament metrics
        summary_table.add_row("Total Hands Played", f"{summary['total_hands_played']}")
        summary_table.add_row("Total Players", f"{summary['total_players']}")
        summary_table.add_row("Average Pot Size", f"${summary['average_pot_size']}")
        
        # Tournament records
        summary_table.add_row("Biggest Pot", f"${summary['biggest_pot']} (won by {summary['biggest_pot_winner']})" if summary['biggest_pot_winner'] else "No pots won yet")
        
        # Best hand information
        if best_hand and 'player' in best_hand:
            summary_table.add_row("Best Hand Seen", f"{best_hand['description']} by {best_hand['player']}")
            
            if best_hand.get('hole_cards'):
                # Convert card strings back to integers and display with colors
                hole_card_ints = [Card.new(card_str) for card_str in best_hand['hole_cards']]
                community_card_ints = [Card.new(card_str) for card_str in best_hand['community_cards']]
                
                hole_cards_str = cards_to_pretty_str(hole_card_ints)
                community_cards_str = cards_to_pretty_str(community_card_ints)
                
                summary_table.add_row("   Hole Cards", hole_cards_str)
                summary_table.add_row("   Community Cards", community_cards_str)
        else:
            summary_table.add_row("Best Hand Seen", "No completed showdowns yet")
        
        # Playing style insights
        summary_table.add_row("Most Aggressive Player", summary['most_aggressive_player'])
        summary_table.add_row("Most Conservative Player", summary['most_conservative_player'])

        self.console.print(summary_table)
        self.console.print()
    
    def _display_all_player_analyses(self, stats: TournamentStats, final_players: List[Any]):
        """Display detailed analysis for all players who participated in the tournament."""
        self.console.rule("[bold green]Individual Player Analysis[/bold green]")
        
        # Get all player names from stats (includes eliminated players)
        all_player_names = stats.get_all_player_names()
        
        # Create a lookup for final players to get current chip counts
        final_player_lookup = {player.name: player for player in final_players}
        
        # Sort all players by their final position (already set in stats)
        all_analyses = []
        for player_name in all_player_names:
            analysis = stats.get_player_analysis(player_name)
            if 'error' not in analysis:
                all_analyses.append(analysis)
        
        # Sort by final position
        sorted_analyses = sorted(all_analyses, key=lambda x: x['final_position'])
        
        for analysis in sorted_analyses:
            self._display_single_player_analysis(analysis, analysis['final_position'])

    def _display_player_analyses(self, stats: TournamentStats, final_players: List[Any]):
        """Display detailed analysis for each player."""
        self.console.rule("[bold green]Individual Player Analysis[/bold green]")
        
        # Sort players by final position
        sorted_players = sorted(final_players, key=lambda p: p.chips, reverse=True)
        
        for i, player in enumerate(sorted_players, 1):
            analysis = stats.get_player_analysis(player.name)
            
            if 'error' in analysis:
                continue
            
            # Create player panel
            self._display_single_player_analysis(analysis, i)
    
    def _display_single_player_analysis(self, analysis: Dict[str, Any], position: int):
        """Display analysis for a single player."""
        name = analysis['name']
        # Add separator line with player name announcement
        self.console.rule(f"[bold green]{name}[/bold green]")
        # Create main stats table
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Stat", style="cyan", width=20)
        stats_table.add_column("Value", style="white", width=15)
        stats_table.add_column("Stat", style="cyan", width=20)
        stats_table.add_column("Value", style="white", width=15)
        
        # Performance metrics
        stats_table.add_row(
            "Hands Played", f"{analysis['hands_played']}",
            "Hands Won", f"{analysis['hands_won']}"
        )
        stats_table.add_row(
            "Hands Won", f"{analysis['hands_won']}",
            "Win Rate", f"{analysis['win_rate']:.1%}"
        )
        stats_table.add_row(
            "Total Winnings", f"${analysis['total_winnings']:,}",
            "Total Invested", f"${analysis['total_invested']:,}"
        )
        stats_table.add_row(
            "Net Profit", f"${analysis['net_profit']:,}",
            "ROI", f"{analysis['roi']:.1f}%"
        )
        stats_table.add_row(
            "Chip Change", f"{analysis['chip_change']:+,}",
            "Biggest Pot Won", f"${analysis['biggest_pot_won']:,}"
        )
        
        self.console.print(stats_table)
        
        if 'fold_frequency' in analysis:
            self.console.print(f"\n[bold cyan]Playing Style:[/bold cyan]")
            self.console.print(f"  Fold: {analysis['fold_frequency']:.1%} | Aggression: {analysis['aggression_frequency']:.1%} | Pre-flop Fold: {analysis['pre_flop_fold_rate']:.1%}")
            if analysis['average_raise_amount'] > 0:
                self.console.print(f"  Avg Raise: ${analysis['average_raise_amount']:.0f} | Showdowns: {analysis['showdown_frequency']:.1%}")
        
        self.console.print(f"\n[bold green]Best Hand:[/bold green] {analysis['strongest_hand']}")
        self.console.print()