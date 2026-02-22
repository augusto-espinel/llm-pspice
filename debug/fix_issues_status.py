import json

# Load issues
with open('logs/issues.json', 'r', encoding='utf-8') as f:
    issues = json.load(f)

# Find issues without status
issues_without_status = [i for i in issues if 'status' not in i]

print(f"Total issues: {len(issues)}")
print(f"Issues without status: {len(issues_without_status)}")

if issues_without_status:
    # Check what fields these issues have
    print(f"Fields in issues without status:")
    for i, issue in enumerate(issues_without_status[:3]):
        print(f"  Issue {i}: {list(issue.keys())}")

    # Add missing fields
    for issue in issues:
        if 'status' not in issue:
            issue['status'] = 'open'
        if 'id' not in issue:
            # Find the next available ID
            max_id = max([i.get('id', 0) for i in issues]) if issues else 0
            issue['id'] = max_id + 1

    # Save back
    with open('logs/issues.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)

    print(f"\nFixed {len(issues_without_status)} issues")
else:
    print("All issues have status field")