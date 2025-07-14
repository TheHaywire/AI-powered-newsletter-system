"""
AI Newsletter Analysis Engine
Handles sentiment analysis, fact-checking, relevance scoring, and bias detection
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from datetime import datetime
from rich.console import Console
from rich.progress import track
from dataclasses import dataclass

console = Console()

@dataclass
class AnalysisResult:
    """Represents analysis results for an article"""
    article_id: str
    sentiment_score: float
    sentiment_label: str
    relevance_score: float
    bias_score: float
    fact_check_score: float
    key_topics: List[str]
    summary: str
    insights: List[str]

class AnalysisEngine:
    """Main analysis engine for processing collected articles"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Load fact-checking database (simplified)
        self.fact_check_db = self._load_fact_check_database()
        
    def _load_fact_check_database(self) -> Dict[str, Any]:
        """Load fact-checking database with known facts and sources"""
        return {
            "ai_facts": {
                "openai_founded": "2015",
                "chatgpt_released": "2022",
                "gpt4_released": "2023"
            },
            "tech_companies": {
                "apple_founded": "1976",
                "google_founded": "1998",
                "facebook_founded": "2004"
            },
            "reliable_sources": [
                "reuters.com", "ap.org", "bbc.com", "npr.org",
                "nature.com", "science.org", "arxiv.org"
            ]
        }
    
    def analyze_articles(self, articles: List) -> List[AnalysisResult]:
        """Analyze a list of articles and return analysis results"""
        console.print(f"[blue]Analyzing {len(articles)} articles...[/blue]")
        
        results = []
        
        for article in track(articles, description="Analyzing articles"):
            try:
                result = self._analyze_single_article(article)
                results.append(result)
            except Exception as e:
                # Handle both dict and dataclass objects
                title = getattr(article, 'title', None) or article.get('title', 'Unknown') if hasattr(article, 'get') else 'Unknown'
                console.print(f"[red]Error analyzing article {title}: {e}[/red]")
        
        console.print(f"[green]Completed analysis of {len(results)} articles[/green]")
        return results
    
    def _analyze_single_article(self, article) -> AnalysisResult:
        """Analyze a single article (handles both dict and dataclass objects)"""
        # Handle both dict and dataclass objects
        if hasattr(article, 'get'):
            # Dictionary-like object
            content = article.get('content', '')
            title = article.get('title', '')
            category = article.get('category', '')
            url = article.get('url', '')
        else:
            # Dataclass object
            content = getattr(article, 'content', '')
            title = getattr(article, 'title', '')
            category = getattr(article, 'category', '')
            url = getattr(article, 'url', '')
        
        full_text = f"{title} {content}"
        
        # Sentiment analysis
        sentiment_score, sentiment_label = self._analyze_sentiment(full_text)
        
        # Relevance scoring
        relevance_score = self._calculate_relevance_score(full_text, category)
        
        # Bias detection
        bias_score = self._detect_bias(full_text)
        
        # Fact checking
        fact_check_score = self._fact_check_article(full_text)
        
        # Extract key topics
        key_topics = self._extract_key_topics(full_text)
        
        # Generate summary
        summary = self._generate_summary(content)
        
        # Generate insights
        insights = self._generate_insights(full_text, sentiment_score, bias_score)
        
        return AnalysisResult(
            article_id=url,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            relevance_score=relevance_score,
            bias_score=bias_score,
            fact_check_score=fact_check_score,
            key_topics=key_topics,
            summary=summary,
            insights=insights
        )
    
    def _analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Analyze sentiment of text using multiple methods"""
        # VADER sentiment analysis
        vader_scores = self.sentiment_analyzer.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combine scores (weighted average)
        combined_score = (vader_compound * 0.7) + (textblob_polarity * 0.3)
        
        # Determine label
        if combined_score >= 0.05:
            label = "positive"
        elif combined_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        
        return combined_score, label
    
    def _calculate_relevance_score(self, text: str, category: str) -> float:
        """Calculate relevance score based on content and category"""
        # Extract keywords from text
        doc = self.nlp(text.lower())
        
        # Define relevant keywords for different categories
        category_keywords = {
            "technology": ["ai", "artificial intelligence", "machine learning", "tech", "software", "hardware"],
            "business": ["startup", "funding", "investment", "market", "revenue", "profit"],
            "science": ["research", "study", "discovery", "scientific", "experiment"],
            "general": ["news", "update", "announcement", "development"]
        }
        
        relevant_keywords = category_keywords.get(category.lower(), category_keywords["general"])
        
        # Count keyword matches
        keyword_matches = sum(1 for token in doc if token.text in relevant_keywords)
        
        # Calculate relevance score (0-1)
        max_possible_matches = len(relevant_keywords)
        relevance_score = min(keyword_matches / max_possible_matches, 1.0)
        
        return relevance_score
    
    def _detect_bias(self, text: str) -> float:
        """Detect potential bias in text"""
        bias_indicators = {
            "emotional_language": [
                "amazing", "incredible", "terrible", "horrible", "fantastic",
                "outrageous", "shocking", "stunning", "devastating"
            ],
            "subjective_phrases": [
                "clearly", "obviously", "undoubtedly", "certainly",
                "everyone knows", "it's clear that", "without doubt"
            ],
            "loaded_words": [
                "radical", "extreme", "dangerous", "threat", "crisis",
                "revolutionary", "breakthrough", "game-changing"
            ]
        }
        
        text_lower = text.lower()
        bias_score = 0.0
        
        # Check for emotional language
        emotional_count = sum(1 for word in bias_indicators["emotional_language"] 
                            if word in text_lower)
        
        # Check for subjective phrases
        subjective_count = sum(1 for phrase in bias_indicators["subjective_phrases"] 
                             if phrase in text_lower)
        
        # Check for loaded words
        loaded_count = sum(1 for word in bias_indicators["loaded_words"] 
                          if word in text_lower)
        
        # Calculate bias score (0-1, higher = more biased)
        total_indicators = len(bias_indicators["emotional_language"]) + \
                          len(bias_indicators["subjective_phrases"]) + \
                          len(bias_indicators["loaded_words"])
        
        total_found = emotional_count + subjective_count + loaded_count
        bias_score = min(total_found / total_indicators, 1.0)
        
        return bias_score
    
    def _fact_check_article(self, text: str) -> float:
        """Perform basic fact checking on article content"""
        fact_check_score = 1.0  # Start with perfect score
        
        # Check for specific facts against our database
        for category, facts in self.fact_check_db.items():
            if category in ["ai_facts", "tech_companies"]:
                for fact, correct_value in facts.items():
                    # Look for the fact in the text
                    if fact.replace("_", " ") in text.lower():
                        # This is a simplified check - in reality, you'd need more sophisticated parsing
                        # For now, we'll assume the fact is mentioned correctly
                        pass
        
        # Check for citation patterns
        citation_patterns = [
            r'according to [^,]+',
            r'[^,]+ reports',
            r'study by [^,]+',
            r'research from [^,]+'
        ]
        
        citations_found = sum(1 for pattern in citation_patterns 
                            if re.search(pattern, text, re.IGNORECASE))
        
        # Reduce score if no citations found
        if citations_found == 0:
            fact_check_score *= 0.8
        
        return fact_check_score
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text using NLP"""
        doc = self.nlp(text)
        
        # Extract noun phrases and named entities
        topics = []
        
        # Named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PERSON', 'GPE', 'PRODUCT']:
                topics.append(ent.text)
        
        # Noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to 3 words max
                topics.append(chunk.text)
        
        # Remove duplicates and limit to top 10
        unique_topics = list(set(topics))
        return unique_topics[:10]
    
    def _generate_summary(self, content: str) -> str:
        """Generate a concise summary of the content"""
        if len(content) < 100:
            return content
        
        # Simple extractive summarization
        sentences = content.split('.')
        if len(sentences) <= 3:
            return content
        
        # Take first few sentences as summary
        summary_sentences = sentences[:3]
        summary = '. '.join(summary_sentences) + '.'
        
        return summary
    
    def _generate_insights(self, text: str, sentiment_score: float, bias_score: float) -> List[str]:
        """Generate insights about the article"""
        insights = []
        
        # Sentiment-based insights
        if sentiment_score > 0.3:
            insights.append("Article has a positive tone")
        elif sentiment_score < -0.3:
            insights.append("Article has a negative tone")
        else:
            insights.append("Article has a neutral tone")
        
        # Bias-based insights
        if bias_score > 0.5:
            insights.append("Article shows potential bias - verify claims")
        else:
            insights.append("Article appears relatively balanced")
        
        # Content-based insights
        if len(text) > 1000:
            insights.append("Comprehensive coverage of the topic")
        elif len(text) < 300:
            insights.append("Brief overview - may need additional sources")
        
        # Check for data/statistics
        if re.search(r'\d+%|\d+ percent|\d+ million|\d+ billion', text):
            insights.append("Contains statistical data")
        
        return insights
    
    def get_analysis_summary(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate summary of analysis results"""
        if not results:
            return {"error": "No analysis results"}
        
        summary = {
            "total_articles": len(results),
            "sentiment_distribution": self._get_sentiment_distribution(results),
            "average_scores": {
                "sentiment": np.mean([r.sentiment_score for r in results]),
                "relevance": np.mean([r.relevance_score for r in results]),
                "bias": np.mean([r.bias_score for r in results]),
                "fact_check": np.mean([r.fact_check_score for r in results])
            },
            "top_topics": self._get_top_topics(results),
            "quality_metrics": self._get_quality_metrics(results)
        }
        
        return summary
    
    def _get_sentiment_distribution(self, results: List[AnalysisResult]) -> Dict[str, int]:
        """Get distribution of sentiment labels"""
        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        
        for result in results:
            distribution[result.sentiment_label] += 1
        
        return distribution
    
    def _get_top_topics(self, results: List[AnalysisResult]) -> List[str]:
        """Get most common topics across all articles"""
        all_topics = []
        for result in results:
            all_topics.extend(result.key_topics)
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Return top 10 topics
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:10]]
    
    def _get_quality_metrics(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Get quality metrics for the analyzed articles"""
        high_quality = sum(1 for r in results 
                          if r.relevance_score > 0.7 and r.fact_check_score > 0.8)
        
        low_bias = sum(1 for r in results if r.bias_score < 0.3)
        
        return {
            "high_quality_articles": high_quality,
            "low_bias_articles": low_bias,
            "quality_percentage": (high_quality / len(results)) * 100 if results else 0,
            "low_bias_percentage": (low_bias / len(results)) * 100 if results else 0
        }
    
    def save_analysis_results(self, results: List[AnalysisResult], filename: str = "analysis_results.json"):
        """Save analysis results to JSON file"""
        results_data = []
        
        for result in results:
            results_data.append({
                'article_id': result.article_id,
                'sentiment_score': result.sentiment_score,
                'sentiment_label': result.sentiment_label,
                'relevance_score': result.relevance_score,
                'bias_score': result.bias_score,
                'fact_check_score': result.fact_check_score,
                'key_topics': result.key_topics,
                'summary': result.summary,
                'insights': result.insights
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        console.print(f"[green]Saved analysis results to {filename}[/green]")

if __name__ == "__main__":
    # Example usage
    engine = AnalysisEngine()
    
    # Sample articles for testing
    sample_articles = [
        {
            "title": "AI Breakthrough in Medical Diagnosis",
            "content": "Researchers have developed a new AI system that can diagnose diseases with 95% accuracy. This incredible breakthrough will revolutionize healthcare.",
            "category": "technology",
            "url": "https://example.com/ai-medical"
        },
        {
            "title": "Tech Company Reports Record Profits",
            "content": "The company announced quarterly earnings that exceeded all expectations. Revenue increased by 25% compared to last year.",
            "category": "business",
            "url": "https://example.com/tech-profits"
        }
    ]
    
    # Analyze articles
    results = engine.analyze_articles(sample_articles)
    
    # Get summary
    summary = engine.get_analysis_summary(results)
    console.print(f"Analysis summary: {summary}")
    
    # Save results
    engine.save_analysis_results(results) 