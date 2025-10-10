# Tournament Analysis and Podium Display
"""
Post-tournament analysis display system.

Generates comprehensive tournament reports including:
- Podium ceremony for top finishers
- Detailed player analysis and statistics
- Interesting tournament facts and records
- Performance insights and patterns
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from typing import List, Dict, Any
from tournament_stats import TournamentStats

class TournamentAnalyzer:
    """
    Generates and displays comprehensive post-tournament analysis.
    """
    
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
        """Display overall tournament statistics combined with records."""
        summary = stats.get_tournament_summary()
        
        # Tournament Overview Section
        overview_table = Table(title="Tournament Overview", show_header=False)
        overview_table.add_column("Metric", style="cyan", width=25)
        overview_table.add_column("Value", style="white", width=30)
        
        overview_table.add_row("Total Hands Played", f"{summary['total_hands_played']}")
        overview_table.add_row("Total Players", f"{summary['total_players']}")
        overview_table.add_row("Biggest Pot", f"${summary['biggest_pot']} (won by {summary['biggest_pot_winner']})")
        overview_table.add_row("Average Pot Size", f"${summary['average_pot_size']}")
        
        self.console.print(overview_table)
        self.console.print()
        
        # Tournament Records Section
        best_hand = summary['best_hand_seen']
        
        records_table = Table(title="Tournament Records & Interesting Facts", show_header=True)
        records_table.add_column("Record", style="bold cyan", width=30)
        records_table.add_column("Details", style="white", width=40)
        
        # Only show best hand if there is one
        if best_hand and 'player' in best_hand:
            records_table.add_row(
                "Best Hand Seen",
                f"{best_hand['description']} by {best_hand['player']}"
            )
            
            if best_hand.get('hole_cards'):
                hole_cards_str = " ".join(best_hand['hole_cards'])
                community_cards_str = " ".join(best_hand['community_cards'])
                records_table.add_row(
                    "   Hole Cards",
                    hole_cards_str
                )
                records_table.add_row(
                    "   Community Cards", 
                    community_cards_str
                )
        else:
            records_table.add_row(
                "Best Hand Seen",
                "No completed showdowns yet"
            )
        
        records_table.add_row(
            "Biggest Pot",
            f"${summary['biggest_pot']} won by {summary['biggest_pot_winner']}" if summary['biggest_pot_winner'] else "No pots won yet"
        )
        records_table.add_row(
            "Most Aggressive",
            summary['most_aggressive_player']
        )
        records_table.add_row(
            "Most Conservative",
            summary['most_conservative_player']
        )
        
        self.console.print(records_table)
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
        
        # Create main stats table
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Stat", style="cyan", width=20)
        stats_table.add_column("Value", style="white", width=15)
        stats_table.add_column("Stat", style="cyan", width=20)
        stats_table.add_column("Value", style="white", width=15)
        
        # Performance metrics
        stats_table.add_row(
            "Final Position", f"#{analysis['final_position']}",
            "Hands Played", f"{analysis['hands_played']}"
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
        
        # Display the table first
        self.console.print(f"\n[bold]{name}[/bold] - Position #{position}")
        self.console.print(stats_table)
        
        # Behavioral analysis (if available)
        behavior_stats = []
        if 'fold_frequency' in analysis:
            behavior_stats.extend([
                f"Fold Frequency: {analysis['fold_frequency']:.1%}",
                f"Aggression Rate: {analysis['aggression_frequency']:.1%}",
                f"Pre-flop Fold Rate: {analysis['pre_flop_fold_rate']:.1%}",
                f"Showdown Frequency: {analysis['showdown_frequency']:.1%}"
            ])
            
            if analysis['average_raise_amount'] > 0:
                behavior_stats.append(f"Avg Raise Amount: ${analysis['average_raise_amount']:.0f}")
        
        # Display behavioral analysis
        if behavior_stats:
            self.console.print(f"\n[bold cyan]Playing Style:[/bold cyan]")
            for stat in behavior_stats:
                self.console.print(f"  {stat}")
        
        # Strongest hand
        self.console.print(f"\n[bold green]Best Hand:[/bold green] {analysis['strongest_hand']}")
        
        # Add separator line
        self.console.rule("[bold green][/bold green]")
        self.console.print()