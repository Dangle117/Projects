import os
from time import sleep
from datetime import datetime
import pygame
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

console = Console()

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

set_time: str = input("🔧 Enter your alarm time (HH:MM:SS): ")

is_running = True
while is_running:
    clear_screen()
    current = datetime.now().strftime("%H:%M:%S")

    # Styled digital clock display
    clock_panel = Panel.fit(
        Align.center(f"[bold cyan]{current}[/bold cyan]", vertical="middle"),
        title="[bold magenta]⏰ DIGITAL CLOCK[/bold magenta]",
        subtitle=f"[green]Alarm set for: [bold yellow]{set_time}[/bold yellow]",
        border_style="bright_blue",
        padding=(1, 10),
    )

    console.print(clock_panel)

    if current == set_time:
        is_running = False
        console.print("\n[bold red blink]🔔 Alarm time reached![/bold red blink]")
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("sound/alarm_clock.mp3")  # Make sure this file exists
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            sleep(1)

    sleep(1)
