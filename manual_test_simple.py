#!/usr/bin/env python3
"""
Simple Manual Test - Quick AI Response Check
Run this to quickly test a single ticket classification
"""
from __future__ import annotations

import asyncio
from datetime import datetime

from app.dependencies import get_orchestrator


async def test_single_ticket():
    """Test a single ticket and display the result"""
    
    # Edit this ticket to test different scenarios
    ticket = {
        "id": "quick_test_1",
        "subject": "Website keeps crashing when I upload large files",
        "description": "Every time I try to upload a file larger than 10MB, the website crashes with a timeout error.",
        "expected": "Technical Issue"  # What you expect the category to be
    }
    
    print("=" * 80)
    print("QUICK AI CLASSIFICATION TEST")
    print("=" * 80)
    
    print(f"\n📨 Testing Ticket:")
    print(f"   Subject: {ticket['subject']}")
    print(f"   Description: {ticket['description']}")
    print(f"\n⏳ Classifying...")
    
    orchestrator = get_orchestrator()
    
    result = await orchestrator.classify(
        ticket_id=ticket['id'],
        subject=ticket['subject'],
        description=ticket['description'],
        created_at=datetime.utcnow().isoformat(),
        simulate_ai_failure=False,
    )
    
    print(f"\n🤖 AI Classification Result:")
    print(f"   Category: {result['category']}")
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Decision Path: {' -> '.join(result['metadata']['decision_path'])}")
    
    if 'ai_provider' in result['metadata']:
        print(f"   AI Provider: {result['metadata']['ai_provider']}")
        print(f"   Model: {result['metadata'].get('model', 'N/A')}")
    
    if result['metadata'].get('fallback_used'):
        print(f"   ⚠️  Fallback Used: {result['metadata'].get('fallback_reason', 'Unknown')}")
    
    print(f"\n💭 Expected Category: {ticket['expected']}")
    
    if result['category'] == ticket['expected']:
        print("✅ Result matches expectation!")
    else:
        print(f"⚠️  Result differs from expectation")
    
    print("\n" + "=" * 80)
    
    # Ask for confirmation
    response = input("\nDoes the classification look correct? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("✅ Test passed!")
    else:
        print("❌ Test failed - manual review needed")
        print("\nPossible issues to check:")
        print("  • OpenAI API key configuration")
        print("  • Prompt clarity and instructions")
        print("  • Model selection")
        print("  • Expected category definition")


if __name__ == "__main__":
    asyncio.run(test_single_ticket())
