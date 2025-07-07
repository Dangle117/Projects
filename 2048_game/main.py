import os
from rich import print
from rich.console import Console
from rich.table import Table
import random
import copy

console = Console()

def clear_screen():
    # Clears the terminal screen depending on OS
    os.system("cls" if os.name == "nt" else "clear")

class Game2048():
    def __init__(self):
        # Initialize empty 4x4 grid
        self.layout = [[0]*4 for _ in range(4)]
        
        # Mapping user inputs to rotations to simplify move logic
        self.rotation: dict[str, int] = {
            'a': 0,  # left
            'w': 3,  # up
            's': 1,  # down
            'd': 2   # right
        }
        
        # Place two random tiles to start the game
        self.random_cell()
        self.random_cell()

    def user_input(self) -> str:
        # Prompt user for input, convert to lowercase
        _input: str = console.input("🎮 [bold yellow]Move (W/A/S/D): [/bold yellow]").lower()
        return _input

    def random_cell(self) -> None:
        # Place a random 2 or 4 (90% 2, 10% 4) on an empty cell
        while True:
            loc = [random.randint(0,3), random.randint(0,3)]
            if self.layout[loc[0]][loc[1]] == 0:
                self.layout[loc[0]][loc[1]] = 4 if random.random() < 0.1 else 2
                break

    def rotate(self, grid, times) -> list:
        # Rotate grid 90 degrees clockwise 'times' times
        for _ in range(times):
            grid = [list(row) for row in zip(*grid[::-1])]
        return grid

    def can_merge(self, grid) -> bool:
        # Check if there are any valid moves (empty spaces or adjacent merges)
        for i in range(4):
            for j in range(4):
                if grid[i][j] == 0:
                    return True
                if j < 3 and grid[i][j] == grid[i][j + 1]:
                    return True
                if i < 3 and grid[i][j] == grid[i + 1][j]:
                    return True
        return False

    def movement(self, grid) -> list:
        # Perform user move by rotating, calculating merges, then rotating back
        user_move = self.user_input()
        r = self.rotation.get(user_move)
        if r is None:
            return grid  # invalid input, skip turn
        
        rotate_grid = self.rotate(grid, r)
        grid = self.calculation(rotate_grid)
        rotate_grid_back = self.rotate(grid, (4 - r))
        
        return rotate_grid_back

    def calculation(self, grid) -> list:
        # Slide and merge tiles for each row
        new_grid = []
        for row in grid:
            new_row = [cell for cell in row if cell != 0]  # slide left
            for i in range(len(new_row) - 1):
                if new_row[i] == new_row[i + 1]:
                    new_row[i] *= 2  # merge
                    new_row.pop(i + 1)
                    new_row.append(0)  # keep length same
            new_row += [0] * (len(row) - len(new_row))  # pad with zeros
            new_grid.append(new_row)
        return new_grid

    def show_layout(self, grid) -> None:
        # Use rich table to render the board with colors
        table = Table(title="2048 GAME", style="bold white on black")
        for _ in range(4):
            table.add_column(justify="center", style="bold white")

        for row in grid:
            styled_row = []
            for cell in row:
                # Use different colors based on value
                if cell == 0:
                    styled_row.append("[dim]-[/dim]")
                
                elif cell == 2:
                    styled_row.append(f"[cyan]{cell}[/cyan]")
                
                elif cell == 4:
                    styled_row.append(f"[blue]{cell}[/blue]")
                
                elif cell == 8:
                    styled_row.append(f"[magenta]{cell}[/magenta]")
                
                elif cell == 16:
                    styled_row.append(f"[green]{cell}[/green]")
                
                elif cell == 32:
                    styled_row.append(f"[yellow]{cell}[/yellow]")
                
                elif cell == 64:
                    styled_row.append(f"[red]{cell}[/red]")
                
                elif cell == 128:
                    styled_row.append(f"[bright_cyan]{cell}[/bright_cyan]")
                
                elif cell == 256:
                    styled_row.append(f"[bright_magenta]{cell}[/bright_magenta]")
                
                elif cell == 512:
                    styled_row.append(f"[bright_green]{cell}[/bright_green]")
                
                elif cell == 1024:
                    styled_row.append(f"[bright_yellow]{cell}[/bright_yellow]")
                
                elif cell == 2048:
                    styled_row.append(f"[reverse][bold bright_white on bright_red]{cell}[/bold bright_white on bright_red][/reverse]")
                
                else:
                    styled_row.append(f"[bold white]{cell}[/bold white]")
            table.add_row(*styled_row)
        console.print(table)

    def play(self) -> None:
        # Main loop for human player mode
        while True:
            clear_screen()
            prev_layout = copy.deepcopy(self.layout)
            self.show_layout(self.layout)
            self.layout = self.movement(self.layout)

            # Only place new tile if move changed the board
            if self.layout != prev_layout:
                self.random_cell()

            # Check win
            if any(2048 in row for row in self.layout):
                clear_screen()
                self.show_layout(self.layout)
                console.print("[bold green]YOU WIN[/bold green]")
                return

            # Check lose
            if not self.can_merge(self.layout):
                clear_screen()
                self.show_layout(self.layout)
                console.print("[bold red]YOU LOSE[/bold red]")
                return

    def auto_play(self, delay=0.1) -> None:
        # Simple AI that chooses move with most empty cells + corner bonus
        import time
        while True:
            clear_screen()
            self.show_layout(self.layout)
            time.sleep(delay)

            best_move = None
            best_score = -1

            # Try all moves and score them
            for move, r in self.rotation.items():
                rotated = self.rotate(self.layout, r)
                moved = self.calculation(rotated)
                moved_back = self.rotate(moved, (4 - r))

                if moved_back != self.layout:
                    empty_cells = sum(row.count(0) for row in moved_back)
                    corner_bonus = moved_back[0][0] * 0.1
                    score = empty_cells + corner_bonus

                    if score > best_score:
                        best_score = score
                        best_move = move

            # No valid moves = lose
            if best_move is None:
                clear_screen()
                self.show_layout(self.layout)
                console.print("[bold red]AI LOSES![/bold red]")
                return

            # Apply best move
            r = self.rotation[best_move]
            rotated = self.rotate(self.layout, r)
            moved = self.calculation(rotated)
            self.layout = self.rotate(moved, (4 - r))
            self.random_cell()

            # Check win
            if any(2048 in row for row in self.layout):
                clear_screen()
                self.show_layout(self.layout)
                console.print("[bold green]AI WINS![/bold green]")
                return

            # Check lose
            if not self.can_merge(self.layout):
                clear_screen()
                self.show_layout(self.layout)
                console.print("[bold red]AI LOSES![/bold red]")
                return
   
def main() -> None:
    # Main entry: choose manual or AI mode
    mode: str = console.input("Play 👤 or AI_Play 🤖 (p or a): ").lower()
    game = Game2048()
    
    if mode == 'a':
        game.auto_play() # ← AI
    
    else:
        game.play()

if __name__ == "__main__":
    main()
