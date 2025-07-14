"""
AI Newsletter Research Engine
Handles topic discovery, source identification, and content aggregation
"""

import requests
import feedparser
import newspaper
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from rich.console import Console
from rich.progress import track

console = Console()

@dataclass
class Article:
    """Represents a collected article with metadata"""
    title: str
    url: str
    content: str
    author: str
    published_date: datetime
    source: str
    category: str
    sentiment_score: float = 0.0
    relevance_score: float = 0.0

class ResearchEngine:
    """Main research engine for discovering and collecting content"""
    
    def __init__(self, config_path: str = "config/research_config.json"):
        self.config = self._load_config(config_path)
        self.articles = []
        self.trending_topics = []
        self.sources = self.config.get('sources', {})
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load research configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]Config file {config_path} not found. Using defaults.[/red]")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for research sources"""
        return {
            "sources": {
                "tech_news": [
                    "https://techcrunch.com/feed/",
                    "https://www.theverge.com/rss/index.xml",
                    "https://feeds.arstechnica.com/arstechnica/index"
                ],
                "business_news": [
                    "https://feeds.bloomberg.com/markets/news.rss",
                    "https://www.ft.com/rss/home"
                ],
                "general_news": [
                    "https://feeds.bbci.co.uk/news/rss.xml",
                    "https://rss.cnn.com/rss/edition.rss"
                ]
            },
            "keywords": [
                "artificial intelligence", "machine learning", "startup", 
                "technology", "innovation", "business", "finance"
            ],
            "max_articles_per_source": 10,
            "date_range_days": 7,
            "api_keys": {
                "news_api": "2a1663b6af254eb184719e666a40be47" # Add your NewsAPI key here
            },
            "excluded_domains": [
                "twitter.com", "reddit.com", "facebook.com" # Add domains to exclude
            ]
        }
    
    def discover_trending_topics(self) -> List[str]:
        """Discover trending topics using various APIs and sources"""
        console.print("[blue]Discovering trending topics...[/blue]")
        
        topics = []
        
        # Get trending topics from Twitter (if API available)
        try:
            topics.extend(self._get_twitter_trends())
        except Exception as e:
            console.print(f"[yellow]Twitter trends unavailable: {e}[/yellow]")
        
        # Get trending topics from Reddit
        try:
            topics.extend(self._get_reddit_trends())
        except Exception as e:
            console.print(f"[yellow]Reddit trends unavailable: {e}[/yellow]")
        
        # Get trending topics from Google Trends
        try:
            topics.extend(self._get_google_trends())
        except Exception as e:
            console.print(f"[yellow]Google trends unavailable: {e}[/yellow]")
        
        self.trending_topics = list(set(topics))  # Remove duplicates
        console.print(f"[green]Discovered {len(self.trending_topics)} trending topics[/green]")
        return self.trending_topics
    
    def _get_twitter_trends(self) -> List[str]:
        """Get trending topics from Twitter"""
        # This would require Twitter API credentials
        # For demo purposes, returning sample trends
        return [
            "AI regulation", "ChatGPT updates", "Tech layoffs",
            "Cryptocurrency", "Climate tech", "Web3"
        ]
    
    def _get_reddit_trends(self) -> List[str]:
        """Get trending topics from Reddit"""
        # This would require Reddit API
        # For demo purposes, returning sample trends
        return [
            "Machine learning breakthroughs", "Startup funding",
            "Tech industry news", "Programming languages"
        ]
    
    def _get_google_trends(self) -> List[str]:
        """Get trending topics from Google Trends"""
        # This would require pytrends library
        # For demo purposes, returning sample trends
        return [
            "Artificial intelligence", "Remote work", "Cybersecurity",
            "Sustainable technology", "Digital transformation"
        ]
    
    def collect_articles(self, topics: List[str] = None) -> List[Article]:
        """Collect articles from various sources based on topics"""
        if topics is None:
            topics = self.trending_topics
        
        console.print(f"[blue]Collecting articles for {len(topics)} topics...[/blue]")
        
        all_articles = []
        
        # Collect from RSS feeds
        for category, feeds in self.sources.items():
            for feed_url in track(feeds, description=f"Processing {category} feeds"):
                try:
                    articles = self._collect_from_rss(feed_url, category, topics)
                    all_articles.extend(articles)
                except Exception as e:
                    console.print(f"[red]Error collecting from {feed_url}: {e}[/red]")
        
        # Collect from news APIs
        try:
            api_articles = self._collect_from_news_api(topics)
            all_articles.extend(api_articles)
        except Exception as e:
            console.print(f"[red]Error collecting from news API: {e}[/red]")
        
        # Remove duplicates and filter by date
        filtered_articles = self._filter_articles(all_articles)
        
        self.articles = filtered_articles
        console.print(f"[green]Collected {len(self.articles)} articles[/green]")
        return self.articles
    
    def _collect_from_rss(self, feed_url: str, category: str, topics: List[str]) -> List[Article]:
        """Collect articles from RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:self.config.get('max_articles_per_source', 10)]:
                # Check if article is relevant to our topics
                if self._is_relevant(entry.title + " " + entry.get('summary', ''), topics):
                    article = Article(
                        title=entry.title,
                        url=entry.link,
                        content=self._extract_content(entry.link),
                        author=entry.get('author', 'Unknown'),
                        published_date=self._parse_date(entry.get('published', '')),
                        source=feed.feed.get('title', 'Unknown'),
                        category=category
                    )
                    articles.append(article)
        
        except Exception as e:
            console.print(f"[red]Error parsing RSS feed {feed_url}: {e}[/red]")
        
        return articles
    
    def _collect_from_news_api(self, topics: List[str]) -> List[Article]:
        """Collect articles from News API"""
        articles = []
        api_key = self.config.get("api_keys", {}).get("news_api", "")
        if not api_key:
            console.print("[yellow]No NewsAPI key found in config. Skipping NewsAPI collection.[/yellow]")
            return articles

        endpoint = "https://newsapi.org/v2/everything"
        headers = {"Authorization": api_key}
        max_articles = self.config.get('max_articles_per_source', 10)
        date_from = (datetime.now() - timedelta(days=self.config.get('date_range_days', 7))).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")

        for topic in topics:
            params = {
                "q": topic,
                "from": date_from,
                "to": date_to,
                "language": "en",
                "sortBy": "relevancy",
                "pageSize": max_articles,
            }
            try:
                response = requests.get(endpoint, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                for item in data.get("articles", []):
                    url = item.get("url", "")
                    if any(excl in url for excl in self.config.get("excluded_domains", [])):
                        continue
                    article = Article(
                        title=item.get("title", ""),
                        url=url,
                        content=item.get("content", "") or item.get("description", ""),
                        author=item.get("author", "Unknown"),
                        published_date=self._parse_date(item.get("publishedAt", "")),
                        source=item.get("source", {}).get("name", "NewsAPI"),
                        category="news_api"
                    )
                    articles.append(article)
            except Exception as e:
                console.print(f"[red]Error fetching from NewsAPI for topic '{topic}': {e}[/red]")

        return articles
    
    def _is_relevant(self, text: str, topics: List[str]) -> bool:
        """Check if text is relevant to given topics"""
        text_lower = text.lower()
        return any(topic.lower() in text_lower for topic in topics)
    
    def _extract_content(self, url: str) -> str:
        """Extract article content from URL"""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            console.print(f"[yellow]Could not extract content from {url}: {e}[/yellow]")
            return ""
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            # Try common date formats
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            return datetime.now()
        except Exception:
            return datetime.now()
    
    def _filter_articles(self, articles: List[Article]) -> List[Article]:
        """Filter articles by date and remove duplicates"""
        cutoff_date = datetime.now() - timedelta(days=self.config.get('date_range_days', 7))
        
        # Filter by date
        recent_articles = [a for a in articles if a.published_date >= cutoff_date]
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        
        for article in recent_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)
        
        return unique_articles
    
    def save_articles(self, filename: str = "collected_articles.json"):
        """Save collected articles to JSON file"""
        articles_data = []
        
        for article in self.articles:
            articles_data.append({
                'title': article.title,
                'url': article.url,
                'content': article.content,
                'author': article.author,
                'published_date': article.published_date.isoformat(),
                'source': article.source,
                'category': article.category,
                'sentiment_score': article.sentiment_score,
                'relevance_score': article.relevance_score
            })
        
        with open(filename, 'w') as f:
            json.dump(articles_data, f, indent=2)
        
        console.print(f"[green]Saved {len(self.articles)} articles to {filename}[/green]")
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Generate a summary of the research findings"""
        if not self.articles:
            return {"error": "No articles collected"}
        
        summary = {
            "total_articles": len(self.articles),
            "sources": list(set(a.source for a in self.articles)),
            "categories": list(set(a.category for a in self.articles)),
            "date_range": {
                "earliest": min(a.published_date for a in self.articles).isoformat(),
                "latest": max(a.published_date for a in self.articles).isoformat()
            },
            "trending_topics": self.trending_topics,
            "top_sources": self._get_top_sources(),
            "top_categories": self._get_top_categories()
        }
        
        return summary
    
    def _get_top_sources(self) -> List[Dict[str, Any]]:
        """Get top sources by article count"""
        source_counts = {}
        for article in self.articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1
        
        return [{"source": source, "count": count} 
                for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)]

    def _get_top_categories(self) -> List[Dict[str, Any]]:
        """Get top categories by article count"""
        category_counts = {}
        for article in self.articles:
            category_counts[article.category] = category_counts.get(article.category, 0) + 1
        
        return [{"category": category, "count": count} 
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)]

if __name__ == "__main__":
    # Example usage
    engine = ResearchEngine()
    
    # Discover trending topics
    topics = engine.discover_trending_topics()
    console.print(f"Trending topics: {topics}")
    
    # Collect articles
    articles = engine.collect_articles(topics)
    
    # Save articles
    engine.save_articles()
    
    # Get summary
    summary = engine.get_research_summary()
    console.print(f"Research summary: {summary}") 