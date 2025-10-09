# Texas Hold'em Game Logic
import os
import time
from treys import Card, Evaluator, Deck
from rich.table import Table
from rich.console import Console

console = Console()

class TexasHoldemGame:
    def __init__(self, players, small_blind=10, big_blind=20):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_pos = 0
        self.evaluator = Evaluator()
        self.hand_history = []
    
    def start_hand(self):
        # Clear screen for new hand
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Remove bankrupt players at the start of the hand
        bankrupt_players = [player for player in self.players if player.chips <= 0]
        for player in bankrupt_players:
            print(f"{player.name} has been eliminated with ${player.chips} chips!")
            self.players.remove(player)
            input(f"Press Enter to continue after {player.name}'s elimination...")
        
        if len(self.players) <= 1:
            return False  # Game over
        
        # Adjust dealer position if needed after eliminations
        if self.dealer_pos >= len(self.players):
            self.dealer_pos = 0
        
        # Reset game state
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        
        # Reset players
        for player in self.players:
            player.reset_for_new_hand()
        
        # Post blinds
        sb_pos = (self.dealer_pos + 1) % len(self.players)
        bb_pos = (self.dealer_pos + 2) % len(self.players)
        
        # Small blind
        sb_amount = min(self.small_blind, self.players[sb_pos].chips)
        self.players[sb_pos].chips -= sb_amount
        self.players[sb_pos].current_bet = sb_amount
        
        # Big blind
        bb_amount = min(self.big_blind, self.players[bb_pos].chips)
        self.players[bb_pos].chips -= bb_amount
        self.players[bb_pos].current_bet = bb_amount
        
        self.pot = sb_amount + bb_amount
        self.current_bet = max(sb_amount, bb_amount)
        
        # Deal cards
        for player in self.players:
            card1 = self.deck.draw(1)[0]  # draw(1) returns a list, get first element
            card2 = self.deck.draw(1)[0]
            player.receive_cards([card1, card2])
        
        self.display_persistent_game_state("Pre-flop")
        return True  # Hand started successfully
    
    def betting_round(self, round_name):
        console.rule(f"[bold green]--- {round_name} Betting Round ---[/bold green]")
        
        # Clear screen for clean betting round display
        if round_name != "Pre-flop":  # Don't clear on pre-flop as it's already cleared from start_hand
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_persistent_game_state(round_name)
        
        # Determine starting position based on betting round
        if round_name == "Pre-flop":
            # Pre-flop: Start with player after big blind (UTG)
            start_pos = (self.dealer_pos + 3) % len(self.players)
        else:
            # Post-flop: Start with small blind (or first active player after dealer)
            start_pos = (self.dealer_pos + 1) % len(self.players)
        
        current_pos = start_pos
        last_raiser = None
        players_acted = 0
        players_in_hand = len([p for p in self.players if not p.folded])
        
        while players_acted < players_in_hand:
            player = self.players[current_pos]
            
            if not player.folded and not player.all_in:
                game_state = {
                    'current_bet': self.current_bet,
                    'min_raise': self.big_blind,
                    'max_raise': player.chips,
                    'pot': self.pot,
                    'community_cards': self.community_cards,
                    'player_bet': player.current_bet
                }
                
                # Clear screen and show updated game state at top
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Always display the full game state at the top
                self.display_persistent_game_state(round_name)
                
                # Create player action table
                action_table = Table(title=f"{player.name}'s Turn")
                action_table.add_column("Info", style="cyan")
                action_table.add_column("Value", style="white")
                
                hand_str = ' '.join([Card.int_to_str(card) for card in player.hand])
                to_call = self.current_bet - player.current_bet
                
                action_table.add_row("Hand", f"[green]{hand_str}[/green]")
                action_table.add_row("Chips", f"[yellow]${player.chips}[/yellow]")
                action_table.add_row("Current Bet", f"[blue]${player.current_bet}[/blue]")
                action_table.add_row("To Call", f"[red]${to_call}[/red]")
                
                console.print(action_table)
                
                action, amount = player.decide_action(game_state)
                
                # Create action result table
                result_table = Table(title="Action")
                result_table.add_column("Player", style="cyan")
                result_table.add_column("Decision", style="bold")
                result_table.add_column("Amount", style="yellow")
                
                if action == 'fold':
                    player.folded = True
                    result_table.add_row(player.name, "[yellow]FOLDS[/yellow]", "--")
                elif action == 'check':
                    if player.current_bet < self.current_bet:
                        result_table.add_row(player.name, "[red]INVALID CHECK[/red]", "--")
                        console.print(result_table)
                        console.print(f"[red]Must call or fold - trying again...[/red]")
                        continue
                    result_table.add_row(player.name, "[cyan]CHECKS[/cyan]", "--")
                elif action == 'call':
                    call_amount = self.current_bet - player.current_bet
                    if call_amount >= player.chips:
                        call_amount = player.chips
                        player.all_in = True
                        result_table.add_row(player.name, "[magenta]CALLS ALL-IN[/magenta]", f"${call_amount}")
                    else:
                        result_table.add_row(player.name, "[blue]CALLS[/blue]", f"${call_amount}")
                    
                    player.chips -= call_amount
                    player.current_bet += call_amount
                    self.pot += call_amount
                elif action == 'raise':
                    total_bet_needed = amount
                    if total_bet_needed <= player.current_bet:
                        result_table.add_row(player.name, "[red]INVALID RAISE[/red]", f"${total_bet_needed}")
                        console.print(result_table)
                        console.print(f"[red]Raise must be more than current bet - trying again...[/red]")
                        continue
                    
                    additional_chips_needed = total_bet_needed - player.current_bet
                    if additional_chips_needed >= player.chips:
                        additional_chips_needed = player.chips
                        total_bet_needed = player.current_bet + additional_chips_needed
                        player.all_in = True
                        result_table.add_row(player.name, "[magenta]RAISES ALL-IN[/magenta]", f"${total_bet_needed}")
                    else:
                        result_table.add_row(player.name, "[bold green]RAISES[/bold green]", f"${total_bet_needed}")
                    
                    player.chips -= additional_chips_needed
                    player.current_bet = total_bet_needed
                    self.pot += additional_chips_needed
                    self.current_bet = total_bet_needed
                    last_raiser = current_pos
                    players_acted = 0  # Reset action count after raise
                
                console.print(result_table)
                
                # Input interrupt between bot actions
                input(f"Press Enter to continue after {player.name}'s action...")
            
            # Clear screen and refresh display after each player (whether they acted or not)
            # This will be done at the beginning of the next player's turn instead
            # os.system('cls' if os.name == 'nt' else 'clear')
            # self.display_persistent_game_state(round_name)
            
            current_pos = (current_pos + 1) % len(self.players)
            players_acted += 1
            
            if last_raiser is not None and current_pos == last_raiser:
                break  # Betting round complete
    
    def deal_community_cards(self, num_cards):
        for _ in range(num_cards):
            card = self.deck.draw(1)[0]  # draw(1) returns a list, get first element
            self.community_cards.append(card)
        
        self.display_game_state("Community Cards")
    
    def showdown(self):
        console.print("[bold green]--- Showdown ---[/bold green]")
        
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
            console.print(f"[bold yellow]{winner.name} wins {self.pot} chips![/bold yellow]")
            return
        
        # Evaluate hands
        scores = []
        for player in active_players:
            score = self.evaluator.evaluate(self.community_cards, player.hand)
            scores.append((player, score))
        
        # Sort by best hand (lower score is better)
        scores.sort(key=lambda x: x[1])
        
        # Determine winners
        winning_score = scores[0][1]
        winners = [p for p, s in scores if s == winning_score]
        prize = self.pot // len(winners)
        
        # Display hand rankings
        table = Table(title="Showdown Results")
        table.add_column("Player", style="cyan")
        table.add_column("Hand")
        table.add_column("Rank", style="magenta")
        
        for player, score in scores:
            hand_class = self.evaluator.class_to_string(self.evaluator.get_rank_class(score))
            table.add_row(
                player.name,
                " ".join([Card.int_to_str(card) for card in player.hand]),
                hand_class
            )
        
        console.print(table)
        
        # Award prizes
        for winner in winners:
            winner.chips += prize
            console.print(f"[bold yellow]{winner.name} wins {prize} chips with {self.evaluator.class_to_string(self.evaluator.get_rank_class(winning_score))}[/bold yellow]")
    
    def display_persistent_game_state(self, round_name):
        """Display the persistent game state that stays at the top of the screen"""
        
        # 1. GAME-WIDE STATE: Display all players table first (most persistent)
        table = Table(title="All Players")
        table.add_column("Position", style="yellow")
        table.add_column("Name", style="cyan")
        table.add_column("Hole Cards", style="green")
        table.add_column("Chips", style="white")
        table.add_column("Current Bet", style="blue")
        table.add_column("Status", style="white")
        
        # Calculate positions
        sb_pos = (self.dealer_pos + 1) % len(self.players)
        bb_pos = (self.dealer_pos + 2) % len(self.players)
        
        for i, player in enumerate(self.players):
            # Determine position
            position = ""
            if i == self.dealer_pos:
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
        
        console.print(table)
        console.print()  # Add spacing
        
        # 2. HAND-WIDE STATE: Display stage header and community cards
        console.print(f"[bold cyan]=== {round_name} ===[/bold cyan]")
        
        # Display community cards table
        if self.community_cards:
            stage = len(self.community_cards)
            if stage == 3:
                stage_name = "Flop"
            elif stage == 4:
                stage_name = "Turn"
            elif stage == 5:
                stage_name = "River"
            else:
                stage_name = "Community Cards"
            
            community_str = " ".join([Card.int_to_str(card) for card in self.community_cards])
            community_table = Table(title="Community Cards")
            community_table.add_column(stage_name, style="green", justify="center")
            community_table.add_row(community_str)
        else:
            community_table = Table(title="Community Cards")
            community_table.add_column("Pre-flop", style="dim", justify="center")
            community_table.add_row("[dim]None dealt yet[/dim]")
        
        console.print(community_table)
        
        # Display pot and current bet
        console.print(f"Pot: [yellow]${self.pot}[/yellow] | Current bet: [red]${self.current_bet}[/red]")
        console.print()  # Add spacing before individual player actions
    
    def display_game_state(self, round_name):
        console.print(f"[bold]=== {round_name} ===[/bold]")
        
        # Display community cards in a Rich table
        if self.community_cards:
            stage = len(self.community_cards)
            if stage == 3:
                stage_name = "Flop"
            elif stage == 4:
                stage_name = "Turn"
            elif stage == 5:
                stage_name = "River"
            else:
                stage_name = "Community Cards"
            
            community_str = " ".join([Card.int_to_str(card) for card in self.community_cards])
            community_table = Table(title="Community Cards")
            community_table.add_column(stage_name, style="green", justify="center")
            community_table.add_row(community_str)
        else:
            community_table = Table(title="Community Cards")
            community_table.add_column("Pre-flop", style="dim", justify="center")
            community_table.add_row("[dim]None dealt yet[/dim]")
        
        console.print(community_table)
        
        # Display pot and current bet
        console.print(f"Pot: [yellow]{self.pot}[/yellow] | Current bet: [red]{self.current_bet}[/red]")
        
        # Display player status
        table = Table(title="Players")
        table.add_column("Position", style="yellow")
        table.add_column("Name", style="cyan")
        table.add_column("Hole Cards", style="green")
        table.add_column("Chips")
        table.add_column("Current Bet")
        table.add_column("Status")
        
        # Calculate positions
        sb_pos = (self.dealer_pos + 1) % len(self.players)
        bb_pos = (self.dealer_pos + 2) % len(self.players)
        
        for i, player in enumerate(self.players):
            # Determine position
            position = ""
            if i == self.dealer_pos:
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
                hole_cards = "[dim] ".join([Card.int_to_str(card) for card in player.hand]).join(" [/dim]")
            else:
                hole_cards = "[dim]--[/dim]"
            
            table.add_row(
                position,
                player.name,
                hole_cards,
                str(player.chips),
                str(player.current_bet),
                " ".join(status)
            )
        
        # Remove the existing time.sleep since we're clearing screen
        # time.sleep(1)  # Pause for readability
    
    def play_hand(self):
        # Pre-flop betting
        self.betting_round("Pre-flop")
        
        # Flop
        if len([p for p in self.players if not p.folded]) > 1:
            self.deal_community_cards(3)
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.betting_round("Flop")
        
        # Turn
        if len([p for p in self.players if not p.folded]) > 1:
            self.deal_community_cards(1)
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.betting_round("Turn")
        
        # River
        if len([p for p in self.players if not p.folded]) > 1:
            self.deal_community_cards(1)
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.betting_round("River")
        
        # Showdown
        if len([p for p in self.players if not p.folded]) > 0:
            self.showdown()
            
            # Remove bankrupt players immediately after showdown
            bankrupt_players = [p for p in self.players if p.chips <= 0]
            for player in bankrupt_players:
                console.print(f"[bold red]{player.name} is eliminated with $0 chips![/bold red]")
            
            # Remove bankrupt players from the game
            remaining_players = [p for p in self.players if p.chips > 0]
            
            # Adjust dealer position if players were eliminated
            if len(remaining_players) < len(self.players):
                # Count eliminated players before current dealer
                eliminated_before_dealer = 0
                for i, player in enumerate(self.players):
                    if i < self.dealer_pos and player.chips <= 0:
                        eliminated_before_dealer += 1
                
                # Update dealer position accounting for eliminated players
                self.dealer_pos = (self.dealer_pos - eliminated_before_dealer) % len(remaining_players)
                
            self.players = remaining_players
        
        # Rotate dealer button (only if there are still players)
        if len(self.players) > 1:
            self.dealer_pos = (self.dealer_pos + 1) % len(self.players)