import json
import os

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Show last 5 issues
print("="*60)
print("LAST 5 ISSUES:")
print("="*60)

for issue in data[-5:]:
    print(f"\nTimestamp: {issue.get('timestamp', 'N/A')}")
    print(f"Model: {issue.get('llm_model', issue.get('metadata', {}).get('llm_model', 'N/A'))}")
    print(f"Prompt: {issue.get('prompt', 'N/A')[:80]}")
    print(f"Type: {issue.get('issue_type', 'N/A')}")
    if issue.get('error_message'):
        print(f"Error: {issue['error_message'][:150]}")
    if 'metadata' in issue and 'context' in issue['metadata']:
        print(f"Context: {issue['metadata']['context']}")
    print("-"*60)

print(f"\nTotal issues: {len(data)}")