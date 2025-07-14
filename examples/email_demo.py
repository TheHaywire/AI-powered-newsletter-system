#!/usr/bin/env python3
"""
Email Distribution Demo
Shows how to set up and use the email distribution system
"""

import os
from src.email_distributor import EmailDistributor
from src.creation_engine import ContentCreationEngine
from datetime import datetime

def main():
    print("📧 AI Newsletter Email Distribution Demo")
    print("=" * 50)
    
    # Initialize email distributor
    distributor = EmailDistributor()
    
    # Add test subscribers
    print("\n1. Adding test subscribers...")
    distributor.add_subscriber("your-email@gmail.com", "Your Name")
    distributor.add_subscriber("test@example.com", "Test User")
    
    # Show subscriber stats
    stats = distributor.get_subscriber_stats()
    print(f"✓ Total subscribers: {stats['total_subscribers']}")
    print(f"✓ Active subscribers: {stats['active_subscribers']}")
    
    # Create a sample newsletter
    print("\n2. Creating sample newsletter...")
    creation_engine = ContentCreationEngine()
    
    # Sample newsletter data
    from src.creation_engine import Newsletter, NewsletterSection
    
    sample_section = NewsletterSection(
        title="🚀 Technology & Innovation",
        content="""
### AI Breakthrough in Medical Diagnosis

Researchers have developed a new AI system that can diagnose diseases with 95% accuracy. This incredible breakthrough will revolutionize healthcare.

**Source:** Tech News | [Read More](https://example.com/ai-medical)

---

### Startup Raises $50M in Series B Funding

A promising startup in the AI space has secured significant funding to expand their operations and develop new products.

**Source:** Business Daily | [Read More](https://example.com/startup-funding)
        """,
        articles=[],
        insights=["High relevance to AI industry", "Positive sentiment"],
        category="technology"
    )
    
    newsletter = Newsletter(
        title="The Technology & Innovation Weekly: AI & Beyond",
        subtitle="Your curated digest of the top 2 stories in technology & innovation",
        sections=[sample_section],
        summary="This week's newsletter covers 2 stories across 1 categories. Key highlights include emerging trends in technology and business developments.",
        key_insights=["AI is transforming healthcare", "Startup funding remains strong"],
        generated_date=datetime.now(),
        word_count=150,
        reading_time=1
    )
    
    # Generate HTML and text versions
    html_content = creation_engine.format_newsletter(newsletter, "html")
    text_content = creation_engine.format_newsletter(newsletter, "plain_text")
    
    print("✓ Newsletter created successfully")
    
    # Send newsletter (if email is configured)
    print("\n3. Sending newsletter...")
    print("⚠️  Note: Email sending requires proper Gmail configuration")
    print("   - Update config/email_config.json with your credentials")
    print("   - Enable 2FA and generate App Password in Gmail")
    
    try:
        results = distributor.send_newsletter(
            html_content, 
            text_content, 
            "Technology & Innovation",
            f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if results.get("success", False):
            print("✓ Newsletter sent successfully!")
            print(f"  - Sent to: {results['sent_successfully']} subscribers")
            print(f"  - Failed: {results['failed']} subscribers")
        else:
            print(f"✗ Email sending failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Email sending error: {e}")
    
    # Export subscribers
    print("\n4. Exporting subscribers...")
    distributor.export_subscribers("subscribers_export.csv")
    
    print("\n📧 Email Distribution Demo Complete!")
    print("\nNext steps:")
    print("1. Update config/email_config.json with your Gmail credentials")
    print("2. Enable 2FA in your Gmail account")
    print("3. Generate an App Password for this application")
    print("4. Run the main system: python main.py --generate")

if __name__ == "__main__":
    main() 