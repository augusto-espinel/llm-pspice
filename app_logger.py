"""
Simple App Logger - Production logging only
Logs failures to JSON without any Ralph/agent dependencies
"""

import json
import os
from datetime import datetime


class AppLogger:
    """
    Simple file logger for the LLM-PSPICE app
    Logs failures without any dependencies on Ralph or other tools
    """

    def __init__(self, log_file="logs/issues.json"):
        self.log_file = log_file
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def log_issue(self, prompt, issue_type, error_message="", **metadata):
        """
        Log an issue (production use only)

        Args:
            prompt (str): The original user prompt
            issue_type (str): Type of issue (empty_output, simulation_error, etc.)
            error_message (str): Error message if any
            **metadata: Additional info (llm_model, provider, etc.)
        """
        issue = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'issue_type': issue_type,
            'error_message': error_message,
            'metadata': metadata
        }

        # Append to JSON as a new line (line-delimited JSON for streaming compatibility)
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Read existing issues
        issues = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    issues = json.load(f)
            except Exception as e:
                print(f"[AppLogger] Warning: Could not read existing log: {e}")

        # Add new issue
        issues.append(issue)

        # Write back
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(issues, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[AppLogger] Error writing log: {e}")


# Global instance
_logger = None


def get_logger():
    """Get the global app logger instance"""
    global _logger
    if _logger is None:
        _logger = AppLogger()
    return _logger


# Convenience functions
def log_empty(prompt, llm_model="", provider="", context="", debug_info=None):
    """
    Log empty output issue (IMPROVED - 2026-02-22)

    Now includes detailed debugging information to diagnose root cause.

    Args:
        prompt: User prompt
        llm_model: LLM model name
        provider: Provider (Ollama, etc.)
        context: Context message
        debug_info: Dict with additional debug info (analysis type, has_time, has_nodes, etc.)
    """
    logger = get_logger()

    # Build enhanced metadata with debug info
    metadata = {
        'llm_model': llm_model,
        'provider': provider,
        'context': context
    }

    # Add debug info if provided (for root cause analysis)
    if debug_info:
        metadata.update(debug_info)

    logger.log_issue(
        prompt=prompt,
        issue_type="empty_output",
        **metadata
    )


def log_simulation_error(prompt, error_message, llm_model="", provider=""):
    """Log simulation error"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="simulation_error",
        error_message=error_message,
        llm_model=llm_model,
        provider=provider
    )


def log_invalid_circuit(prompt, error_message, llm_model="", provider=""):
    """Log invalid circuit"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="invalid_circuit",
        error_message=error_message,
        llm_model=llm_model,
        provider=provider
    )


def log_api_error(prompt, error_message, llm_model="", provider=""):
    """Log API error"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="api_error",
        error_message=error_message,
        llm_model=llm_model,
        provider=provider
    )


def log_timeout(prompt, error_message, llm_model="", provider=""):
    """Log timeout"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="timeout",
        error_message=error_message,
        llm_model=llm_model,
        provider=provider
    )


def log_no_code_block(prompt, llm_response="", llm_model="", provider=""):
    """Log missing code block"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="no_code_block",
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_syntax_error(prompt, error_message, llm_response="", llm_model="", provider=""):
    """Log syntax error"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="syntax_error",
        error_message=error_message,
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )


def log_response_duplication(prompt, llm_response="", llm_model="", provider="", details=""):
    """Log response duplication issue"""
    logger = get_logger()
    logger.log_issue(
        prompt=prompt,
        issue_type="response_duplication",
        error_message=details if details else "LLM response appears to be duplicated",
        llm_response=llm_response,
        llm_model=llm_model,
        provider=provider
    )