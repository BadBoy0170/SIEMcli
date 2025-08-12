#!/usr/bin/env python3

import os
import sys
import time
import logging
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress
from pyfiglet import Figlet
from colorama import Fore, Style, init
import yaml
import threading
from queue import Queue
import json

# Initialize colorama
init(autoreset=True)

class AdvancedSIEM:
    def __init__(self):
        self.console = Console()
        self.event_queue = Queue()
        self.should_run = True
        self.setup_logging()
        
    def display_banner(self):
        f = Figlet(font='slant')
        banner = f.renderText('AdvancedSIEM')
        self.console.print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
        self.console.print("[bold blue]Advanced Security Information and Event Management System[/bold blue]")
        self.console.print("[bold green]Version 2.0 - AI-Powered Detection[/bold green]\n")
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        self.logger = logging.getLogger("rich")
        
    def start_collectors(self):
        """Start log collectors in separate threads"""
        from .collectors import LogCollector
        collectors = []
        # Add different collectors for various sources
        sources = ['system', 'network', 'application']
        
        for source in sources:
            collector = LogCollector(source, self.event_queue)
            thread = threading.Thread(target=collector.run)
            thread.daemon = True
            thread.start()
            collectors.append(thread)
            
    def start_analyzer(self):
        """Start the analyzer in a separate thread"""
        from .analyzer import LogAnalyzer
        analyzer = LogAnalyzer(self.event_queue)
        thread = threading.Thread(target=analyzer.run)
        thread.daemon = True
        thread.start()
        return thread
        
    def start_ai_detection(self):
        """Start AI-based detection system"""
        from .ai_detection import AIDetectionEngine
        ai_engine = AIDetectionEngine(self.event_queue)
        thread = threading.Thread(target=ai_engine.run)
        thread.daemon = True
        thread.start()
        return thread
        
    def run(self):
        """Main execution method"""
        try:
            self.display_banner()
            
            with Progress() as progress:
                task1 = progress.add_task("[cyan]Starting log collectors...", total=100)
                task2 = progress.add_task("[green]Initializing AI engine...", total=100)
                task3 = progress.add_task("[yellow]Setting up analyzers...", total=100)
                
                # Simulate startup progress
                while not progress.finished:
                    progress.update(task1, advance=0.9)
                    progress.update(task2, advance=0.7)
                    progress.update(task3, advance=0.8)
                    time.sleep(0.02)
            
            self.console.print("\n[bold green]✓[/bold green] SIEM System initialized successfully!")
            
            # Start all components
            self.start_collectors()
            analyzer_thread = self.start_analyzer()
            ai_thread = self.start_ai_detection()
            
            # Keep the main thread running
            while self.should_run:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Shutting down SIEM system...[/bold red]")
            self.should_run = False
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Critical error: {str(e)}")
            self.should_run = False
            sys.exit(1)

if __name__ == "__main__":
    siem = AdvancedSIEM()
    siem.run() 