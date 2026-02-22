#!/usr/bin/env python3
"""
Mark Ralph-applied fixes as resolved
"""
import json
from datetime import datetime, timezone

# Load issues
with open('logs/issues.json', 'r', encoding='utf-8') as f:
    issues = json.load(f)

# Mark specific issues as resolved
resolved_ids = [13, 14, 15, 16, 17, 18, 20, 22]
resolved_count = 0

for issue in issues:
    # Skip issues without 'id' field
    if 'id' not in issue:
        continue

    if issue['id'] in resolved_ids:
        issue['status'] = 'resolved'
        if issue['id'] == 22:
            issue['resolution'] = 'Applied fix: fallback'
        else:
            issue['resolution'] = 'Applied fix: enhanced_system_prompt'
        issue['resolved_at'] = datetime.now(timezone.utc).isoformat()
        resolved_count += 1

# Save back
with open('logs/issues.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, indent=2, ensure_ascii=False)

print(f"[OK] Marked {resolved_count} issues as resolved")
print(f"  Total issues: {len(issues)}")
print(f"  Resolved: {sum(1 for i in issues if i['status'] == 'resolved')}")
print(f"  Still open: {sum(1 for i in issues if i['status'] == 'open')}")