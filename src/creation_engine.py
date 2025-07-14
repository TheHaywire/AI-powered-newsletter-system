"""
AI Newsletter Content Creation Engine
Handles summarization, insight generation, story structuring, and automated writing
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from rich.console import Console
from rich.progress import track
import openai
from transformers import pipeline
import markdown

console = Console()

@dataclass
class NewsletterSection:
    """Represents a section in the newsletter"""
    title: str
    content: str
    articles: List[Dict]
    insights: List[str]
    category: str

@dataclass
class Newsletter:
    """Represents a complete newsletter"""
    title: str
    subtitle: str
    sections: List[NewsletterSection]
    summary: str
    key_insights: List[str]
    generated_date: datetime
    word_count: int
    reading_time: int

class ContentCreationEngine:
    """Main content creation engine for generating newsletters"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Initialize summarization pipeline
        try:
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        except Exception as e:
            console.print(f"[yellow]Summarization model not available: {e}[/yellow]")
            self.summarizer = None
    
    def create_newsletter(self, articles: List[Dict], analysis_results: List[Dict], 
                         theme: str = "Technology & Innovation") -> Newsletter:
        """Create a complete newsletter from articles and analysis"""
        console.print(f"[blue]Creating newsletter with {len(articles)} articles...[/blue]")
        
        # Group articles by category
        categorized_articles = self._categorize_articles(articles, analysis_results)
        
        # Generate newsletter title and subtitle
        title, subtitle = self._generate_newsletter_header(theme, articles)
        
        # Create sections for each category
        sections = []
        for category, category_data in categorized_articles.items():
            section = self._create_section(category, category_data['articles'], 
                                         category_data['analysis'])
            sections.append(section)
        
        # Generate overall summary
        summary = self._generate_newsletter_summary(sections)
        
        # Extract key insights
        key_insights = self._extract_key_insights(sections)
        
        # Calculate metrics
        word_count = sum(len(section.content.split()) for section in sections)
        reading_time = max(1, word_count // 200)  # Assume 200 words per minute
        
        newsletter = Newsletter(
            title=title,
            subtitle=subtitle,
            sections=sections,
            summary=summary,
            key_insights=key_insights,
            generated_date=datetime.now(),
            word_count=word_count,
            reading_time=reading_time
        )
        
        console.print(f"[green]Created newsletter: {title}[/green]")
        return newsletter
    
    def _categorize_articles(self, articles: List, 
                           analysis_results: List) -> Dict[str, Dict]:
        """Categorize articles and their analysis results"""
        categorized = {}
        
        for article, analysis in zip(articles, analysis_results):
            # Handle both dict and dataclass objects
            if hasattr(article, 'get'):
                category = article.get('category', 'general')
            else:
                category = getattr(article, 'category', 'general')
            
            if category not in categorized:
                categorized[category] = {
                    'articles': [],
                    'analysis': []
                }
            
            categorized[category]['articles'].append(article)
            categorized[category]['analysis'].append(analysis)
        
        return categorized
    
    def _generate_newsletter_header(self, theme: str, articles: List) -> tuple:
        """Generate newsletter title and subtitle"""
        # Extract key topics from articles
        all_titles = []
        for article in articles:
            if hasattr(article, 'get'):
                all_titles.append(article.get('title', ''))
            else:
                all_titles.append(getattr(article, 'title', ''))
        
        key_topics = self._extract_common_topics(all_titles)
        
        # Generate title
        if key_topics:
            title = f"The {theme} Weekly: {key_topics[0].title()} & Beyond"
        else:
            title = f"The {theme} Weekly"
        
        # Generate subtitle
        article_count = len(articles)
        subtitle = f"Your curated digest of the top {article_count} stories in {theme.lower()}"
        
        return title, subtitle
    
    def _extract_common_topics(self, titles: List[str]) -> List[str]:
        """Extract common topics from article titles"""
        # Simple keyword extraction
        common_words = ['ai', 'artificial intelligence', 'tech', 'technology', 
                       'startup', 'business', 'innovation', 'machine learning']
        
        found_topics = []
        for word in common_words:
            count = sum(1 for title in titles if word.lower() in title.lower())
            if count >= len(titles) * 0.3:  # If 30% of articles mention it
                found_topics.append(word)
        
        return found_topics[:3]  # Return top 3
    
    def _create_section(self, category: str, articles: List, 
                       analysis_results: List) -> NewsletterSection:
        """Create a section for a specific category"""
        # Sort articles by relevance score
        sorted_data = sorted(zip(articles, analysis_results), 
                           key=lambda x: getattr(x[1], 'relevance_score', 0) if hasattr(x[1], 'relevance_score') else x[1].get('relevance_score', 0), reverse=True)
        
        articles, analysis_results = zip(*sorted_data) if sorted_data else ([], [])
        
        # Generate section title
        section_title = self._generate_section_title(category, articles)
        
        # Create content for each article
        article_contents = []
        insights = []
        
        for article, analysis in zip(articles, analysis_results):
            article_content = self._create_article_summary(article, analysis)
            article_contents.append(article_content)
            
            # Collect insights
            if hasattr(analysis, 'insights'):
                insights.extend(analysis.insights)
            elif analysis.get('insights'):
                insights.extend(analysis['insights'])
        
        # Combine article contents
        section_content = self._combine_article_contents(article_contents)
        
        return NewsletterSection(
            title=section_title,
            content=section_content,
            articles=articles,
            insights=insights[:5],  # Limit to top 5 insights
            category=category
        )
    
    def _generate_section_title(self, category: str, articles: List) -> str:
        """Generate a title for a section"""
        category_titles = {
            'technology': '🚀 Technology & Innovation',
            'business': '💼 Business & Finance',
            'science': '🔬 Science & Research',
            'general': '📰 Top Stories'
        }
        
        return category_titles.get(category.lower(), f"📋 {category.title()}")
    
    def _create_article_summary(self, article, analysis) -> str:
        """Create a summary for a single article (handles both dict and dataclass objects)"""
        # Handle both dict and dataclass objects
        if hasattr(article, 'get'):
            # Dictionary-like object
            title = article.get('title', '')
            content = article.get('content', '')
            source = article.get('source', 'Unknown')
            url = article.get('url', '')
        else:
            # Dataclass object
            title = getattr(article, 'title', '')
            content = getattr(article, 'content', '')
            source = getattr(article, 'source', 'Unknown')
            url = getattr(article, 'url', '')
        
        # Generate summary using AI or extractive method
        if self.summarizer and len(content) > 100:
            try:
                summary = self._generate_ai_summary(content)
            except Exception:
                summary = self._generate_extractive_summary(content)
        else:
            summary = self._generate_extractive_summary(content)
        
        # Format the article summary
        article_summary = f"""
### {title}

{summary}

**Source:** {source} | [Read More]({url})

---
"""
        return article_summary
    
    def _generate_ai_summary(self, content: str) -> str:
        """Generate summary using AI model"""
        if not self.summarizer:
            return self._generate_extractive_summary(content)
        
        # Truncate content if too long
        max_length = 1000
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        try:
            summary = self.summarizer(content, max_length=150, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            console.print(f"[yellow]AI summarization failed: {e}[/yellow]")
            return self._generate_extractive_summary(content)
    
    def _generate_extractive_summary(self, content: str) -> str:
        """Generate extractive summary using simple heuristics"""
        sentences = content.split('.')
        
        # Take first few sentences as summary
        if len(sentences) <= 3:
            return content
        
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences) + '.'
        
        return summary
    
    def _combine_article_contents(self, article_contents: List[str]) -> str:
        """Combine multiple article contents into a section"""
        return '\n\n'.join(article_contents)
    
    def _generate_newsletter_summary(self, sections: List[NewsletterSection]) -> str:
        """Generate overall newsletter summary"""
        total_articles = sum(len(section.articles) for section in sections)
        
        summary = f"""
This week's newsletter covers {total_articles} stories across {len(sections)} categories. 
Key highlights include emerging trends in technology, business developments, and scientific breakthroughs.
"""
        
        return summary.strip()
    
    def _extract_key_insights(self, sections: List[NewsletterSection]) -> List[str]:
        """Extract key insights from all sections"""
        all_insights = []
        
        for section in sections:
            all_insights.extend(section.insights)
        
        # Remove duplicates and limit
        unique_insights = list(set(all_insights))
        return unique_insights[:10]  # Return top 10 insights
    
    def format_newsletter(self, newsletter: Newsletter, format_type: str = "markdown") -> str:
        """Format newsletter for different output formats"""
        if format_type == "markdown":
            return self._format_markdown(newsletter)
        elif format_type == "html":
            return self._format_html(newsletter)
        elif format_type == "plain_text":
            return self._format_plain_text(newsletter)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_markdown(self, newsletter: Newsletter) -> str:
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
            md_content += f"## {section.title}\n\n"
            md_content += f"{section.content}\n\n"
        
        return md_content
    
    def _format_html(self, newsletter: Newsletter) -> str:
        """Format newsletter as HTML"""
        # Convert markdown to HTML
        md_content = self._format_markdown(newsletter)
        html_content = markdown.markdown(md_content)
        
        # Add HTML styling
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{newsletter.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .metadata {{ color: #7f8c8d; font-style: italic; margin-bottom: 30px; }}
        .insights {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        return html_template
    
    def _format_plain_text(self, newsletter: Newsletter) -> str:
        """Format newsletter as plain text"""
        text_content = f"""{newsletter.title}
{newsletter.subtitle}

Generated on {newsletter.generated_date.strftime('%B %d, %Y')}
{newsletter.word_count} words • {newsletter.reading_time} min read

{'='*50}

EXECUTIVE SUMMARY

{newsletter.summary}

KEY INSIGHTS

"""
        
        for insight in newsletter.key_insights:
            text_content += f"• {insight}\n"
        
        text_content += "\n" + "="*50 + "\n\n"
        
        # Add sections
        for section in newsletter.sections:
            text_content += f"{section.title}\n"
            text_content += "-" * len(section.title) + "\n\n"
            text_content += f"{section.content}\n\n"
        
        return text_content
    
    def save_newsletter(self, newsletter: Newsletter, filename: str, format_type: str = "markdown"):
        """Save newsletter to file"""
        content = self.format_newsletter(newsletter, format_type)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        console.print(f"[green]Saved newsletter to {filename}[/green]")
    
    def get_newsletter_metrics(self, newsletter: Newsletter) -> Dict[str, Any]:
        """Get metrics about the newsletter"""
        return {
            "title": newsletter.title,
            "word_count": newsletter.word_count,
            "reading_time": newsletter.reading_time,
            "sections": len(newsletter.sections),
            "total_articles": sum(len(section.articles) for section in newsletter.sections),
            "key_insights": len(newsletter.key_insights),
            "generated_date": newsletter.generated_date.isoformat()
        }

if __name__ == "__main__":
    # Example usage
    engine = ContentCreationEngine()
    
    # Sample data
    sample_articles = [
        {
            "title": "AI Breakthrough in Medical Diagnosis",
            "content": "Researchers have developed a new AI system that can diagnose diseases with 95% accuracy...",
            "category": "technology",
            "source": "Tech News",
            "url": "https://example.com/ai-medical"
        },
        {
            "title": "Startup Raises $50M in Series B Funding",
            "content": "A promising startup in the AI space has secured significant funding...",
            "category": "business",
            "source": "Business Daily",
            "url": "https://example.com/startup-funding"
        }
    ]
    
    sample_analysis = [
        {
            "relevance_score": 0.9,
            "insights": ["High relevance to AI industry", "Positive sentiment"]
        },
        {
            "relevance_score": 0.8,
            "insights": ["Significant business impact", "Neutral sentiment"]
        }
    ]
    
    # Create newsletter
    newsletter = engine.create_newsletter(sample_articles, sample_analysis)
    
    # Save in different formats
    engine.save_newsletter(newsletter, "newsletter.md", "markdown")
    engine.save_newsletter(newsletter, "newsletter.html", "html")
    engine.save_newsletter(newsletter, "newsletter.txt", "plain_text")
    
    # Get metrics
    metrics = engine.get_newsletter_metrics(newsletter)
    console.print(f"Newsletter metrics: {metrics}") 