#!/usr/bin/env python3

import time
import json
import logging
from datetime import datetime
from rich.console import Console
from src.siem_core import AdvancedSIEM
from queue import Queue

def generate_test_events():
    """Generate test events to verify detection capabilities"""
    return [
        {
            'timestamp': datetime.now().isoformat(),
            'source': 'system',
            'content': 'Failed login attempt from IP 192.168.1.100',
            'severity': 'WARNING'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'source': 'system',
            'content': 'sudo su - root executed by user',
            'severity': 'HIGH'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'source': 'network',
            'content': 'Detected nmap scan from IP 10.0.0.5',
            'severity': 'MEDIUM'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'source': 'application',
            'content': "SELECT * FROM users WHERE username='' OR '1'='1'",
            'severity': 'HIGH'
        },
        {
            'timestamp': datetime.now().isoformat(),
            'source': 'system',
            'content': 'cat /etc/shadow attempted by unauthorized user',
            'severity': 'CRITICAL'
        }
    ]

def test_siem():
    """Test SIEM functionality"""
    console = Console()
    console.print("\n[bold cyan]Starting SIEM Testing...[/bold cyan]")
    
    # Initialize SIEM
    try:
        siem = AdvancedSIEM()
        console.print("[green]✓[/green] SIEM initialized successfully")
    except Exception as e:
        console.print(f"[red]✗[/red] SIEM initialization failed: {str(e)}")
        return False
    
    # Test banner display
    try:
        siem.display_banner()
        console.print("[green]✓[/green] Banner display working")
    except Exception as e:
        console.print(f"[red]✗[/red] Banner display failed: {str(e)}")
    
    # Generate and process test events
    console.print("\n[bold cyan]Testing Event Processing...[/bold cyan]")
    test_events = generate_test_events()
    
    # Start components first
    try:
        # Start collectors
        console.print("\n[bold cyan]Starting Log Collectors...[/bold cyan]")
        siem.start_collectors()
        console.print("[green]✓[/green] Log collectors started")
        
        # Start analyzer
        console.print("\n[bold cyan]Starting Log Analyzer...[/bold cyan]")
        analyzer_thread = siem.start_analyzer()
        console.print("[green]✓[/green] Log analyzer started")
        
        # Start AI detection
        console.print("\n[bold cyan]Starting AI Detection Engine...[/bold cyan]")
        ai_thread = siem.start_ai_detection()
        console.print("[green]✓[/green] AI detection engine started")
        
        # Wait for components to initialize
        time.sleep(2)
        
        # Process test events
        for event in test_events:
            try:
                # Add event to queue
                siem.event_queue.put(event)
                console.print(f"[yellow]Event added:[/yellow] {event['content'][:50]}...")
                
                # Give time for processing
                time.sleep(0.5)
                
            except Exception as e:
                console.print(f"[red]✗[/red] Event processing failed: {str(e)}")
        
        # Wait for processing to complete
        console.print("\n[bold yellow]Waiting for event processing...[/bold yellow]")
        time.sleep(5)
        
        console.print("\n[bold green]Testing completed![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]Error during testing:[/red] {str(e)}")
        return False

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Run tests
    test_siem() 