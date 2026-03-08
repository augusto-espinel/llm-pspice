#!/usr/bin/env python3
"""
Check for recent low-pass filter issues
"""

import json

# Load issues
with open('logs/issues.json', 'r', encoding='utf-8') as f:
    issues = json.load(f)

# Look for filter-related issues
filter_issues = []
for issue in issues:
    prompt = issue.get('prompt', '').lower()
    error = issue.get('error_message', '').lower()
    issue_type = issue.get('issue_type', '')

    if 'filter' in prompt or 'low-pass' in prompt or 'cutoff' in prompt:
        ts = issue.get('timestamp', '')[:19] if issue.get('timestamp') else 'N/A'
        status = issue.get('status', 'unknown')
        filter_issues.append({
            'id': issue.get('id'),
            'prompt': issue.get('prompt', 'N/A')[:60],
            'timestamp': ts,
            'status': status,
            'type': issue_type,
            'error': issue.get('error_message', '')[:100]
        })

if filter_issues:
    print(f"Found {len(filter_issues)} filter-related issues:")
    print("=" * 80)
    for issue in filter_issues:
        print(f"ID {issue['id']}: {issue['timestamp']}")
        print(f"  Type: {issue['type']}")
        print(f"  Status: {issue['status']}")
        print(f"  Prompt: {issue['prompt']}")
        if issue['error']:
            print(f"  Error: {issue['error']}")
        print()
else:
    print("No filter-related issues found in log")