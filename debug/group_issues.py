#!/usr/bin/env python3
"""Compress remaining no-id open issues"""
import json
from datetime import datetime, timezone

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group no-id open issues by type
open_no_id = []
with_id_open = []

for issue in data:
    if issue.get('status', 'open') != 'open':
        continue
    if 'id' in issue:
        with_id_open.append(issue)
    else:
        open_no_id.append(issue)

print(f"With ID open: {len(with_id_open)}")
print(f"No-ID open: {len(open_no_id)}")

# Group no-id issues by type
by_type = {}
for issue in open_no_id:
    itype = issue.get('issue_type', 'unknown')
    if itype not in by_type:
        by_type[itype] = []
    by_type[itype].append(issue)

print(f"\nNo-ID issues by type:")
for itype, issues in by_type.items():
    print(f"  {itype}: {len(issues)}")
    # Show prompts
    for idx, iss in enumerate(issues[:3], 1):
        prompt = iss.get('prompt', '')[:50]
        print(f"    {idx}. {prompt}...")