#!/usr/bin/env python3
"""
Manual AI Prompt Testing Script
Run this with human supervision to verify OpenAI responses are accurate.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime

from app.dependencies import get_orchestrator


# Test Cases
TEST_TICKETS = [
    {
        "id": "manual_test_1",
        "subject": "Can't access my account after password reset",
        "description": "I tried to reset my password but the link doesn't work. Now I'm locked out completely.",
        "expected_category": "Account / Access",
        "rationale": "Keywords: access, account, password, locked",
    },
    {
        "id": "manual_test_2", 
        "subject": "Need refund for double charge",
        "description": "I was charged twice last month for my subscription. Please refund the duplicate payment.",
        "expected_category": "Billing",
        "rationale": "Keywords: refund, charge, payment, subscription",
    },
    {
        "id": "manual_test_3",
        "subject": "API returning 500 errors",
        "description": "Our production API started throwing 500 internal server errors after the last deployment. Need urgent help.",
        "expected_category": "Technical Issue",
        "rationale": "Keywords: API, 500, server errors, bug",
    },
    {
        "id": "manual_test_4",
        "subject": "Questions about new features",
        "description": "I saw some announcements about new features. Can you explain how they work?",
        "expected_category": "Other",
        "rationale": "No specific keywords, general question",
    },
]


def print_separator():
    print("\n" + "=" * 80 + "\n")


def print_result(ticket, result):
    """Display test result for human review"""
    print_separator()
    print(f"🎫 TICKET: {ticket['id']}")
    print(f"Subject: {ticket['subject']}")
    print(f"Description: {ticket['description']}")
    print(f"\n📊 EXPECTED:")
    print(f"   Category: {ticket['expected_category']}")
    print(f"   Rationale: {ticket['rationale']}")
    print(f"\n🤖 AI RESPONSE:")
    print(f"   Category: {result['category']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Decision Path: {' -> '.join(result['metadata']['decision_path'])}")
    
    # Check if match
    is_match = result['category'] == ticket['expected_category']
    if is_match:
        print(f"\n✅ MATCH: AI response matches expected category!")
    else:
        print(f"\n❌ MISMATCH: Expected '{ticket['expected_category']}' but got '{result['category']}'")
    
    return is_match


async def run_tests():
    """Run all test cases and display results"""
    print("=" * 80)
    print("MANUAL AI PROMPT TESTING")
    print("=" * 80)
    print("\nThis script tests whether the OpenAI classifier is working correctly.")
    print("Review each result to verify the AI response matches expectations.\n")
    
    orchestrator = get_orchestrator()
    
    results = []
    matches = 0
    
    for i, ticket in enumerate(TEST_TICKETS, 1):
        print(f"\n▶️  Running test {i}/{len(TEST_TICKETS)}...")
        
        result = await orchestrator.classify(
            ticket_id=ticket['id'],
            subject=ticket['subject'],
            description=ticket['description'],
            created_at=datetime.utcnow().isoformat(),
            simulate_ai_failure=False,
        )
        
        is_match = print_result(ticket, result)
        results.append({
            'ticket': ticket,
            'result': result,
            'match': is_match,
        })
        
        if is_match:
            matches += 1
    
    # Summary
    print_separator()
    print("📋 SUMMARY")
    print(f"Total Tests: {len(TEST_TICKETS)}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {len(TEST_TICKETS) - matches}")
    print(f"Accuracy: {matches / len(TEST_TICKETS) * 100:.1f}%")
    print_separator()
    
    # Ask for human confirmation
    print("\n🧑 HUMAN REVIEW:")
    approval = input("Do all results look correct? (yes/no): ").strip().lower()
    
    if approval in ['yes', 'y']:
        print("✅ Tests PASSED - AI prompt is working as expected!")
        return 0
    else:
        print("❌ Tests FAILED - Review needed for AI prompt configuration")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run_tests()))
