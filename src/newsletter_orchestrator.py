"""
AI Newsletter Orchestrator
Coordinates research, analysis, and creation engines to produce complete newsletters
"""

import os
import json
import schedule
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from research_engine import ResearchEngine
from analysis_engine import AnalysisEngine
from creation_engine import ContentCreationEngine
from email_distributor import EmailDistributor

console = Console()

class NewsletterOrchestrator:
    """Main orchestrator for the AI newsletter system"""
    
    def __init__(self, config_path: str = "config/orchestrator_config.json"):
        self.config = self._load_config(config_path)
        self.research_engine = ResearchEngine()
        self.analysis_engine = AnalysisEngine()
        self.creation_engine = ContentCreationEngine(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.email_distributor = EmailDistributor()
        
        # Create output directories
        self._create_directories()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[yellow]Config file {config_path} not found. Using defaults.[/yellow]")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for the orchestrator"""
        return {
            "newsletter_theme": "Technology & Innovation",
            "output_formats": ["markdown", "html", "plain_text"],
            "schedule": {
                "frequency": "weekly",
                "day": "friday",
                "time": "09:00"
            },
            "quality_thresholds": {
                "min_articles": 5,
                "min_relevance_score": 0.6,
                "max_bias_score": 0.7
            },
            "output_directory": "output",
            "archive_directory": "archive"
        }
    
    def _create_directories(self):
        """Create necessary output directories"""
        directories = [
            self.config.get("output_directory", "output"),
            self.config.get("archive_directory", "archive"),
            "logs",
            "data"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def generate_newsletter(self, theme: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete newsletter"""
        theme = theme or self.config.get("newsletter_theme", "Technology & Innovation")
        
        console.print(Panel(f"[bold blue]Starting Newsletter Generation[/bold blue]\nTheme: {theme}", 
                           border_style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Research Phase
            task1 = progress.add_task("🔍 Researching trending topics...", total=None)
            topics = self.research_engine.discover_trending_topics()
            progress.update(task1, description=f"📚 Collected {len(topics)} trending topics")
            
            # Step 2: Content Collection
            task2 = progress.add_task("📰 Collecting articles...", total=None)
            articles = self.research_engine.collect_articles(topics)
            progress.update(task2, description=f"📄 Collected {len(articles)} articles")
            
            # Step 3: Content Analysis
            task3 = progress.add_task("🔬 Analyzing content...", total=None)
            analysis_results = self.analysis_engine.analyze_articles(articles)
            progress.update(task3, description=f"📊 Analyzed {len(analysis_results)} articles")
            
            # Step 4: Content Creation
            task4 = progress.add_task("✍️ Creating newsletter...", total=None)
            newsletter = self.creation_engine.create_newsletter(articles, analysis_results, theme)
            progress.update(task4, description=f"📧 Created newsletter: {newsletter.title}")
        
        # Step 5: Quality Check
        quality_report = self._perform_quality_check(newsletter, analysis_results)
        
        # Step 6: Save Outputs
        self._save_outputs(newsletter, articles, analysis_results, quality_report)
        
        # Step 7: Email Distribution (if enabled)
        email_results = self._distribute_newsletter(newsletter, theme)
        
        # Step 8: Generate Report
        final_report = self._generate_final_report(newsletter, articles, analysis_results, quality_report, email_results)
        
        console.print(Panel(f"[bold green]Newsletter Generation Complete![/bold green]\n{newsletter.title}", 
                           border_style="green"))
        
        return final_report
    
    def _perform_quality_check(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Perform quality checks on the generated newsletter"""
        console.print("[blue]Performing quality checks...[/blue]")
        
        quality_report = {
            "overall_score": 0.0,
            "checks_passed": 0,
            "total_checks": 0,
            "issues": [],
            "recommendations": []
        }
        
        checks = [
            self._check_article_count,
            self._check_relevance_scores,
            self._check_bias_scores,
            self._check_content_length,
            self._check_source_diversity
        ]
        
        for check in checks:
            result = check(newsletter, analysis_results)
            quality_report["total_checks"] += 1
            
            if result["passed"]:
                quality_report["checks_passed"] += 1
            else:
                quality_report["issues"].append(result["issue"])
                quality_report["recommendations"].append(result["recommendation"])
        
        quality_report["overall_score"] = quality_report["checks_passed"] / quality_report["total_checks"]
        
        return quality_report
    
    def _check_article_count(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Check if we have enough articles"""
        min_articles = self.config["quality_thresholds"]["min_articles"]
        total_articles = sum(len(section.articles) for section in newsletter.sections)
        
        passed = total_articles >= min_articles
        return {
            "passed": passed,
            "issue": f"Insufficient articles: {total_articles}/{min_articles}" if not passed else None,
            "recommendation": "Collect more articles from additional sources" if not passed else None
        }
    
    def _check_relevance_scores(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Check relevance scores of articles"""
        min_relevance = self.config["quality_thresholds"]["min_relevance_score"]
        low_relevance_count = sum(1 for result in analysis_results 
                                 if result.relevance_score < min_relevance)
        
        passed = low_relevance_count == 0
        return {
            "passed": passed,
            "issue": f"{low_relevance_count} articles below relevance threshold" if not passed else None,
            "recommendation": "Filter out low-relevance articles" if not passed else None
        }
    
    def _check_bias_scores(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Check bias scores of articles"""
        max_bias = self.config["quality_thresholds"]["max_bias_score"]
        high_bias_count = sum(1 for result in analysis_results 
                             if result.bias_score > max_bias)
        
        passed = high_bias_count == 0
        return {
            "passed": passed,
            "issue": f"{high_bias_count} articles above bias threshold" if not passed else None,
            "recommendation": "Review high-bias articles for balance" if not passed else None
        }
    
    def _check_content_length(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Check if newsletter has appropriate length"""
        min_words = 500
        max_words = 3000
        
        passed = min_words <= newsletter.word_count <= max_words
        return {
            "passed": passed,
            "issue": f"Newsletter length ({newsletter.word_count} words) outside optimal range" if not passed else None,
            "recommendation": "Adjust content length for better engagement" if not passed else None
        }
    
    def _check_source_diversity(self, newsletter, analysis_results) -> Dict[str, Any]:
        """Check source diversity"""
        sources = set()
        for section in newsletter.sections:
            for article in section.articles:
                # Handle both dict and dataclass objects
                if hasattr(article, 'get'):
                    sources.add(article.get('source', 'Unknown'))
                else:
                    sources.add(getattr(article, 'source', 'Unknown'))
        
        min_sources = 3
        passed = len(sources) >= min_sources
        return {
            "passed": passed,
            "issue": f"Limited source diversity: {len(sources)} sources" if not passed else None,
            "recommendation": "Include articles from more diverse sources" if not passed else None
        }
    
    def _distribute_newsletter(self, newsletter, theme: str) -> Dict[str, Any]:
        """Distribute newsletter via email if enabled"""
        # Check if email distribution is enabled
        if not self.config.get("email_settings", {}).get("enable_email_distribution", False):
            console.print("[yellow]Email distribution disabled in config[/yellow]")
            return {"enabled": False}
        
        try:
            # Generate HTML and text versions
            html_content = self.creation_engine.format_newsletter(newsletter, "html")
            text_content = self.creation_engine.format_newsletter(newsletter, "plain_text")
            
            # Send newsletter
            newsletter_id = f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            email_results = self.email_distributor.send_newsletter(
                html_content, text_content, theme, newsletter_id
            )
            
            return {
                "enabled": True,
                "results": email_results
            }
            
        except Exception as e:
            console.print(f"[red]Email distribution failed: {e}[/red]")
            return {
                "enabled": True,
                "error": str(e)
            }
    
    def _save_outputs(self, newsletter, articles, analysis_results, quality_report):
        """Save all outputs to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.config.get("output_directory", "output")
        
        # Save newsletter in different formats
        for format_type in self.config.get("output_formats", ["markdown"]):
            filename = f"{output_dir}/newsletter_{timestamp}.{format_type.replace('_', '')}"
            self.creation_engine.save_newsletter(newsletter, filename, format_type)
        
        # Save raw data
        self.research_engine.save_articles(f"{output_dir}/articles_{timestamp}.json")
        self.analysis_engine.save_analysis_results(analysis_results, f"{output_dir}/analysis_{timestamp}.json")
        
        # Save quality report
        with open(f"{output_dir}/quality_report_{timestamp}.json", 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        # Save comprehensive report
        comprehensive_report = {
            "newsletter_metrics": self.creation_engine.get_newsletter_metrics(newsletter),
            "research_summary": self.research_engine.get_research_summary(),
            "analysis_summary": self.analysis_engine.get_analysis_summary(analysis_results),
            "quality_report": quality_report,
            "generation_timestamp": timestamp
        }
        
        with open(f"{output_dir}/comprehensive_report_{timestamp}.json", 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
    
    def _generate_final_report(self, newsletter, articles, analysis_results, quality_report) -> Dict[str, Any]:
        """Generate final comprehensive report"""
        # Create summary table
        table = Table(title="Newsletter Generation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Newsletter Title", newsletter.title)
        table.add_row("Total Articles", str(sum(len(section.articles) for section in newsletter.sections)))
        table.add_row("Word Count", str(newsletter.word_count))
        table.add_row("Reading Time", f"{newsletter.reading_time} minutes")
        table.add_row("Sections", str(len(newsletter.sections)))
        table.add_row("Quality Score", f"{quality_report['overall_score']:.2%}")
        table.add_row("Checks Passed", f"{quality_report['checks_passed']}/{quality_report['total_checks']}")
        
        console.print(table)
        
        # Show quality issues if any
        if quality_report["issues"]:
            console.print("\n[red]Quality Issues Found:[/red]")
            for issue in quality_report["issues"]:
                console.print(f"• {issue}")
        
        # Show recommendations if any
        if quality_report["recommendations"]:
            console.print("\n[yellow]Recommendations:[/yellow]")
            for rec in quality_report["recommendations"]:
                console.print(f"• {rec}")
        
        return {
            "newsletter": newsletter,
            "articles": articles,
            "analysis_results": analysis_results,
            "quality_report": quality_report,
            "timestamp": datetime.now().isoformat()
        }
    
    def schedule_newsletter(self):
        """Schedule automatic newsletter generation"""
        schedule_config = self.config.get("schedule", {})
        frequency = schedule_config.get("frequency", "weekly")
        day = schedule_config.get("day", "friday")
        time_str = schedule_config.get("time", "09:00")
        
        if frequency == "weekly":
            getattr(schedule.every(), day).at(time_str).do(self.generate_newsletter)
        elif frequency == "daily":
            schedule.every().day.at(time_str).do(self.generate_newsletter)
        
        console.print(f"[green]Scheduled newsletter generation: {frequency} on {day} at {time_str}[/green]")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_interactive(self):
        """Run the orchestrator in interactive mode"""
        console.print(Panel("[bold blue]AI Newsletter Generator - Interactive Mode[/bold blue]", 
                           border_style="blue"))
        
        while True:
            console.print("\nOptions:")
            console.print("1. Generate newsletter")
            console.print("2. View configuration")
            console.print("3. Run quality check on existing newsletter")
            console.print("4. Schedule automatic generation")
            console.print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                theme = input("Enter newsletter theme (or press Enter for default): ").strip()
                theme = theme if theme else None
                self.generate_newsletter(theme)
            
            elif choice == "2":
                console.print(json.dumps(self.config, indent=2))
            
            elif choice == "3":
                console.print("[yellow]Quality check feature not implemented yet[/yellow]")
            
            elif choice == "4":
                self.schedule_newsletter()
            
            elif choice == "5":
                console.print("[green]Goodbye![/green]")
                break
            
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")

if __name__ == "__main__":
    orchestrator = NewsletterOrchestrator()
    
    # Check if running in interactive mode
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--interactive":
        orchestrator.run_interactive()
    else:
        # Generate a single newsletter
        report = orchestrator.generate_newsletter()
        console.print(f"[green]Newsletter generated successfully![/green]") 