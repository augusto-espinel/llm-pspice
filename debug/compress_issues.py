#!/usr/bin/env python3
"""
Compress issues.json by grouping similar issues
"""

import json
from collections import defaultdict
from datetime import datetime, timezone

def compress_issues(input_file='logs/issues.json', output_file='logs/issues.json'):
    """
    Compress similar issues to reduce file size
    """
    # Load existing issues (with UTF-8 encoding)
    with open(input_file, 'r', encoding='utf-8') as f:
        issues = json.load(f)

    # Separate resolved and open issues
    resolved_issues = [i for i in issues if i.get('status') == 'resolved']
    open_issues = [i for i in issues if i.get('status') == 'open']

    # Group open issues by type
    grouped = defaultdict(list)
    for issue in open_issues:
        itype = issue.get('issue_type', 'unknown')
        grouped[itype].append(issue)

    # Keep all resolved issues (they represent successful fixes)
    compressed = resolved_issues.copy()

    new_id = max([i['id'] for i in resolved_issues]) + 1

    # For each type, create a representative summary
    for itype, issues_list in grouped.items():
        if itype == 'api_error':
            # Compress ALL API errors into one representative entry
            # Count occurrences by model
            model_counts = defaultdict(int)
            prompts = set()

            for issue in issues_list:
                model = issue.get('llm_model', 'unknown')
                model_counts[model] += 1
                prompts.add(issue.get('prompt', 'unknown'))

            # Create representative entry
            compressed.append({
                "id": new_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt": f"[{len(issues_list)} API errors compressed] - Models {list(model_counts.keys())}",
                "issue_type": "api_error",
                "error_message": f"Multiple API errors: models not available on Ollama Cloud",
                "llm_response": "",
                "llm_model": "multiple",
                "provider": "ollama",
                "context": json.dumps({
                    "total_occurrences": len(issues_list),
                    "models_involved": dict(model_counts),
                    "unique_prompts": len(prompts),
                    "example_prompt": list(prompts)[0] if prompts else "none"
                }),
                "status": "open",
                "attempts": 0,
                "fix_attempt": None,
                "compressed": {
                    "original_count": len(issues_list),
                    "compression_ratio": f"{len(issues_list)}:1"
                }
            })
            new_id += 1

        elif itype in ['empty_output', 'no_code_block', 'simulation_error']:
            # Keep a few representative samples (up to 3 per type)
            # Group by prompt to avoid duplicates
            unique_prompts = {}
            for issue in issues_list:
                prompt = issue.get('prompt', '')
                if prompt not in unique_prompts:
                    unique_prompts[prompt] = issue

            # Keep up to 3 unique prompts per type
            kept = list(unique_prompts.values())[:3]

            # If we had more, add a summary of the compressed ones
            if len(issues_list) > len(kept):
                compressed_count = len(issues_list) - len(kept)
                compressed.append({
                    "id": new_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "prompt": f"[{compressed_count} additional {itype} issues compressed]",
                    "issue_type": itype,
                    "error_message": "Multiple similar issues - see representative samples",
                    "llm_response": "",
                    "llm_model": "various",
                    "provider": "ollama",
                    "context": f"Compressed {compressed_count} similar issues",
                    "status": "open",
                    "attempts": 0,
                    "fix_attempt": None,
                    "compressed": {
                        "original_count": compressed_count,
                        "compression_ratio": f"{compressed_count}:1"
                    }
                })
                new_id += 1

            # Add the representative issues
            for issue in kept:
                issue['id'] = new_id
                compressed.append(issue)
                new_id += 1

        else:
            # Keep as-is for other types
            compressed.extend(issues_list)
            new_id += len(issues_list)

    # Sort by ID
    compressed.sort(key=lambda x: x['id'])

    # Write compressed data (with UTF-8 encoding)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(compressed, f, indent=2, ensure_ascii=False)

    # Print summary
    original_count = len(issues)
    compressed_count = len(compressed)
    reduction = (1 - compressed_count / original_count) * 100

    print("=" * 60)
    print("ISSUES COMPRESSION SUMMARY")
    print("=" * 60)
    print(f"Original issues:     {original_count}")
    print(f"Compressed issues:   {compressed_count}")
    print(f"Reduction:           {reduction:.1f}%")
    print()

    # Show breakdown
    print("Breakdown by status:")
    print(f"  Resolved:  {len([i for i in compressed if i['status'] == 'resolved'])}")
    print(f"  Open:      {len([i for i in compressed if i['status'] == 'open'])}")
    print()

    print("Breakdown by type (open issues):")
    for itype in ['api_error', 'empty_output', 'no_code_block', 'simulation_error']:
        count = len([i for i in compressed if i.get('issue_type') == itype and i.get('status') == 'open'])
        if count > 0:
            print(f"  {itype}: {count}")

    print()
    print(f"[OK] Compressed issues saved to: {output_file}")
    print()

if __name__ == "__main__":
    compress_issues()