#!/usr/bin/env python3
"""Find examples of successful circuit code generation"""
import json

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 80)
print("EXAMPLES FROM ISSUES WITH LLM RESPONSES")
print("=" * 80)

count = 0
for issue in data:
    llm_resp = issue.get('llm_response', '').strip()

    # Only show if there's actual code content
    if llm_resp and len(llm_resp) > 200 and '```python' in llm_resp:
        count += 1
        print(f"\n{'=' * 80}")
        print(f"Example #{count}: Issue ID {issue.get('id', 'unknown')}")
        print(f"{'=' * 80}")
        print(f"\n[PROMPT]")
        print(f"  {issue.get('prompt', 'N/A')}")
        print(f"\n[MODEL]")
        print(f"  {issue.get('llm_model', 'unknown')}")
        print(f"\n[RESPONSE - First 1000 chars]")
        print(f"  {llm_resp[:1000]}...")
        print(f"\n[STATUS]")
        print(f"  {issue.get('status', 'unknown')}")
        print(f"[DATE]")
        print(f"  {issue.get('timestamp', 'unknown').split('T')[0]}")

        if count >= 3:  # Show 3 examples
            break

print(f"\n\n{'=' * 80}")
print(f"TOTAL: Found {count} examples with Python code blocks")
print('=' * 80)