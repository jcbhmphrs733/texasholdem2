#!/usr/bin/env python3
"""
Bot Testing Dojo - Simple bot validation and tuning tool

A lightweight testing environment for validating poker bot behavior against
expected outcomes in common scenarios. Helps ensure bots make reasonable
decisions across different game situations.

Usage:
    python dojo.py BotName
    
Example:
    python dojo.py Coyote
"""

import sys
import os
import importlib
from typing import Dict, Any, List
from treys import Card
from rich.console import Console
from rich.table import Table

# Add parent directory to path for game_logic and other imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Add player_pool to path for bot imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'player_pool'))

console = Console()

class BotTester:
    """Simple bot testing and validation."""
    
    def __init__(self):
        """Initialize the tester with predefined scenarios."""
        self.test_scenarios = [
            {
                "name": "Premium Hand Pre-flop",
                "hole_cards": ['As', 'Ah'],
                "community_cards": [],
                "game_state": {
                    'current_bet': 20,
                    'player_bet': 0,
                    'min_raise': 20,
                    'pot': 30,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "raise"
            },
            {
                "name": "Strong Hand Value Bet",
                "hole_cards": ['As', 'Kd'],
                "community_cards": ['Ah', '7c', '3s'],
                "game_state": {
                    'current_bet': 0,
                    'player_bet': 0,
                    'min_raise': 20,
                    'pot': 50,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "raise"
            },
            {
                "name": "Drawing Hand Decision",
                "hole_cards": ['Kh', 'Qh'],
                "community_cards": ['Jh', '9s', '2c'],
                "game_state": {
                    'current_bet': 30,
                    'player_bet': 0,
                    'min_raise': 30,
                    'pot': 60,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "call"
            },
            {
                "name": "Weak Hand Fold",
                "hole_cards": ['7h', '2s'],
                "community_cards": ['Kc', 'Qd', 'Js'],
                "game_state": {
                    'current_bet': 50,
                    'player_bet': 0,
                    'min_raise': 50,
                    'pot': 80,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "fold"
            },
            {
                "name": "Made Hand River Value",
                "hole_cards": ['As', 'Ah'],
                "community_cards": ['Kd', 'Qc', '7h', '3s', '2h'],
                "game_state": {
                    'current_bet': 0,
                    'player_bet': 0,
                    'min_raise': 20,
                    'pot': 120,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "raise"
            },
            {
                "name": "Suited Connectors Pre-flop",
                "hole_cards": ['8s', '7s'],
                "community_cards": [],
                "game_state": {
                    'current_bet': 20,
                    'player_bet': 0,
                    'min_raise': 20,
                    'pot': 30,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "call"
            },
            {
                "name": "Pocket Pair vs Overcard",
                "hole_cards": ['Jh', 'Js'],
                "community_cards": ['Kc', '9d', '4h'],
                "game_state": {
                    'current_bet': 40,
                    'player_bet': 0,
                    'min_raise': 40,
                    'pot': 70,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "call"
            },
            {
                "name": "Flush Draw on Turn",
                "hole_cards": ['Ad', '6d'],
                "community_cards": ['Kd', '9d', '4h', '2s'],
                "game_state": {
                    'current_bet': 60,
                    'player_bet': 0,
                    'min_raise': 60,
                    'pot': 100,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "call"
            },
            {
                "name": "Trash Hand Pre-flop",
                "hole_cards": ['9h', '3c'],
                "community_cards": [],
                "game_state": {
                    'current_bet': 60,
                    'player_bet': 0,
                    'min_raise': 60,
                    'pot': 90,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "fold"
            },
            {
                "name": "Two Pair Value Bet",
                "hole_cards": ['Ah', '8c'],
                "community_cards": ['As', '8h', '3d', '7s'],
                "game_state": {
                    'current_bet': 0,
                    'player_bet': 0,
                    'min_raise': 20,
                    'pot': 80,
                    'small_blind': 10,
                    'big_blind': 20,
                    'players': []
                },
                "expected_action": "raise"
            }
        ]
    
    def load_bot(self, bot_name: str):
        """Load a bot class by name."""
        try:
            module = importlib.import_module(bot_name)
            bot_class = getattr(module, bot_name)
            return bot_class
        except ImportError:
            console.print(f"[red]Error: Could not import bot '{bot_name}'[/red]")
            console.print(f"Make sure {bot_name}.py exists in the player_pool directory")
            return None
        except AttributeError:
            console.print(f"[red]Error: No class '{bot_name}' found in {bot_name}.py[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading bot: {e}[/red]")
            return None
    
    def run_test_scenario(self, bot_instance, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario and return results."""
        # Set up bot with hole cards
        hole_cards = [Card.new(card) for card in scenario["hole_cards"]]
        community_cards = [Card.new(card) for card in scenario["community_cards"]]
        
        bot_instance.hand = hole_cards
        
        # Prepare game state
        game_state = scenario["game_state"].copy()
        game_state['community_cards'] = community_cards
        
        try:
            # Get bot decision
            action, amount = bot_instance.decide_action(game_state)
            
            # Get hand strength if available
            hand_strength = None
            if hasattr(bot_instance, 'get_hand_strength'):
                try:
                    hand_strength = bot_instance.get_hand_strength()
                except:
                    pass
            
            # Check if decision matches expectation
            expected = scenario["expected_action"]
            matches_expected = action.lower() == expected.lower()
            
            return {
                "scenario_name": scenario["name"],
                "hole_cards": scenario["hole_cards"],
                "community_cards": scenario["community_cards"],
                "expected_action": expected,
                "actual_action": action,
                "amount": amount,
                "matches_expected": matches_expected,
                "hand_strength": hand_strength
            }
            
        except Exception as e:
            return {
                "scenario_name": scenario["name"],
                "hole_cards": scenario["hole_cards"],
                "community_cards": scenario["community_cards"],
                "expected_action": scenario["expected_action"],
                "actual_action": "ERROR",
                "amount": 0,
                "matches_expected": False,
                "hand_strength": None
            }
    
    def test_bot(self, bot_name: str):
        """Test a bot against all scenarios and display results."""
        console.print(f"[bold blue]Testing Bot: {bot_name}[/bold blue]\n")
        
        # Load bot
        bot_class = self.load_bot(bot_name)
        if not bot_class:
            return
        
        # Create bot instance (try different constructor patterns)
        try:
            bot_instance = bot_class(bot_name)
        except TypeError:
            # Fallback for bots that still expect chips parameter
            try:
                bot_instance = bot_class(bot_name, 1000)
            except TypeError:
                # Last resort - default constructor
                bot_instance = bot_class()
        
        # Run all scenarios
        results = []
        for scenario in self.test_scenarios:
            result = self.run_test_scenario(bot_instance, scenario)
            results.append(result)
        
        # Display results
        self.display_results(bot_name, results)
        
        # Summary
        self.display_summary(results)
    
    def display_results(self, bot_name: str, results: List[Dict[str, Any]]):
        """Display test results in a table."""
        table = Table(title=f"{bot_name} Test Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Hole Cards", style="green")
        table.add_column("Board", style="blue")
        table.add_column("Expected", style="yellow")
        table.add_column("Actual", style="white")
        table.add_column("Match", style="bold")
        table.add_column("Hand Strength", style="magenta")
        
        for result in results:
            # Format cards
            hole_str = " ".join(result["hole_cards"])
            board_str = " ".join(result["community_cards"]) if result["community_cards"] else "Pre-flop"
            
            # Format action
            actual_str = result["actual_action"].upper()
            if result["amount"] > 0:
                actual_str += f" ${result['amount']}"
            
            # Match status
            match_str = "[green]YES[/green]" if result["matches_expected"] else "[red]NO[/red]"
            
            # Hand strength
            strength_str = f"{result['hand_strength']:.3f}" if result["hand_strength"] is not None else "N/A"
            
            table.add_row(
                result["scenario_name"],
                hole_str,
                board_str,
                result["expected_action"].upper(),
                actual_str,
                match_str,
                strength_str
            )
        
        console.print(table)
    
    def display_summary(self, results: List[Dict[str, Any]]):
        """Display test summary and analysis."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["matches_expected"])
        
        console.print(f"\n[bold]Test Summary:[/bold]")
        console.print(f"Total Tests: {total_tests}")
        console.print(f"Passed: {passed_tests}")
        console.print(f"Failed: {total_tests - passed_tests}")
        console.print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Performance assessment
        if passed_tests == total_tests:
            console.print("[bold green]EXCELLENT: Bot passed all tests![/bold green]")
        elif passed_tests >= total_tests * 0.8:
            console.print("[bold yellow]GOOD: Bot shows solid strategic understanding[/bold yellow]")
        elif passed_tests >= total_tests * 0.6:
            console.print("[bold yellow]FAIR: Bot needs some strategic adjustments[/bold yellow]")
        else:
            console.print("[bold red]POOR: Bot requires significant strategy improvements[/bold red]")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        console.print("[bold red]Usage: python dojo.py <BotName>[/bold red]")
        console.print("\nExample: python dojo.py Coyote")
        console.print("\nAvailable bots:")
        
        # List available bots
        player_pool_dir = os.path.join(os.path.dirname(__file__), 'player_pool')
        if os.path.exists(player_pool_dir):
            for filename in os.listdir(player_pool_dir):
                if filename.endswith('.py') and not filename.startswith('__'):
                    bot_name = filename[:-3]
                    console.print(f"  - {bot_name}")
        return
    
    bot_name = sys.argv[1]
    tester = BotTester()
    tester.test_bot(bot_name)


if __name__ == "__main__":
    main()