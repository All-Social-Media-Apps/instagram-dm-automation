#!/usr/bin/env python3
"""
Instagram DMs Automation Replica
Main entry point for the Apify-style Instagram DM automation tool.
Windows-compatible version with ASCII characters.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID

# Set UTF-8 encoding for Windows compatibility
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import with error handling
try:
    from core.instagram_dm_actor import InstagramDMsActor
    from models.input_schema import InputSchema, validate_input
    from models.output_schema import OutputSchema
    from utils.logger import setup_logger, get_logger
    from utils.config import load_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are installed and properly structured.")
    sys.exit(1)

console = Console()
logger = get_logger(__name__)

class InstagramDMsAutomation:
    """Main application class that replicates Apify Instagram DMs Automation actor functionality."""

    def __init__(self):
        self.actor = None
        self.config = None
        self.results = []

    async def initialize(self, input_data: Dict[str, Any]) -> bool:
        """Initialize the automation actor with input parameters."""
        try:
            # Validate input schema
            validated_input = validate_input(input_data)

            # Load configuration
            self.config = load_config()

            # Setup logging
            setup_logger(self.config.LOG_LEVEL, self.config.LOG_FILE)

            # Initialize the Instagram DM actor
            self.actor = InstagramDMsActor(validated_input, self.config.__dict__)

            logger.info("Instagram DMs Automation initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize automation: {str(e)}")
            console.print(f"[red]ERROR: Initialization failed: {str(e)}[/red]")
            return False

    async def run_automation(self, input_data: Dict[str, Any]) -> OutputSchema:
        """Run the complete Instagram DM automation process."""
        console.print(Panel.fit("Instagram DMs Automation - Apify Replica", style="bold blue"))

        # Initialize
        if not await self.initialize(input_data):
            from datetime import datetime
            return OutputSchema(
                success=False,
                total_attempted=0,
                successful_sends=0,
                failed_sends=0,
                skipped_sends=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                runtime_seconds=0.0,
                results=[],
                error="Failed to initialize automation",
                average_processing_time_ms=0.0,
                rate_limit_hits=0,
                session_valid=False
            )

        try:
            # Start the automation process
            with Progress() as progress:
                main_task = progress.add_task("[cyan]Running automation...", total=100)

                # Execute the automation
                results = await self.actor.run(progress_callback=lambda p: progress.update(main_task, completed=p))

                progress.update(main_task, completed=100)

            # Display results
            self._display_results(results)
            return results

        except Exception as e:
            logger.error(f"Automation run failed: {str(e)}")
            console.print(f"[red]ERROR: Automation failed: {str(e)}[/red]")
            from datetime import datetime
            return OutputSchema(
                success=False,
                total_attempted=0,
                successful_sends=0,
                failed_sends=0,
                skipped_sends=0,
                start_time=datetime.now(),
                end_time=datetime.now(),
                runtime_seconds=0.0,
                results=[],
                error=str(e),
                average_processing_time_ms=0.0,
                rate_limit_hits=0,
                session_valid=False
            )

    def _display_results(self, results: OutputSchema):
        """Display automation results in a formatted table."""
        # Summary panel
        summary_text = f"""
        [green]SUCCESS[/green] Total Messages Attempted: {results.total_attempted}
        [green]SUCCESS[/green] Successfully Sent: {results.successful_sends}
        [red]FAILED[/red] Failed Sends: {results.failed_sends}
        [yellow]TIME[/yellow] Total Runtime: {results.runtime_seconds:.2f}s
        """

        console.print(Panel(summary_text, title="Automation Summary", style="green"))

        # Detailed results table
        if results.results:
            table = Table(title="Detailed Results")
            table.add_column("Username", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Message", style="yellow")
            table.add_column("Timestamp", style="magenta")
            table.add_column("Error", style="red")

            for result in results.results:
                status = "[green]SENT[/green]" if result.success else "[red]FAILED[/red]"
                error_msg = result.error_message or ""

                table.add_row(
                    result.username,
                    status,
                    result.message[:50] + "..." if len(result.message) > 50 else result.message,
                    result.timestamp.strftime("%H:%M:%S"),
                    error_msg[:30] + "..." if error_msg and len(error_msg) > 30 else error_msg
                )

            console.print(table)

# CLI Interface
@click.group()
def cli():
    """Instagram DMs Automation - Apify Actor Replica"""
    pass

@cli.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), help='JSON input file path')
@click.option('--session-id', '-s', help='Instagram session ID')
@click.option('--usernames', '-u', help='Comma-separated list of usernames')
@click.option('--message', '-m', help='Message to send')
@click.option('--output-file', '-o', default='output.json', help='Output file path')
@click.option('--test-mode', is_flag=True, help='Run in test mode (no actual messages sent)')
def run(input_file, session_id, usernames, message, output_file, test_mode):
    """Run the Instagram DM automation."""
    
    # Prepare input data
    if input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    else:
        # Build input from CLI arguments
        input_data = {}
        if session_id:
            input_data['sessionId'] = session_id
        if usernames:
            input_data['usernames'] = [u.strip() for u in usernames.split(',')]
        if message:
            input_data['message'] = message
        if test_mode:
            input_data['testMode'] = True

    # Validate required parameters
    if not input_data.get('sessionId'):
        console.print("[red]ERROR: Instagram session ID is required[/red]")
        return

    if not input_data.get('usernames'):
        console.print("[red]ERROR: Target usernames are required[/red]")
        return

    if not input_data.get('message'):
        console.print("[red]ERROR: Message content is required[/red]")
        return

    # Run automation
    automation = InstagramDMsAutomation()
    results = asyncio.run(automation.run_automation(input_data))

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        # Use model_dump instead of dict() for Pydantic v2
        try:
            json.dump(results.model_dump(), f, indent=2, default=str, ensure_ascii=False)
        except AttributeError:
            # Fallback for older Pydantic versions
            json.dump(results.dict(), f, indent=2, default=str, ensure_ascii=False)

    console.print(f"[green]SUCCESS: Results saved to {output_file}[/green]")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """Validate input JSON file against schema."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        validated = validate_input(input_data)
        console.print("[green]SUCCESS: Input validation successful[/green]")
        
        # Use model_dump instead of dict() for Pydantic v2
        try:
            validated_dict = validated.model_dump()
        except AttributeError:
            # Fallback for older Pydantic versions
            validated_dict = validated.dict()
            
        console.print(f"[cyan]INFO: Validated parameters: {len(validated_dict)} items[/cyan]")
        console.print(f"[cyan]INFO: Target users: {', '.join(validated.usernames)}[/cyan]")
        console.print(f"[cyan]INFO: Message length: {len(validated.message)} characters[/cyan]")

    except Exception as e:
        console.print(f"[red]ERROR: Input validation failed: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
def test_connection():
    """Test Instagram connection with provided session ID."""
    session_id = click.prompt("Enter Instagram session ID", hide_input=True)

    input_data = {
        'sessionId': session_id,
        'usernames': ['test_user'],  # Dummy username for connection test
        'message': 'test',
        'testMode': True
    }

    automation = InstagramDMsAutomation()
    console.print("[cyan]INFO: Testing Instagram connection...[/cyan]")

    # This would test connection without sending actual messages
    result = asyncio.run(automation.run_automation(input_data))

    if result.success:
        console.print("[green]SUCCESS: Connection test successful[/green]")
    else:
        console.print(f"[red]ERROR: Connection test failed: {result.error}[/red]")

if __name__ == "__main__":
    cli()
