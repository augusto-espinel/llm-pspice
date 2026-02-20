"""
Issue Logger for LLM-PSPICE
Tracks failed prompts, empty outputs, and edge cases for systematic debugging
"""

import json
import os
from datetime import datetime
from enum import Enum


class IssueType(Enum):
    """Types of issues that can be logged"""
    EMPTY_OUTPUT = "empty_output"
    SIMULATION_ERROR = "simulation_error"
    INVALID_CIRCUIT = "invalid_circuit"
    API_ERROR = "api_error"
    TIMEOUT = "timeout"
    NO_CODE_BLOCK = "no_code_block"
    SYNTAX_ERROR = "syntax_error"
    OTHER = "other"


class IssueLogger:
    """
    Logs and manages failed prompts for systematic debugging and fixing

    Issues are stored in: logs/issues.json (appends to JSON array)
    """

    def __init__(self, log_file="logs/issues.json"):
        self.log_file = log_file
        self.issues = []
        self._ensure_log_directory()
        self._load_existing_issues()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def _load_existing_issues(self):
        """Load existing issues from log file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.issues = json.load(f)
            except Exception as e:
                print(f"[IssueLogger] Warning: Could not load existing issues: {e}")
                self.issues = []

    def _save_issues(self):
        """Save issues to log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.issues, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[IssueLogger] Error saving issues: {e}")

    def log_issue(self, prompt, issue_type, error_message="", llm_response="",
                  llm_model="", provider="", context=""):
        """
        Log an issue with metadata

        Args:
            prompt (str): The original user prompt
            issue_type (IssueType or str): Type of issue
            error_message (str): Error message if any
            llm_response (str): LLM's response (if any)
            llm_model (str): Model used
            provider (str): Provider used (openai, deepseek, ollama, etc.)
            context (str): Additional context
        """
        # Convert string to IssueType if needed
        if isinstance(issue_type, str):
            try:
                issue_type = IssueType(issue_type)
            except ValueError:
                issue_type = IssueType.OTHER

        issue = {
            'id': len(self.issues) + 1,
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'issue_type': issue_type.value,
            'error_message': error_message,
            'llm_response': llm_response,
            'llm_model': llm_model,
            'provider': provider,
            'context': context,
            'status': 'open',  # open, in_progress, resolved
            'attempts': 0,
            'fix_attempt': None
        }

        self.issues.append(issue)
        self._save_issues()

        print(f"[IssueLogger] Logged issue #{issue['id']}: {issue_type.value} - {prompt[:50]}...")

        return issue['id']

    def mark_in_progress(self, issue_id, attempted_fix=""):
        """Mark an issue as being worked on"""
        for issue in self.issues:
            if issue['id'] == issue_id:
                issue['status'] = 'in_progress'
                issue['attempts'] += 1
                issue['fix_attempt'] = attempted_fix
                issue['last_attempt'] = datetime.now().isoformat()
                self._save_issues()
                return True
        return False

    def mark_resolved(self, issue_id, resolution_note=""):
        """Mark an issue as resolved"""
        for issue in self.issues:
            if issue['id'] == issue_id:
                issue['status'] = 'resolved'
                issue['resolution'] = resolution_note
                issue['resolved_at'] = datetime.now().isoformat()
                self._save_issues()
                return True
        return False

    def get_open_issues(self):
        """Get all open issues"""
        return [issue for issue in self.issues if issue.get('status', 'unknown') == 'open']

    def get_issues_by_type(self, issue_type):
        """Get issues filtered by type"""
        if isinstance(issue_type, str):
            issue_type = IssueType(issue_type)

        return [issue for issue in self.issues if issue['issue_type'] == issue_type.value]

    def get_recent_issues(self, days=7):
        """Get issues from the last N days"""
        from datetime import timedelta, timezone
        # Create aware datetime for cutoff
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = []
        for issue in self.issues:
            try:
                # Parse timestamp - ensure it's timezone-aware
                ts = issue['timestamp']
                # Handle both 'Z' and offset formats
                if ts.endswith('Z'):
                    ts = ts.replace('Z', '+00:00')
                issue_dt = datetime.fromisoformat(ts)
                # If parsed datetime is naive, treat it as UTC
                if issue_dt.tzinfo is None:
                    from datetime import timezone as tz
                    issue_dt = issue_dt.replace(tzinfo=tz.utc)
                # Compare only if both are aware
                if issue_dt.tzinfo is not None:
                    if issue_dt > cutoff:
                        result.append(issue)
            except Exception as e:
                # Skip issues with invalid timestamps
                print(f"[WARNING] Skipping issue with invalid timestamp: {e}")
                continue
        return result

    def get_issue_summary(self):
        """Get a summary of all issues"""
        if not self.issues:
            return {
                'total': 0,
                'by_type': {},
                'by_status': {},
                'by_model': {}
            }

        summary = {
            'total': len(self.issues),
            'by_type': {},
            'by_status': {},
            'by_model': {}
        }

        for issue in self.issues:
            # By type
            issue_type = issue['issue_type']
            summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1

            # By status (with fallback for missing field)
            status = issue.get('status', 'unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1

            # By model
            model = issue.get('llm_model', 'unknown')
            summary['by_model'][model] = summary['by_model'].get(model, 0) + 1

        return summary

    def export_issues_for_ralph(self, format="json"):
        """
        Export issues in a format suitable for Ralph to process

        Args:
            format (str): "json" or "prompt" - format for export

        Returns:
            str: Exported issues
        """
        open_issues = self.get_open_issues()

        if format == "prompt":
            # Create a prompt for Ralph
            lines = [
                "# Task: Fix these circuit generation issues",
                "",
                f"Total issues to fix: {len(open_issues)}",
                "",
                "For each issue:",
                "1. Analyze why the LLM failed to generate working circuit code",
                "2. Determine if the prompt is missing context/information",
                "3. Generate either:",
                "   - An improved system prompt that ensures complete circuits",
                "   - A template-based solution for this type of circuit",
                "   - A fix that adds missing context automatically",
                "",
                "---"
            ]

            for i, issue in enumerate(open_issues):
                lines.extend([
                    "",
                    f"## Issue #{issue['id']}: {issue['issue_type']}",
                    f"**Timestamp:** {issue['timestamp']}",
                    f"**Prompt:** {issue['prompt']}",
                    f"**Model:** {issue.get('llm_model', 'unknown')}",
                    f"**Provider:** {issue.get('provider', 'unknown')}",
                    f"**Error:** {issue.get('error_message', 'N/A')}",
                    f"**LLM Response:** {issue.get('llm_response', 'N/A')[:500]}",
                    "---"
                ])

            return "\n".join(lines)

        else:  # JSON format
            return json.dumps(open_issues, indent=2, ensure_ascii=False)

    def clear_resolved_issues(self):
        """Remove resolved issues from log"""
        self.issues = [issue for issue in self.issues if issue['status'] != 'resolved']
        self._save_issues()
        print(f"[IssueLogger] Cleared {len(self.issues)} resolved issues")


# Global instance
_issue_logger = None


def get_issue_logger(log_file="logs/issues.json"):
    """Get the global issue logger instance"""
    global _issue_logger
    if _issue_logger is None:
        _issue_logger = IssueLogger(log_file)
    return _issue_logger


# Convenience functions for logging
def log_empty_output(prompt, llm_response="", llm_model="", provider="", context=""):
    """Log an empty output issue"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.EMPTY_OUTPUT,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider,
        context=context
    )


def log_simulation_error(prompt, error_message, llm_response="", llm_model="", provider=""):
    """Log a simulation error"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.SIMULATION_ERROR,
        error_message=error_message,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_invalid_circuit(prompt, error_message, llm_response="", llm_model="", provider=""):
    """Log an invalid circuit"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.INVALID_CIRCUIT,
        error_message=error_message,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_api_error(prompt, error_message, llm_response="", llm_model="", provider=""):
    """Log an API error"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.API_ERROR,
        error_message=error_message,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_timeout(prompt, error_message, llm_model="", provider=""):
    """Log a timeout"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.TIMEOUT,
        error_message=error_message,
        llm_model=llm_model,
        provider=provider
    )


def log_no_code_block(prompt, llm_response="", llm_model="", provider=""):
    """Log missing code block issue"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.NO_CODE_BLOCK,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_syntax_error(prompt, error_message, llm_response="", llm_model="", provider=""):
    """Log a syntax error"""
    logger = get_issue_logger()
    return logger.log_issue(
        prompt=prompt,
        issue_type=IssueType.SYNTAX_ERROR,
        error_message=error_message,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )