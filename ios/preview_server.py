"""
Standalone MVP preview server for the AI Newsletter iOS app.
Serves a mobile web app that mirrors the SwiftUI iOS interface,
backed by a mock API with realistic demo data.
"""

from flask import Flask, jsonify, request, send_from_directory
import json
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__, static_folder='preview')

# ─── Mock Data ──────────────────────────────────────────────────────────────

NEWSLETTERS = [
    {
        "id": "nl_001",
        "title": "AI & Machine Learning Weekly Digest",
        "subtitle": "Top stories in artificial intelligence this week",
        "theme": "Technology & AI",
        "status": "published",
        "created_at": "2026-02-25 09:00:00",
        "summary": "This week saw major breakthroughs in multimodal AI models, with several companies releasing new architectures that combine vision, language, and reasoning capabilities. The open-source community continues to close the gap with proprietary models.",
        "key_insights": [
            "Multimodal AI models are becoming the new standard for enterprise applications",
            "Open-source LLMs now match proprietary models on several benchmarks",
            "AI regulation frameworks are being adopted across 15 new countries",
            "Edge AI deployment grew 340% year-over-year in manufacturing"
        ],
        "sections": [
            {
                "id": "sec_001",
                "title": "Artificial Intelligence",
                "articles": [
                    {
                        "id": "art_001",
                        "title": "New Multimodal Architecture Achieves State-of-the-Art Results",
                        "url": "#",
                        "content": "Researchers have unveiled a new multimodal architecture that combines vision transformers with large language models, achieving state-of-the-art results across 12 benchmarks. The model uses a novel cross-attention mechanism that allows seamless reasoning across text and images.",
                        "author": "Dr. Sarah Chen",
                        "source": "TechCrunch",
                        "category": "AI Research",
                        "sentiment_score": 0.85,
                        "relevance_score": 0.95,
                        "bias_score": 0.1
                    },
                    {
                        "id": "art_002",
                        "title": "Open Source LLM Matches GPT-4 on Coding Tasks",
                        "url": "#",
                        "content": "A community-developed open-source language model has achieved parity with GPT-4 on competitive programming benchmarks. The model, trained on a curated dataset of high-quality code, demonstrates strong reasoning capabilities.",
                        "author": "Alex Rivera",
                        "source": "The Verge",
                        "category": "Open Source",
                        "sentiment_score": 0.72,
                        "relevance_score": 0.88,
                        "bias_score": 0.15
                    }
                ]
            },
            {
                "id": "sec_002",
                "title": "Business & Startups",
                "articles": [
                    {
                        "id": "art_003",
                        "title": "AI Startup Raises $500M Series C for Enterprise Automation",
                        "url": "#",
                        "content": "An AI-powered enterprise automation startup has secured $500 million in Series C funding, valuing the company at $8 billion. The platform uses AI agents to automate complex business workflows across industries.",
                        "author": "Maria Lopez",
                        "source": "Bloomberg",
                        "category": "Funding",
                        "sentiment_score": 0.65,
                        "relevance_score": 0.82,
                        "bias_score": 0.2
                    },
                    {
                        "id": "art_004",
                        "title": "Edge AI Market Expected to Reach $50B by 2028",
                        "url": "#",
                        "content": "A new market research report projects the edge AI market will grow from $15 billion to $50 billion by 2028, driven by manufacturing, healthcare, and autonomous vehicle applications.",
                        "author": "James Park",
                        "source": "Reuters",
                        "category": "Market Analysis",
                        "sentiment_score": 0.45,
                        "relevance_score": 0.75,
                        "bias_score": 0.12
                    }
                ]
            },
            {
                "id": "sec_003",
                "title": "Policy & Regulation",
                "articles": [
                    {
                        "id": "art_005",
                        "title": "EU AI Act Implementation Begins Across Member States",
                        "url": "#",
                        "content": "The European Union's AI Act has entered its implementation phase, with member states beginning to establish national AI offices. Companies have 12 months to comply with high-risk AI system requirements.",
                        "author": "Emma Wilson",
                        "source": "BBC News",
                        "category": "Regulation",
                        "sentiment_score": 0.1,
                        "relevance_score": 0.9,
                        "bias_score": 0.08
                    }
                ]
            }
        ],
        "metrics": {
            "word_count": 2450,
            "reading_time_minutes": 8,
            "article_count": 5,
            "source_count": 5,
            "average_sentiment": 0.55,
            "quality_score": 0.87
        }
    },
    {
        "id": "nl_002",
        "title": "Blockchain & Web3 Innovation Report",
        "subtitle": "Decentralized technology trends and analysis",
        "theme": "Blockchain & Web3",
        "status": "published",
        "created_at": "2026-02-18 09:00:00",
        "summary": "Layer 2 scaling solutions gained significant traction this week with several major DeFi protocols migrating. Institutional adoption continues to accelerate with new regulatory clarity in key markets.",
        "key_insights": [
            "Layer 2 transaction volume surpassed Layer 1 for the first time",
            "DeFi TVL reached new all-time high of $180B",
            "Three major banks announced blockchain settlement pilots"
        ],
        "sections": [
            {
                "id": "sec_004",
                "title": "DeFi & Protocols",
                "articles": [
                    {
                        "id": "art_006",
                        "title": "Layer 2 Networks Process More Transactions Than Ethereum Mainnet",
                        "url": "#",
                        "content": "For the first time, Layer 2 rollup networks processed more daily transactions than the Ethereum mainnet, marking a significant milestone in blockchain scalability efforts.",
                        "author": "David Kim",
                        "source": "CoinDesk",
                        "category": "DeFi",
                        "sentiment_score": 0.78,
                        "relevance_score": 0.92,
                        "bias_score": 0.18
                    }
                ]
            }
        ],
        "metrics": {
            "word_count": 1850,
            "reading_time_minutes": 6,
            "article_count": 4,
            "source_count": 4,
            "average_sentiment": 0.62,
            "quality_score": 0.79
        }
    },
    {
        "id": "nl_003",
        "title": "Climate Tech & Sustainability Weekly",
        "subtitle": "Green innovation and environmental technology",
        "theme": "Climate & Sustainability",
        "status": "draft",
        "created_at": "2026-02-24 14:30:00",
        "summary": "Breakthrough in solid-state battery technology could accelerate EV adoption. Carbon capture costs fell below $100 per ton for the first time at scale.",
        "key_insights": [
            "Solid-state batteries achieved 500-mile range in testing",
            "Carbon capture costs dropped 40% year-over-year",
            "Renewable energy now cheapest power source in 90% of markets"
        ],
        "sections": [],
        "metrics": {
            "word_count": 1200,
            "reading_time_minutes": 4,
            "article_count": 3,
            "source_count": 3,
            "average_sentiment": 0.7,
            "quality_score": 0.72
        }
    }
]

SUBSCRIBERS = [
    {"id": "sub_001", "email": "sarah@techcorp.com", "name": "Sarah Chen", "subscribed_at": "2026-01-15", "is_active": True, "preferences": {"categories": ["AI", "Technology"], "frequency": "weekly", "format": "html"}},
    {"id": "sub_002", "email": "alex@startup.io", "name": "Alex Rivera", "subscribed_at": "2026-01-20", "is_active": True, "preferences": {"categories": ["Startups", "Business"], "frequency": "weekly", "format": "html"}},
    {"id": "sub_003", "email": "james@enterprise.com", "name": "James Park", "subscribed_at": "2026-02-01", "is_active": True, "preferences": {"categories": ["AI", "Blockchain"], "frequency": "daily", "format": "markdown"}},
    {"id": "sub_004", "email": "maria@research.edu", "name": "Maria Lopez", "subscribed_at": "2026-02-10", "is_active": True, "preferences": {"categories": ["Science", "Climate"], "frequency": "weekly", "format": "html"}},
    {"id": "sub_005", "email": "emma@media.co", "name": "Emma Wilson", "subscribed_at": "2026-02-14", "is_active": False, "preferences": {"categories": ["Technology"], "frequency": "weekly", "format": "plain_text"}},
    {"id": "sub_006", "email": "david@fintech.com", "name": "David Kim", "subscribed_at": "2026-02-18", "is_active": True, "preferences": {"categories": ["Blockchain", "Business"], "frequency": "weekly", "format": "html"}},
    {"id": "sub_007", "email": "lisa@dev.io", "name": "Lisa Zhang", "subscribed_at": "2026-02-20", "is_active": True, "preferences": {"categories": ["AI", "Open Source"], "frequency": "daily", "format": "markdown"}},
]

# ─── API Routes ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('preview', 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({"success": True, "token": "demo-token-abc123", "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/dashboard')
def dashboard():
    return jsonify({
        "total_newsletters": len(NEWSLETTERS),
        "total_subscribers": len(SUBSCRIBERS),
        "total_articles": sum(
            sum(len(s["articles"]) for s in nl["sections"])
            for nl in NEWSLETTERS
        ),
        "delivery_rate": 0.96,
        "recent_newsletters": NEWSLETTERS[:3]
    })

@app.route('/api/newsletters')
def newsletters():
    return jsonify(NEWSLETTERS)

@app.route('/api/newsletters/<nid>')
def newsletter_detail(nid):
    for nl in NEWSLETTERS:
        if nl["id"] == nid:
            return jsonify(nl)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    theme = data.get('theme', 'Technology & AI')
    return jsonify({
        "success": True,
        "message": f"Newsletter '{theme}' generated successfully with 5 articles from 4 sources. Quality score: 87%.",
        "newsletter_id": "nl_001"
    })

@app.route('/api/subscribers')
def subscribers():
    return jsonify({"subscribers": SUBSCRIBERS, "total": len(SUBSCRIBERS)})

@app.route('/api/subscribers', methods=['POST'])
def add_subscriber():
    data = request.get_json()
    return jsonify({"success": True, "message": "Subscriber added"})

@app.route('/api/analytics')
def analytics():
    return jsonify({
        "delivery_stats": {
            "total_sent": 156,
            "delivered": 150,
            "failed": 6,
            "delivery_rate": 0.96
        },
        "engagement_stats": {
            "open_rate": 0.68,
            "click_rate": 0.34,
            "unsubscribe_rate": 0.02
        },
        "content_stats": {
            "average_articles": 5.2,
            "average_word_count": 2150,
            "average_reading_time": 7.0,
            "top_categories": [
                {"category": "AI & ML", "count": 45},
                {"category": "Business", "count": 32},
                {"category": "Blockchain", "count": 18},
                {"category": "Climate", "count": 12},
                {"category": "Science", "count": 8}
            ],
            "average_quality_score": 0.82
        },
        "time_series_data": [
            {"date": "2026-01", "newsletters": 4, "subscribers": 3, "delivery_rate": 0.92},
            {"date": "2026-02", "newsletters": 4, "subscribers": 7, "delivery_rate": 0.96}
        ]
    })

if __name__ == '__main__':
    os.makedirs('preview', exist_ok=True)
    print("\n  AI Newsletter iOS Preview")
    print("  ========================")
    print("  Server:  http://localhost:5001")
    print("  Login:   admin / admin123\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
