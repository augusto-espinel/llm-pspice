import json

with open('logs/issues.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

last = data[-1]
print("="*60)
print("MOST RECENT ISSUE:")
print("="*60)
print(f"Prompt: {last.get('prompt', 'N/A')}")
print(f"Error: {last.get('error_message', 'N/A')}")
print(f"Model: {last.get('llm_model', 'N/A')}")
print(f"Issue Type: {last.get('issue_type', 'N/A')}")
print(f"Timestamp: {last.get('timestamp', 'N/A')}")
print(f"Status: {last.get('status', 'N/A')}")
print("="*60)

# Check for recent issues (last hour)
from datetime import datetime
if last.get('timestamp'):
    ts = last['timestamp']
    print(f"Time formatted: {ts}")

print(f"\nTotal issues: {len(data)}")
print(f"Last few models: {[i.get('llm_model', 'N/A') for i in data[-5:]]}")