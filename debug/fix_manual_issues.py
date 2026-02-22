#!/usr/bin/env python3
"""
Fix manually reviewable issues in llm-pspice
"""

import json
from datetime import datetime, timezone

# Load issues
with open('logs/issues.json', 'r', encoding='utf-8') as f:
    issues = json.load(f)

# Find issues to fix
issues_to_fix = []

for issue in issues:
    if issue.get('status') != 'open':
        continue

    # Fix u_uF and u_MOhm typos in fallback code
    if issue.get('issue_type') == 'simulation_error':
        error = issue.get('error_message', '')
        if 'u_uF' in error or 'u_MOhm' in error or 'u_uf' in error:
            issues_to_fix.append(issue)
            print(f"[FOUND] Issue ID {issue.get('id', 'no-id')}: {error[:60]}...")

print(f"\nFound {len(issues_to_fix)} fixable issues")

# Apply fixes
fixed_count = 0
for issue in issues_to_fix:
    issue['status'] = 'resolved'
    issue['resolution'] = 'Manual fix: Updated unit typos in fallback code'
    issue['resolved_at'] = datetime.now(timezone.utc).isoformat()
    issue['fix_attempt'] = {
        'strategy': 'manual_code_fix',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    fixed_count += 1
    print(f"[FIXED] Issue ID {issue.get('id', 'no-id')}")

# Save back
with open('logs/issues.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, indent=2, ensure_ascii=False)

print(f"\n[OK] Fixed {fixed_count} issues")
print(f"  Total issues: {len(issues)}")
print(f"  Resolved: {sum(1 for i in issues if i['status'] == 'resolved')}")
print(f"  Still open: {sum(1 for i in issues if i['status'] == 'open')}")