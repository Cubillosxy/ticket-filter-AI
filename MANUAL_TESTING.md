# Manual AI Testing Guide

This directory contains manual testing scripts to verify that the OpenAI classifier prompt is working correctly. These tests require human supervision to validate the AI responses.

## Test Scripts

### 1. Comprehensive Test Suite (`manual_test_ai.py`)

Tests 4 different ticket scenarios and compares AI responses to expected categories.

**Run:**
```bash
source .venv/bin/activate
python3 manual_test_ai.py
```

**Test Cases:**
- Account access issue (expected: Account / Access)
- Billing refund request (expected: Billing)
- API technical error (expected: Technical Issue)
- General question (expected: Other)

**Output:** Shows each ticket, expected vs actual category, and asks for human confirmation at the end.

### 2. Quick Single Test (`manual_test_simple.py`)

Quick test for a single ticket - useful for rapid iteration on the prompt.

**Run:**
```bash
source .venv/bin/activate
python3 manual_test_simple.py
```

**How to use:**
1. Edit the `ticket` dictionary in the script to test different scenarios
2. Run the script
3. Review the AI classification result
4. Confirm if it looks correct

## What to Check

When reviewing AI responses, verify:

✅ **Category Accuracy** - Does the category make sense for the ticket content?  
✅ **Confidence Level** - Is the confidence score appropriate (higher for clear cases)?  
✅ **Decision Path** - Did it use the right classification method (rules → AI → fallback)?  
✅ **Consistency** - Running the same ticket multiple times should give similar results

## Categories

The system classifies tickets into these categories:
- **Billing** - Payment, invoices, charges, refunds, subscriptions
- **Technical Issue** - Bugs, crashes, API errors, timeouts
- **Account / Access** - Login, password, 2FA, locked accounts
- **Other** - Everything else

## Debugging

If results are unexpected:

1. **Check AI Provider Configuration**
   - Verify OpenAI API key in `.env` or environment
   - Check `AI_PROVIDER` setting (should be "openai" not "stub")

2. **Review Decision Path**
   - If using "fallback" → AI may have failed or is disabled
   - If using "rules" → keyword matching took precedence

3. **Test with Stub Provider**
   - Set `AI_PROVIDER=stub` to test without OpenAI
   - Useful for verifying the flow works

## Example Output

```
🎫 TICKET: manual_test_1
Subject: Can't access my account after password reset
Description: I tried to reset my password but the link doesn't work...

📊 EXPECTED:
   Category: Account / Access
   Rationale: Keywords: access, account, password, locked

🤖 AI RESPONSE:
   Category: Account / Access
   Confidence: 0.92
   Decision Path: rules -> ai

✅ MATCH: AI response matches expected category!
```

## Notes

- These are NOT automated pytest tests - they require human review
- Use these to validate prompt changes before deploying
- Results may vary slightly between runs (AI is non-deterministic)
- Always activate the virtual environment before running
