#!/usr/bin/env python3
"""Check open issues"""
import json

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

open_issues = [i for i in data if i.get('status', 'open') == 'open']

print(f'Open issues: {len(open_issues)}')
print()
for idx, i in enumerate(open_issues, 1):
    pid = i.get('id', 'no-id')
    prompt = i.get('prompt', '')[:60] + '...' if len(i.get('prompt', '')) > 60 else i.get('prompt', '')
    print(f"#{pid}: {i['issue_type']} - {prompt}")