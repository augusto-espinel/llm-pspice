#!/usr/bin/env python3
"""Find and save examples of circuit code to file"""
import json

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Write to a text file
with open('circuit_examples.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("EXAMPLES OF LLM-GENERATED CIRCUIT CODE\n")
    f.write("=" * 80 + "\n\n")

    count = 0
    for issue in data:
        llm_resp = issue.get('llm_response', '').strip()

        # Only show if there's actual code content
        if llm_resp and len(llm_resp) > 200 and '```python' in llm_resp:
            count += 1
            f.write("=" * 80 + "\n")
            f.write(f"Example #{count}: Issue ID {issue.get('id', 'unknown')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Prompt:\n{issue.get('prompt', 'N/A')}\n\n")
            f.write(f"Model: {issue.get('llm_model', 'unknown')}\n\n")
            f.write(f"Generated Code:\n{llm_resp}\n\n")
            f.write(f"Status: {issue.get('status', 'unknown')}\n")
            f.write(f"Date: {issue.get('timestamp', 'unknown').split('T')[0]}\n\n")
            f.write("-" * 80 + "\n\n")

            if count >= 3:  # Show 3 examples
                break

    f.write(f"\nTOTAL: Found {count} examples with Python code blocks\n")

print("Examples saved to circuit_examples.txt")