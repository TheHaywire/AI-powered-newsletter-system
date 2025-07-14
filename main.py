#!/usr/bin/env python3
"""
AI Newsletter Generator - Main Script
Command-line interface for the AI-powered newsletter system
"""

import os
import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from newsletter_orchestrator import NewsletterOrchestrator

console = Console()

def print_banner():
    """Print the application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    AI Newsletter Generator                    ║
    ║                                                              ║
    ║  🤖 Research • 📊 Analysis • ✍️ Creation • 📧 Distribution  ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner, border_style="blue"))

def print_help():
    """Print detailed help information"""
    help_text = """
    [bold blue]AI Newsletter Generator[/bold blue]
    
    This system demonstrates how AI can research and create newsletters by:
    
    [bold]1. Research Phase[/bold]
    • Discovering trending topics from social media and news sources
    • Identifying authoritative sources and RSS feeds
    • Aggregating relevant articles and content
    
    [bold]2. Analysis Phase[/bold]
    • Performing sentiment analysis on collected content
    • Fact-checking and cross-referencing information
    • Scoring relevance and detecting potential bias
    
    [bold]3. Creation Phase[/bold]
    • Summarizing key articles and findings
    • Generating insights and actionable takeaways
    • Structuring content into compelling newsletter format
    
    [bold]4. Quality Assurance[/bold]
    • Grammar and style checking
    • Consistency verification
    • Performance optimization
    
    [bold]Usage Examples:[/bold]
    • python main.py --generate                    # Generate a newsletter
    • python main.py --theme "AI & ML"             # Generate with specific theme
    • python main.py --interactive                 # Run in interactive mode
    • python main.py --schedule                    # Schedule automatic generation
    • python main.py --demo                        # Run with demo data
    
    [bold]Output Formats:[/bold]
    • Markdown (.md) - For web publishing
    • HTML (.html) - For email distribution
    • Plain Text (.txt) - For simple sharing
    
    [bold]Configuration:[/bold]
    • Edit config/research_config.json for sources and keywords
    • Edit config/orchestrator_config.json for quality settings
    • Set environment variables for API keys
    """
    console.print(Panel(help_text, border_style="green"))

def run_demo():
    """Run the system with demo data"""
    console.print(Panel("[bold blue]Running Demo Mode[/bold blue]", border_style="blue"))
    
    # Create demo orchestrator
    orchestrator = NewsletterOrchestrator()
    
    # Generate newsletter with demo theme
    try:
        report = orchestrator.generate_newsletter("AI & Machine Learning")
        
        # Show demo results
        table = Table(title="Demo Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        newsletter = report["newsletter"]
        table.add_row("Newsletter Title", newsletter.title)
        table.add_row("Total Articles", str(sum(len(section.articles) for section in newsletter.sections)))
        table.add_row("Word Count", str(newsletter.word_count))
        table.add_row("Reading Time", f"{newsletter.reading_time} minutes")
        table.add_row("Quality Score", f"{report['quality_report']['overall_score']:.2%}")
        
        console.print(table)
        
        console.print("\n[green]Demo completed successfully! Check the 'output' directory for generated files.[/green]")
        
    except Exception as e:
        console.print(f"[red]Demo failed: {e}[/red]")
        console.print("[yellow]This is expected if external APIs are not configured.[/yellow]")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Newsletter Generator - Research, analyze, and create newsletters automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --generate
  python main.py --theme "Technology Trends"
  python main.py --interactive
  python main.py --demo
        """
    )
    
    parser.add_argument(
        "--generate", 
        action="store_true",
        help="Generate a newsletter"
    )
    
    parser.add_argument(
        "--theme",
        type=str,
        help="Specify newsletter theme (e.g., 'AI & ML', 'Startup News')"
    )
    
    parser.add_argument(
        "--interactive", 
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--schedule", 
        action="store_true",
        help="Schedule automatic newsletter generation"
    )
    
    parser.add_argument(
        "--demo", 
        action="store_true",
        help="Run with demo data"
    )
    
    parser.add_argument(
        "--help-detailed", 
        action="store_true",
        help="Show detailed help information"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Handle help
    if args.help_detailed:
        print_help()
        return
    
    # Handle demo mode
    if args.demo:
        run_demo()
        return
    
    # Create orchestrator
    config_path = args.config if args.config else "config/orchestrator_config.json"
    orchestrator = NewsletterOrchestrator(config_path)
    
    # Handle different modes
    if args.interactive:
        orchestrator.run_interactive()
    
    elif args.schedule:
        console.print("[blue]Starting scheduled newsletter generation...[/blue]")
        orchestrator.schedule_newsletter()
    
    elif args.generate or args.theme:
        theme = args.theme or None
        try:
            console.print("[blue]Starting newsletter generation...[/blue]")
            report = orchestrator.generate_newsletter(theme)
            
            # Show success summary
            if report and 'newsletter' in report:
                newsletter = report['newsletter']
                console.print(f"[green]Newsletter generated successfully![/green]")
                console.print(f"📧 Title: {newsletter.title}")
                console.print(f"📊 Articles: {sum(len(section.articles) for section in newsletter.sections)}")
                console.print(f"⏱️  Reading Time: {newsletter.reading_time} minutes")
                console.print(f"📁 Check 'output' directory for files")
                
                # Show quality score if available
                if 'quality_report' in report:
                    quality = report['quality_report']
                    console.print(f"🎯 Quality Score: {quality['overall_score']:.1%}")
            else:
                console.print("[yellow]Newsletter generated but no report returned[/yellow]")
            
        except Exception as e:
            console.print(f"[red]Error generating newsletter: {e}[/red]")
            console.print("[yellow]Make sure you have the required dependencies installed.[/yellow]")
            return 1
    
    else:
        # No arguments provided, show help
        parser.print_help()
        console.print("\n[blue]For detailed information, run: python main.py --help-detailed[/blue]")

if __name__ == "__main__":
    main() 