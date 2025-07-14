"""
Test suite for AI Newsletter System
Comprehensive tests for all components
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from research_engine import ResearchEngine, Article
from analysis_engine import AnalysisEngine, AnalysisResult
from creation_engine import ContentCreationEngine, Newsletter, NewsletterSection
from newsletter_orchestrator import NewsletterOrchestrator

class TestResearchEngine(unittest.TestCase):
    """Test cases for Research Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = ResearchEngine()
        self.sample_articles = [
            {
                "title": "AI Breakthrough in Medical Diagnosis",
                "url": "https://example.com/ai-medical",
                "content": "Researchers have developed a new AI system that can diagnose diseases with 95% accuracy.",
                "author": "Dr. Smith",
                "published_date": datetime.now() - timedelta(days=1),
                "source": "Tech News",
                "category": "technology"
            },
            {
                "title": "Startup Raises $50M in Funding",
                "url": "https://example.com/startup-funding",
                "content": "A promising startup has secured significant funding for AI development.",
                "author": "Business Reporter",
                "published_date": datetime.now() - timedelta(days=2),
                "source": "Business Daily",
                "category": "business"
            }
        ]
    
    def test_discover_trending_topics(self):
        """Test trending topic discovery"""
        topics = self.engine.discover_trending_topics()
        
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)
        
        # Check that topics are strings
        for topic in topics:
            self.assertIsInstance(topic, str)
    
    def test_collect_articles(self):
        """Test article collection"""
        topics = ["AI", "technology", "startup"]
        articles = self.engine.collect_articles(topics)
        
        self.assertIsInstance(articles, list)
        
        # Articles should be Article objects
        for article in articles:
            self.assertIsInstance(article, Article)
    
    def test_filter_articles(self):
        """Test article filtering"""
        # Create test articles
        articles = []
        for article_data in self.sample_articles:
            article = Article(**article_data)
            articles.append(article)
        
        # Add an old article
        old_article = Article(
            title="Old Article",
            url="https://example.com/old",
            content="Old content",
            author="Old Author",
            published_date=datetime.now() - timedelta(days=30),
            source="Old Source",
            category="general"
        )
        articles.append(old_article)
        
        # Filter articles
        filtered = self.engine._filter_articles(articles)
        
        # Should filter out old articles
        self.assertLessEqual(len(filtered), len(articles))
        
        # Check that no old articles remain
        for article in filtered:
            self.assertGreaterEqual(article.published_date, 
                                   datetime.now() - timedelta(days=7))
    
    def test_save_articles(self):
        """Test article saving"""
        # Create test articles
        articles = []
        for article_data in self.sample_articles:
            article = Article(**article_data)
            articles.append(article)
        
        self.engine.articles = articles
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filename = f.name
        
        try:
            self.engine.save_articles(filename)
            
            # Check that file was created
            self.assertTrue(os.path.exists(filename))
            
            # Check that content is valid JSON
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), len(articles))
            
        finally:
            # Clean up
            if os.path.exists(filename):
                os.unlink(filename)

class TestAnalysisEngine(unittest.TestCase):
    """Test cases for Analysis Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = AnalysisEngine()
        self.sample_articles = [
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
    
    def test_analyze_articles(self):
        """Test article analysis"""
        results = self.engine.analyze_articles(self.sample_articles)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(self.sample_articles))
        
        # Check that results are AnalysisResult objects
        for result in results:
            self.assertIsInstance(result, AnalysisResult)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        positive_text = "This is amazing! Great news for everyone."
        negative_text = "This is terrible. Bad news for everyone."
        neutral_text = "This is a neutral statement about facts."
        
        # Test positive sentiment
        score, label = self.engine._analyze_sentiment(positive_text)
        self.assertIsInstance(score, float)
        self.assertIsInstance(label, str)
        self.assertIn(label, ["positive", "negative", "neutral"])
        
        # Test negative sentiment
        score, label = self.engine._analyze_sentiment(negative_text)
        self.assertIsInstance(score, float)
        self.assertIsInstance(label, str)
        
        # Test neutral sentiment
        score, label = self.engine._analyze_sentiment(neutral_text)
        self.assertIsInstance(score, float)
        self.assertIsInstance(label, str)
    
    def test_relevance_scoring(self):
        """Test relevance scoring"""
        tech_text = "AI and machine learning are transforming technology."
        business_text = "Startup funding and investment in business sector."
        general_text = "General news about various topics."
        
        # Test technology relevance
        score = self.engine._calculate_relevance_score(tech_text, "technology")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test business relevance
        score = self.engine._calculate_relevance_score(business_text, "business")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_bias_detection(self):
        """Test bias detection"""
        biased_text = "This is clearly the most amazing and incredible breakthrough ever!"
        neutral_text = "The study found that the new method shows promising results."
        
        # Test biased text
        bias_score = self.engine._detect_bias(biased_text)
        self.assertIsInstance(bias_score, float)
        self.assertGreaterEqual(bias_score, 0.0)
        self.assertLessEqual(bias_score, 1.0)
        
        # Test neutral text
        bias_score = self.engine._detect_bias(neutral_text)
        self.assertIsInstance(bias_score, float)
        self.assertGreaterEqual(bias_score, 0.0)
        self.assertLessEqual(bias_score, 1.0)
    
    def test_topic_extraction(self):
        """Test topic extraction"""
        text = "Artificial intelligence and machine learning are transforming healthcare and business."
        topics = self.engine._extract_key_topics(text)
        
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)
        
        # Check that topics are strings
        for topic in topics:
            self.assertIsInstance(topic, str)

class TestContentCreationEngine(unittest.TestCase):
    """Test cases for Content Creation Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = ContentCreationEngine()
        self.sample_articles = [
            {
                "title": "AI Breakthrough in Medical Diagnosis",
                "content": "Researchers have developed a new AI system that can diagnose diseases with 95% accuracy.",
                "category": "technology",
                "source": "Tech News",
                "url": "https://example.com/ai-medical"
            },
            {
                "title": "Startup Raises $50M in Funding",
                "content": "A promising startup has secured significant funding for AI development.",
                "category": "business",
                "source": "Business Daily",
                "url": "https://example.com/startup-funding"
            }
        ]
        self.sample_analysis = [
            {
                "relevance_score": 0.9,
                "sentiment_score": 0.8,
                "bias_score": 0.2,
                "insights": ["High relevance to AI industry", "Positive sentiment"]
            },
            {
                "relevance_score": 0.8,
                "sentiment_score": 0.6,
                "bias_score": 0.1,
                "insights": ["Significant business impact", "Neutral sentiment"]
            }
        ]
    
    def test_create_newsletter(self):
        """Test newsletter creation"""
        newsletter = self.engine.create_newsletter(
            self.sample_articles, 
            self.sample_analysis, 
            "Technology & Innovation"
        )
        
        self.assertIsInstance(newsletter, Newsletter)
        self.assertIsInstance(newsletter.title, str)
        self.assertIsInstance(newsletter.subtitle, str)
        self.assertIsInstance(newsletter.sections, list)
        self.assertIsInstance(newsletter.summary, str)
        self.assertIsInstance(newsletter.key_insights, list)
        self.assertIsInstance(newsletter.word_count, int)
        self.assertIsInstance(newsletter.reading_time, int)
    
    def test_categorize_articles(self):
        """Test article categorization"""
        categorized = self.engine._categorize_articles(
            self.sample_articles, 
            self.sample_analysis
        )
        
        self.assertIsInstance(categorized, dict)
        self.assertIn("technology", categorized)
        self.assertIn("business", categorized)
        
        # Check that articles are properly categorized
        self.assertEqual(len(categorized["technology"]["articles"]), 1)
        self.assertEqual(len(categorized["business"]["articles"]), 1)
    
    def test_format_newsletter(self):
        """Test newsletter formatting"""
        # Create a sample newsletter
        sections = [
            NewsletterSection(
                title="🚀 Technology",
                content="Sample content",
                articles=self.sample_articles,
                insights=["Sample insight"],
                category="technology"
            )
        ]
        
        newsletter = Newsletter(
            title="Test Newsletter",
            subtitle="Test Subtitle",
            sections=sections,
            summary="Test summary",
            key_insights=["Test insight"],
            generated_date=datetime.now(),
            word_count=100,
            reading_time=1
        )
        
        # Test markdown formatting
        markdown_content = self.engine.format_newsletter(newsletter, "markdown")
        self.assertIsInstance(markdown_content, str)
        self.assertIn("Test Newsletter", markdown_content)
        
        # Test HTML formatting
        html_content = self.engine.format_newsletter(newsletter, "html")
        self.assertIsInstance(html_content, str)
        self.assertIn("<html>", html_content)
        
        # Test plain text formatting
        text_content = self.engine.format_newsletter(newsletter, "plain_text")
        self.assertIsInstance(text_content, str)
        self.assertIn("Test Newsletter", text_content)

class TestNewsletterOrchestrator(unittest.TestCase):
    """Test cases for Newsletter Orchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = NewsletterOrchestrator()
    
    def test_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNotNone(self.orchestrator.config)
        self.assertIsNotNone(self.orchestrator.research_engine)
        self.assertIsNotNone(self.orchestrator.analysis_engine)
        self.assertIsNotNone(self.orchestrator.creation_engine)
    
    def test_quality_check(self):
        """Test quality checking"""
        # Create mock newsletter and analysis results
        mock_newsletter = Mock()
        mock_newsletter.sections = [Mock()]
        mock_newsletter.sections[0].articles = [Mock(), Mock(), Mock()]  # 3 articles
        mock_newsletter.word_count = 1000
        
        mock_analysis = [
            Mock(relevance_score=0.8, bias_score=0.2),
            Mock(relevance_score=0.7, bias_score=0.3),
            Mock(relevance_score=0.9, bias_score=0.1)
        ]
        
        quality_report = self.orchestrator._perform_quality_check(
            mock_newsletter, 
            mock_analysis
        )
        
        self.assertIsInstance(quality_report, dict)
        self.assertIn("overall_score", quality_report)
        self.assertIn("checks_passed", quality_report)
        self.assertIn("total_checks", quality_report)
        self.assertIn("issues", quality_report)
        self.assertIn("recommendations", quality_report)
    
    def test_directory_creation(self):
        """Test directory creation"""
        # This should create necessary directories
        self.orchestrator._create_directories()
        
        # Check that directories exist
        output_dir = Path(self.orchestrator.config.get("output_directory", "output"))
        archive_dir = Path(self.orchestrator.config.get("archive_directory", "archive"))
        
        self.assertTrue(output_dir.exists())
        self.assertTrue(archive_dir.exists())

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = NewsletterOrchestrator()
    
    @patch('research_engine.ResearchEngine.discover_trending_topics')
    @patch('research_engine.ResearchEngine.collect_articles')
    @patch('analysis_engine.AnalysisEngine.analyze_articles')
    @patch('creation_engine.ContentCreationEngine.create_newsletter')
    def test_full_workflow(self, mock_create, mock_analyze, mock_collect, mock_discover):
        """Test the complete newsletter generation workflow"""
        # Mock the responses
        mock_discover.return_value = ["AI", "technology", "startup"]
        mock_collect.return_value = [Mock(), Mock(), Mock()]
        mock_analyze.return_value = [Mock(), Mock(), Mock()]
        mock_create.return_value = Mock()
        
        # Run the workflow
        report = self.orchestrator.generate_newsletter("Test Theme")
        
        # Verify that all components were called
        mock_discover.assert_called_once()
        mock_collect.assert_called_once()
        mock_analyze.assert_called_once()
        mock_create.assert_called_once()
        
        # Verify that a report was returned
        self.assertIsInstance(report, dict)

class TestDataModels(unittest.TestCase):
    """Test cases for data models"""
    
    def test_article_model(self):
        """Test Article data model"""
        article = Article(
            title="Test Article",
            url="https://example.com/test",
            content="Test content",
            author="Test Author",
            published_date=datetime.now(),
            source="Test Source",
            category="test"
        )
        
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.url, "https://example.com/test")
        self.assertEqual(article.content, "Test content")
        self.assertEqual(article.author, "Test Author")
        self.assertEqual(article.source, "Test Source")
        self.assertEqual(article.category, "test")
    
    def test_analysis_result_model(self):
        """Test AnalysisResult data model"""
        result = AnalysisResult(
            article_id="test_id",
            sentiment_score=0.8,
            sentiment_label="positive",
            relevance_score=0.9,
            bias_score=0.2,
            fact_check_score=0.95,
            key_topics=["AI", "technology"],
            summary="Test summary",
            insights=["Test insight"]
        )
        
        self.assertEqual(result.article_id, "test_id")
        self.assertEqual(result.sentiment_score, 0.8)
        self.assertEqual(result.sentiment_label, "positive")
        self.assertEqual(result.relevance_score, 0.9)
        self.assertEqual(result.bias_score, 0.2)
        self.assertEqual(result.fact_check_score, 0.95)
        self.assertEqual(result.key_topics, ["AI", "technology"])
        self.assertEqual(result.summary, "Test summary")
        self.assertEqual(result.insights, ["Test insight"])

def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestResearchEngine,
        TestAnalysisEngine,
        TestContentCreationEngine,
        TestNewsletterOrchestrator,
        TestIntegration,
        TestDataModels
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 