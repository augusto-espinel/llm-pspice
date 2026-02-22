"""
App Issue Reader for Ralph
Reads issue logs from the app for analysis
Does NOT write to app logs - read-only
"""

import json
import os


class AppIssueReader:
    """
    Reads issues from the app log (read-only)

    Ralph uses this to:
    - Read logs/issues.json
    - Analyze patterns
    - Generate improvements

    Never writes to app logs.
    """

    def __init__(self, log_file="logs/issues.json"):
        self.log_file = log_file

    def read_all_issues(self):
        """Read all issues from app log"""
        if not os.path.exists(self.log_file):
            print("[AppIssueReader] No issue log found yet.")
            return []

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                issues = json.load(f)
            print(f"[AppIssueReader] Read {len(issues)} issues from {self.log_file}")
            return issues
        except Exception as e:
            print(f"[AppIssueReader] Error reading log: {e}")
            return []

    def get_open_issues(self):
        """
        Get open issues

        Returns:
            - Issues without status field (new logger format) → open
            - Issues with status != 'resolved' → open
            - Issues with status = 'resolved' → resolved (skip)
        """
        all_issues = self.read_all_issues()

        open_issues = []
        for issue in all_issues:
            status = issue.get('status', None)

            # New logger format: no status field → open
            if status is None:
                open_issues.append(issue)
            # Old logger format: check if not resolved
            elif status != 'resolved':
                open_issues.append(issue)

        return open_issues

    def get_issues_by_type(self, issue_type):
        """Get issues filtered by type"""
        all_issues = self.read_all_issues()
        return [i for i in all_issues if i['issue_type'] == issue_type]

    def get_recent_issues(self, days=7):
        """Get issues from last N days"""
        from datetime import datetime, timedelta

        all_issues = self.read_all_issues()
        cutoff = datetime.now() - timedelta(days=days)

        recent = []
        for issue in all_issues:
            try:
                issue_time = datetime.fromisoformat(issue['timestamp'])
                if issue_time > cutoff:
                    recent.append(issue)
            except (KeyError, ValueError):
                continue

        return recent

    def get_summary(self):
        """Get summary statistics"""
        all_issues = self.read_all_issues()

        if not all_issues:
            return {
                'total': 0,
                'by_type': {},
                'by_model': {},
                'by_provider': {}
            }

        summary = {
            'total': len(all_issues),
            'by_type': {},
            'by_model': {},
            'by_provider': {},
            'by_status': {}
        }

        for issue in all_issues:
            # By type
            issue_type = issue.get('issue_type', 'unknown')
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1

            # By model
            model = issue.get('metadata', {}).get('llm_model', 'unknown')
            summary['by_model'][model] = summary['by_model'].get(model, 0) + 1

            # By provider
            provider = issue.get('metadata', {}).get('provider', 'unknown')
            summary['by_provider'][provider] = summary['by_provider'].get(provider, 0) + 1

            # By status
            status = issue.get('status', 'open')  # No status = open
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1

        return summary


# Global instance
_reader = None


def get_reader(log_file="logs/issues.json"):
    """Get the global app issue reader instance"""
    global _reader
    if _reader is None:
        _reader = AppIssueReader(log_file)
    return _reader


# Backward compatibility alias for Ralph
get_issue_logger = get_reader