#!/usr/bin/env python3
"""
Simplified AI Newsletter Demo
Shows how the system works without heavy ML dependencies
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dataclasses import dataclass
from typing import List, Dict, Any

console = Console()

@dataclass
class DemoArticle:
    """Demo article for demonstration"""
    title: str
    url: str
    content: str
    author: str
    published_date: datetime
    source: str
    category: str
    sentiment_score: float = 0.0
    relevance_score: float = 0.0

@dataclass
class DemoNewsletter:
    """Demo newsletter for demonstration"""
    title: str
    subtitle: str
    sections: List[Dict]
    summary: str
    key_insights: List[str]
    generated_date: datetime
    word_count: int
    reading_time: int

class SimpleNewsletterDemo:
    """Simplified newsletter demo system"""
    
    def __init__(self):
        self.demo_articles = self._create_demo_articles()
        self.demo_analysis = self._create_demo_analysis()
        
    def _create_demo_articles(self) -> List[DemoArticle]:
        """Create demo articles for demonstration"""
        return [
            DemoArticle(
                title="AI Breakthrough in Medical Diagnosis",
                url="https://example.com/ai-medical",
                content="Researchers at Stanford University have developed a new AI system that can diagnose diseases with 95% accuracy, significantly outperforming traditional diagnostic methods. The system uses advanced machine learning algorithms to analyze medical imaging data and patient symptoms.",
                author="Dr. Sarah Johnson",
                published_date=datetime.now() - timedelta(days=1),
                source="Tech News Daily",
                category="technology",
                sentiment_score=0.8,
                relevance_score=0.9
            ),
            DemoArticle(
                title="Quantum Computing Milestone Achieved",
                url="https://example.com/quantum-breakthrough",
                content="IBM has announced a major breakthrough in quantum computing, achieving quantum advantage in solving complex optimization problems. This development could revolutionize fields ranging from drug discovery to financial modeling.",
                author="Dr. Michael Chen",
                published_date=datetime.now() - timedelta(days=2),
                source="IBM Research",
                category="technology",
                sentiment_score=0.7,
                relevance_score=0.8
            ),
            DemoArticle(
                title="Startup Raises $50M in Series B Funding",
                url="https://example.com/startup-funding",
                content="An innovative AI startup focused on natural language processing has secured $50 million in Series B funding. The company plans to expand its team and accelerate product development.",
                author="Business Reporter",
                published_date=datetime.now() - timedelta(days=1),
                source="Business Daily",
                category="business",
                sentiment_score=0.6,
                relevance_score=0.7
            ),
            DemoArticle(
                title="New AI Ethics Framework Released",
                url="https://example.com/ai-ethics",
                content="A consortium of leading tech companies has released a comprehensive framework for responsible AI development. The guidelines address bias mitigation, transparency, and accountability in AI systems.",
                author="AI Ethics Consortium",
                published_date=datetime.now() - timedelta(days=3),
                source="AI Ethics Consortium",
                category="technology",
                sentiment_score=0.5,
                relevance_score=0.8
            ),
            DemoArticle(
                title="Tech Giant Acquires AI Research Lab",
                url="https://example.com/ai-acquisition",
                content="A major technology company has acquired a prominent AI research laboratory for $200 million. The acquisition will strengthen the company's position in the competitive AI market.",
                author="Tech Business Reporter",
                published_date=datetime.now() - timedelta(days=2),
                source="Tech Business News",
                category="business",
                sentiment_score=0.4,
                relevance_score=0.6
            )
        ]
    
    def _create_demo_analysis(self) -> List[Dict]:
        """Create demo analysis results"""
        return [
            {
                "sentiment_score": 0.8,
                "sentiment_label": "positive",
                "relevance_score": 0.9,
                "bias_score": 0.2,
                "fact_check_score": 0.95,
                "key_topics": ["AI", "medical diagnosis", "machine learning"],
                "summary": "Researchers develop AI system with 95% accuracy for medical diagnosis.",
                "insights": ["High relevance to AI industry", "Positive sentiment", "Significant medical impact"]
            },
            {
                "sentiment_score": 0.7,
                "sentiment_label": "positive",
                "relevance_score": 0.8,
                "bias_score": 0.3,
                "fact_check_score": 0.9,
                "key_topics": ["quantum computing", "IBM", "optimization"],
                "summary": "IBM achieves quantum advantage in optimization problems.",
                "insights": ["Major technological breakthrough", "Positive sentiment", "Commercial applications"]
            },
            {
                "sentiment_score": 0.6,
                "sentiment_label": "positive",
                "relevance_score": 0.7,
                "bias_score": 0.1,
                "fact_check_score": 0.85,
                "key_topics": ["startup", "funding", "AI"],
                "summary": "AI startup secures $50M in Series B funding.",
                "insights": ["Significant business impact", "Positive sentiment", "Market confidence"]
            },
            {
                "sentiment_score": 0.5,
                "sentiment_label": "neutral",
                "relevance_score": 0.8,
                "bias_score": 0.4,
                "fact_check_score": 0.9,
                "key_topics": ["AI ethics", "framework", "responsible AI"],
                "summary": "Tech companies release AI ethics framework.",
                "insights": ["Important for industry", "Neutral sentiment", "Regulatory implications"]
            },
            {
                "sentiment_score": 0.4,
                "sentiment_label": "neutral",
                "relevance_score": 0.6,
                "bias_score": 0.2,
                "fact_check_score": 0.8,
                "key_topics": ["acquisition", "AI research", "tech company"],
                "summary": "Tech company acquires AI research lab for $200M.",
                "insights": ["Market consolidation", "Neutral sentiment", "Strategic move"]
            }
        ]
    
    def run_demo(self):
        """Run the complete newsletter generation demo"""
        console.print(Panel("[bold blue]AI Newsletter Generator - Live Demo[/bold blue]", border_style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Research Phase
            task1 = progress.add_task("🔍 Researching trending topics...", total=None)
            topics = self._discover_trending_topics()
            progress.update(task1, description=f"📚 Discovered {len(topics)} trending topics")
            
            # Step 2: Content Collection
            task2 = progress.add_task("📰 Collecting articles...", total=None)
            articles = self._collect_articles(topics)
            progress.update(task2, description=f"📄 Collected {len(articles)} articles")
            
            # Step 3: Content Analysis
            task3 = progress.add_task("🔬 Analyzing content...", total=None)
            analysis_results = self._analyze_articles(articles)
            progress.update(task3, description=f"📊 Analyzed {len(analysis_results)} articles")
            
            # Step 4: Content Creation
            task4 = progress.add_task("✍️ Creating newsletter...", total=None)
            newsletter = self._create_newsletter(articles, analysis_results)
            progress.update(task4, description=f"📧 Created newsletter: {newsletter.title}")
        
        # Step 5: Quality Check
        quality_report = self._perform_quality_check(newsletter, analysis_results)
        
        # Step 6: Save Outputs
        self._save_outputs(newsletter, articles, analysis_results, quality_report)
        
        # Step 7: Show Results
        self._show_demo_results(newsletter, articles, analysis_results, quality_report)
        
        return newsletter
    
    def _discover_trending_topics(self) -> List[str]:
        """Simulate trending topic discovery"""
        return [
            "Artificial Intelligence",
            "Machine Learning", 
            "Quantum Computing",
            "AI Ethics",
            "Tech Funding",
            "Startup News"
        ]
    
    def _collect_articles(self, topics: List[str]) -> List[DemoArticle]:
        """Simulate article collection"""
        # Filter articles based on topics
        relevant_articles = []
        for article in self.demo_articles:
            for topic in topics:
                if topic.lower() in article.title.lower() or topic.lower() in article.content.lower():
                    relevant_articles.append(article)
                    break
        
        return relevant_articles[:5]  # Return top 5 articles
    
    def _analyze_articles(self, articles: List[DemoArticle]) -> List[Dict]:
        """Simulate article analysis"""
        return self.demo_analysis[:len(articles)]
    
    def _create_newsletter(self, articles: List[DemoArticle], analysis: List[Dict]) -> DemoNewsletter:
        """Create newsletter from articles and analysis"""
        # Group articles by category
        categories = {}
        for article, analysis_result in zip(articles, analysis):
            if article.category not in categories:
                categories[article.category] = []
            categories[article.category].append({
                'article': article,
                'analysis': analysis_result
            })
        
        # Create sections
        sections = []
        for category, items in categories.items():
            section_content = []
            for item in items:
                article = item['article']
                analysis = item['analysis']
                
                section_content.append(f"""
### {article.title}

{analysis['summary']}

**Source:** {article.source} | [Read More]({article.url})

---
""")
            
            sections.append({
                'title': f"🚀 {category.title()}" if category == 'technology' else f"💼 {category.title()}",
                'content': '\n'.join(section_content),
                'articles': [item['article'] for item in items],
                'insights': [insight for item in items for insight in item['analysis']['insights'][:2]]
            })
        
        # Generate title and summary
        title = "The Technology & Innovation Weekly: AI & Beyond"
        subtitle = f"Your curated digest of the top {len(articles)} stories in technology & innovation"
        
        # Calculate metrics
        word_count = sum(len(article.content.split()) for article in articles)
        reading_time = max(1, word_count // 200)
        
        # Extract key insights
        all_insights = []
        for analysis_result in analysis:
            if isinstance(analysis_result, dict) and 'insights' in analysis_result:
                all_insights.extend(analysis_result['insights'])
        key_insights = list(set(all_insights))[:5]
        
        summary = f"This week's newsletter covers {len(articles)} stories across {len(categories)} categories. Key highlights include emerging trends in technology, business developments, and scientific breakthroughs."
        
        return DemoNewsletter(
            title=title,
            subtitle=subtitle,
            sections=sections,
            summary=summary,
            key_insights=key_insights,
            generated_date=datetime.now(),
            word_count=word_count,
            reading_time=reading_time
        )
    
    def _perform_quality_check(self, newsletter: DemoNewsletter, analysis: List[Dict]) -> Dict[str, Any]:
        """Perform quality checks"""
        quality_report = {
            "overall_score": 0.0,
            "checks_passed": 0,
            "total_checks": 5,
            "issues": [],
            "recommendations": []
        }
        
        # Check article count
        total_articles = sum(len(section['articles']) for section in newsletter.sections)
        if total_articles >= 5:
            quality_report["checks_passed"] += 1
        else:
            quality_report["issues"].append("Insufficient articles")
            quality_report["recommendations"].append("Collect more articles")
        
        # Check relevance scores
        high_relevance = sum(1 for result in analysis if result['relevance_score'] >= 0.6)
        if high_relevance == len(analysis):
            quality_report["checks_passed"] += 1
        else:
            quality_report["issues"].append("Some articles have low relevance")
            quality_report["recommendations"].append("Filter low-relevance articles")
        
        # Check bias scores
        low_bias = sum(1 for result in analysis if result['bias_score'] <= 0.7)
        if low_bias == len(analysis):
            quality_report["checks_passed"] += 1
        else:
            quality_report["issues"].append("Some articles show potential bias")
            quality_report["recommendations"].append("Review high-bias articles")
        
        # Check content length
        if 500 <= newsletter.word_count <= 3000:
            quality_report["checks_passed"] += 1
        else:
            quality_report["issues"].append("Newsletter length outside optimal range")
            quality_report["recommendations"].append("Adjust content length")
        
        # Check source diversity
        sources = set()
        for section in newsletter.sections:
            for article in section['articles']:
                sources.add(article.source)
        
        if len(sources) >= 3:
            quality_report["checks_passed"] += 1
        else:
            quality_report["issues"].append("Limited source diversity")
            quality_report["recommendations"].append("Include more diverse sources")
        
        quality_report["overall_score"] = quality_report["checks_passed"] / quality_report["total_checks"]
        
        return quality_report
    
    def _save_outputs(self, newsletter: DemoNewsletter, articles: List[DemoArticle], 
                     analysis: List[Dict], quality_report: Dict):
        """Save demo outputs"""
        # Create output directory
        Path("output").mkdir(exist_ok=True)
        
        # Save newsletter in markdown format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        markdown_content = self._format_newsletter_markdown(newsletter)
        with open(f"output/newsletter_demo_{timestamp}.md", 'w') as f:
            f.write(markdown_content)
        
        # Save analysis results
        analysis_data = []
        for article, analysis_result in zip(articles, analysis):
            analysis_data.append({
                'title': article.title,
                'sentiment_score': analysis_result['sentiment_score'],
                'relevance_score': analysis_result['relevance_score'],
                'bias_score': analysis_result['bias_score'],
                'key_topics': analysis_result['key_topics'],
                'insights': analysis_result['insights']
            })
        
        with open(f"output/analysis_demo_{timestamp}.json", 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        # Save quality report
        with open(f"output/quality_report_demo_{timestamp}.json", 'w') as f:
            json.dump(quality_report, f, indent=2)
    
    def _format_newsletter_markdown(self, newsletter: DemoNewsletter) -> str:
        """Format newsletter as markdown"""
        md_content = f"""# {newsletter.title}

{newsletter.subtitle}

*Generated on {newsletter.generated_date.strftime('%B %d, %Y')} • {newsletter.word_count} words • {newsletter.reading_time} min read*

---

## Executive Summary

{newsletter.summary}

## Key Insights

"""
        
        for insight in newsletter.key_insights:
            md_content += f"- {insight}\n"
        
        md_content += "\n---\n\n"
        
        # Add sections
        for section in newsletter.sections:
            md_content += f"## {section['title']}\n\n"
            md_content += f"{section['content']}\n\n"
        
        return md_content
    
    def _show_demo_results(self, newsletter: DemoNewsletter, articles: List[DemoArticle], 
                          analysis: List[Dict], quality_report: Dict):
        """Show demo results"""
        console.print(Panel(f"[bold green]Demo Completed Successfully![/bold green]\n{newsletter.title}", 
                           border_style="green"))
        
        # Show summary table
        table = Table(title="Newsletter Generation Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Newsletter Title", newsletter.title)
        table.add_row("Total Articles", str(sum(len(section['articles']) for section in newsletter.sections)))
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
        
        # Show key insights
        console.print("\n[blue]Key Insights Generated:[/blue]")
        for insight in newsletter.key_insights:
            console.print(f"• {insight}")
        
        console.print(f"\n[green]✓ Newsletter saved to output/newsletter_demo_*.md[/green]")
        console.print(f"[green]✓ Analysis results saved to output/analysis_demo_*.json[/green]")
        console.print(f"[green]✓ Quality report saved to output/quality_report_demo_*.json[/green]")

def main():
    """Main demo function"""
    demo = SimpleNewsletterDemo()
    newsletter = demo.run_demo()
    
    # Show the generated newsletter
    console.print("\n" + "="*80)
    console.print("[bold blue]GENERATED NEWSLETTER PREVIEW[/bold blue]")
    console.print("="*80)
    
    # Read and display the generated newsletter
    output_files = list(Path("output").glob("newsletter_demo_*.md"))
    if output_files:
        latest_file = max(output_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file, 'r') as f:
            content = f.read()
        
        # Show first 500 characters
        preview = content[:500] + "..." if len(content) > 500 else content
        console.print(preview)
        
        console.print(f"\n[blue]Full newsletter available at: {latest_file}[/blue]")

if __name__ == "__main__":
    main() 