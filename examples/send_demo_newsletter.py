#!/usr/bin/env python3
"""
Send Demo Newsletter
Generates and sends a real newsletter email to demonstrate the system
"""

import os
import json
from datetime import datetime
from src.newsletter_orchestrator import NewsletterOrchestrator
from src.email_distributor import EmailDistributor

def send_demo_newsletter():
    print("📧 Sending Demo Newsletter")
    print("=" * 40)
    
    # Check if email is configured
    try:
        with open("config/email_config.json", 'r') as f:
            config = json.load(f)
        
        if config["sender_email"] == "your-email@gmail.com":
            print("❌ Email not configured yet!")
            print("Run: python setup_email.py")
            return False
            
    except Exception as e:
        print(f"❌ Error reading email config: {e}")
        return False
    
    # Get recipient email
    recipient_email = input("Enter your email address to receive the demo newsletter: ").strip()
    
    if not recipient_email:
        print("❌ Please enter a valid email address")
        return False
    
    print(f"\n📧 Will send newsletter to: {recipient_email}")
    print()
    
    # Initialize email distributor
    distributor = EmailDistributor()
    
    # Add recipient as subscriber
    print("1. Adding you as a subscriber...")
    distributor.add_subscriber(recipient_email, "Demo User")
    
    # Generate newsletter
    print("2. Generating newsletter...")
    orchestrator = NewsletterOrchestrator()
    
    try:
        # Generate newsletter with demo theme
        report = orchestrator.generate_newsletter("AI & Technology Demo")
        
        if not report:
            print("❌ Newsletter generation failed")
            return False
        
        newsletter = report.get("newsletter")
        if not newsletter:
            print("❌ No newsletter in report")
            return False
        
        print(f"✅ Newsletter generated: {newsletter.title}")
        
        # Send via email
        print("3. Sending newsletter via email...")
        
        # Generate HTML and text versions
        html_content = orchestrator.creation_engine.format_newsletter(newsletter, "html")
        text_content = orchestrator.creation_engine.format_newsletter(newsletter, "plain_text")
        
        # Send newsletter
        newsletter_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        email_results = distributor.send_newsletter(
            html_content, 
            text_content, 
            "AI & Technology Demo",
            newsletter_id
        )
        
        if email_results.get("success", False):
            print("🎉 Newsletter sent successfully!")
            print(f"📧 Check your inbox: {recipient_email}")
            print(f"📊 Sent to: {email_results['sent_successfully']} subscribers")
            print(f"📊 Failed: {email_results['failed']} subscribers")
            
            # Show newsletter details
            print(f"\n📰 Newsletter Details:")
            print(f"   Title: {newsletter.title}")
            print(f"   Word Count: {newsletter.word_count}")
            print(f"   Reading Time: {newsletter.reading_time} minutes")
            print(f"   Sections: {len(newsletter.sections)}")
            
            return True
        else:
            print(f"❌ Email sending failed: {email_results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 AI Newsletter Generator - Demo Email")
    print("=" * 50)
    print()
    print("This will generate a real newsletter and send it to your email!")
    print()
    
    # Check if email is configured
    try:
        with open("config/email_config.json", 'r') as f:
            config = json.load(f)
        
        if config["sender_email"] != "your-email@gmail.com":
            print(f"✅ Email configured: {config['sender_email']}")
        else:
            print("⚠️  Email not configured yet")
            print("Run: python setup_email.py")
            return
            
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return
    
    # Send demo newsletter
    if send_demo_newsletter():
        print("\n🎉 Demo complete!")
        print("\nWhat you just experienced:")
        print("1. ✅ AI researched trending topics")
        print("2. ✅ Collected and analyzed articles")
        print("3. ✅ Generated professional newsletter")
        print("4. ✅ Sent via email with HTML formatting")
        print("5. ✅ Tracked delivery success")
        print()
        print("Next steps:")
        print("- Add more subscribers: python email_demo.py")
        print("- Schedule weekly emails: python main.py --schedule")
        print("- Customize themes and sources")
    else:
        print("\n❌ Demo failed. Please check your email configuration.")

if __name__ == "__main__":
    main() 