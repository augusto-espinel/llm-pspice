"""
Enhanced Error Handling for LLM-PSPICE
Categorizes and provides user-friendly error messages for various failures
"""

import re
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors that can occur"""
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    API_ERROR = "api_error"
    MODEL_NOT_FOUND = "model_not_found"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CIRCUIT_INVALID = "circuit_invalid"
    SIMULATION_FAILED = "simulation_failed"
    UNKNOWN = "unknown"


class CircuitErrorHandler:
    """
    Enhanced error handler with categorization and user-friendly messages
    """

    # Known error patterns
    ERROR_PATTERNS = {
        ErrorCategory.AUTHENTICATION: [
            r'401',
            r'unauthorized',
            r'invalid api key',
            r'authentication failed',
            r'forbidden'
        ],
        ErrorCategory.NETWORK: [
            r'connection',
            r'network',
            r'dns',
            r'host unreachable',
            r'connection reset'
        ],
        ErrorCategory.TIMEOUT: [
            r'timeout',
            r'request timed out',
            r'server not responding'
        ],
        ErrorCategory.MODEL_NOT_FOUND: [
            r'model not found',
            r"model ['\"].*['\"] (not found|does not exist)",
            r'invalid model',
            r'unknown model'
        ],
        ErrorCategory.RATE_LIMIT: [
            r'429',
            r'too many requests',
            r'rate limit'
        ],
        ErrorCategory.CIRCUIT_INVALID: [
            r'duplicate declaration',
            r'struct ngcomplex',
            r'invalid component',
            r'node not found'
        ],
        ErrorCategory.SIMULATION_FAILED: [
            r'convergence',
            r'singular matrix',
            r'simulation failed',
            r'singular node',
            r'timestep too small'
        ]
    }

    def __init__(self):
        self.error_history = []

    def categorize_error(self, error_msg):
        """
        Categorize an error based on its message

        Args:
            error_msg (str): The error message to categorize

        Returns:
            ErrorCategory: The category of the error
        """
        error_msg_lower = error_msg.lower()

        for category, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_msg_lower):
                    return category

        return ErrorCategory.UNKNOWN

    def get_user_friendly_message(self, error_msg, error_type=None, context=""):
        """
        Get a user-friendly error message with suggestions

        Args:
            error_msg (str): The error message
            error_type (type): The exception type (optional)
            context (str): Additional context about where error occurred

        Returns:
            str: User-friendly error message with suggestions
        """
        category = self.categorize_error(error_msg.lower())

        # Log the error for debugging
        self.error_history.append({
            'timestamp': self._get_timestamp(),
            'category': category.value,
            'message': error_msg,
            'type': str(error_type) if error_type else None,
            'context': context
        })

        # Build user-friendly message
        message = self._build_message(category, error_msg, error_type, context)

        return message

    def _build_message(self, category, error_msg, error_type, context):
        """Build the user-friendly error message"""
        base_message = ""
        suggestions = ""
        technical_details = ""

        if category == ErrorCategory.AUTHENTICATION:
            base_message = "❌ Authentication Error"
            suggestions = """**Possible causes:**
• Your API key is invalid or expired
• You don't have access to this model
• Your subscription has expired

**Solutions:**
1. Generate a new API key (e.g., `ollama cloud key`)
2. Check your subscription status
3. Try using a different provider or model
"""

        elif category == ErrorCategory.NETWORK:
            base_message = "❌ Network Error"
            suggestions = """**Possible causes:**
• Internet connection issue
• Ollama Cloud service is down
• Corporate firewall or proxy blocking requests
• DNS resolution failure

**Solutions:**
1. Check your internet connection
2. Check Ollama status: https://status.ollama.ai
3. Try using a local model instead
4. If behind a proxy, configure HTTP_PROXY environment variable
"""

        elif category == ErrorCategory.TIMEOUT:
            base_message = "❌ Request Timed Out"
            suggestions = """**Possible causes:**
• Network is slow or congested
• Ollama Cloud service is overloaded
• Request is too complex and taking too long

**Solutions:**
1. Try again in a moment
2. Use a simpler prompt
3. Try using a recommended model: cogito-2.1:671b, qwen3-coder:480b
4. Use a local model for faster response
"""

        elif category == ErrorCategory.MODEL_NOT_FOUND:
            base_message = "❌ Model Not Found"
            suggestions = f"""**The model doesn't exist or you don't have access.**

**Recommended working models:**
• cogito-2.1:671b (recommended)
• qwen3-coder:480b (coding specialist)
• deepseek-v3.1:671b (reasoning)
• kimi-k2:1t (general purpose)

**Note:** Some models like glm-4.7 and glm-5 have known issues with empty responses.
"""

        elif category == ErrorCategory.RATE_LIMIT:
            base_message = "❌ Rate Limit Exceeded"
            suggestions = """**You've made too many requests.**

**Solutions:**
1. Wait a few minutes before trying again
2. Use a local model instead (no rate limits)
3. Upgrade your subscription for higher limits
4. Try a different provider
"""

        elif category == ErrorCategory.CIRCUIT_INVALID:
            base_message = "❌ Circuit Definition Error"
            suggestions = f"""**The circuit code has invalid syntax or structure.**

**Technical details:**
{error_msg[:300]}

**Solutions:**
1. Check if all components are properly defined
2. Verify node names match (e.g., 'n1', 'n2')
3. Make sure voltage and current units are correct (@ u_V, @ u_Ohm)
4. Try rephrasing your circuit description

**Example format:**
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('MyCircuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)
analysis = circuit.simulator().transient(
    step_time=0.1 @ u_ms,
    end_time=10 @ u_ms
)
```
"""

        elif category == ErrorCategory.SIMULATION_FAILED:
            base_message = "❌ Simulation Failed"
            suggestions = f"""**The simulation couldn't complete.**

**Technical details:**
{error_msg[:300]}

**Common causes:**
• Circuit has no DC path to ground
• Simulation timestep too small or too large
• Component values are unrealistic
• Singular matrix (check connections)

**Solutions:**
1. Add a ground reference (circuit.gnd)
2. Adjust simulation parameters (step_time, end_time)
3. Verify component connections
4. Try a simpler circuit first
"""

        else:  # UNKNOWN
            base_message = "❌ Unknown Error"
            suggestions = """**An unexpected error occurred.**

**Solutions:**
1. Try refreshing the page
2. Check if you're using the correct API key
3. Try using a different model
4. If the problem persists, it might be a temporary service issue
"""

        # Add technical details for debugging
        if error_type and str(error_type) not in ["None", "<class 'NoneType'>"]:
            technical_details = f"\n**Technical details:**\nError type: {error_type}\nDetails: {error_msg[:500]}"

        # Add context if provided
        if context:
            suggestions = f"**Context:** {context}\n\n{suggestions}"

        return f"{base_message}\n\n{suggestions}{technical_details}"

    def get_fallback_solution(self, category, user_request):
        """
        Get a fallback solution based on error category

        Args:
            category (ErrorCategory): The error category
            user_request (str): The original user request

        Returns:
            str: Fallback code or suggestion
        """
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.NETWORK,
                       ErrorCategory.TIMEOUT, ErrorCategory.RATE_LIMIT]:
            # For API errors, suggest using local model
            return f"""**Fallback suggestion:**

Since we're having issues with the cloud API, try switching to a local model:

1. In the sidebar, uncheck "Use Ollama Cloud"
2. Make sure Ollama is running locally
3. Try model: deepseek-r1:8b

Or use one of the pre-defined circuit templates:
- "Create a simple RC circuit"
- "Design a voltage divider"
- "Build an LED driver"
"""

        elif category in [ErrorCategory.CIRCUIT_INVALID, ErrorCategory.SIMULATION_FAILED]:
            # For circuit errors, provide a simple working example
            return """**Fallback circuit example:**

Here's a simple RC low-pass filter that usually works:

```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_LowPass_Filter')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

simulator = circuit.simulator()
analysis = simulator.transient(
    step_time=0.1 @ u_ms,
    end_time=10 @ u_ms
)
```

You can modify the R and C values to change the filter characteristics.
"""

        else:
            return "Please try again or use a simpler circuit description."

    def get_error_summary(self):
        """
        Get a summary of recent errors

        Returns:
            dict: Summary of errors by category
        """
        if not self.error_history:
            return {"total": 0, "by_category": {}}

        summary = {"total": len(self.error_history), "by_category": {}}

        for error in self.error_history:
            category = error['category']
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

        return summary

    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def clear_history(self):
        """Clear error history"""
        self.error_history = []


# Global error handler instance
error_handler = CircuitErrorHandler()


def handle_llm_error(error, user_request="", context=""):
    """
    Convenience function to handle LLM API errors

    Args:
        error: The exception that occurred
        user_request (str): The original user request
        context (str): Additional context

    Returns:
        str: User-friendly error message with suggestions
    """
    error_msg = str(error)
    error_type = type(error)

    # Get user-friendly message
    message = error_handler.get_user_friendly_message(
        error_msg,
        error_type,
        context
    )

    # Get fallback suggestion
    category = error_handler.categorize_error(error_msg)
    fallback = error_handler.get_fallback_solution(category, user_request)

    return f"{message}\n\n{fallback}"


def validate_circuit_code(code):
    """
    Validate circuit code before simulation (IMPROVED - 2026-02-22)

    Simplified, robust validation that checks for analysis assignment properly.
    Handles multi-line assignments like:
      analysis = circuit.simulator().transient(
          step_time=1 @ u_ms,
          end_time=10 @ u_ms
      )

    Args:
        code (str): The circuit code to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    # Remove comments to avoid false positives
    code_no_comments = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

    # Check for circuit creation
    if 'Circuit(' not in code:
        return False, "Missing circuit creation (Circuit('name'))"

    # Check for circuit assignment (must be outside comments)
    if not re.search(r'circuit\s*=\s*Circuit\(', code_no_comments):
        return False, "Missing circuit assignment (circuit = Circuit('name'))"

    # Check for transient or AC analysis call
    if '.transient(' not in code and '.ac(' not in code:
        return False, "Missing simulation method (.transient() or .ac())"

    # Check for analysis assignment - look for "analysis = ..." followed by transient/ac
    # This handles multi-line assignments
    lines = code.split('\n')
    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # Skip comment-only lines and empty lines
        if not line_stripped or line_stripped.startswith('#'):
            continue

        # Remove inline comments
        line_no_comment = re.sub(r'#.*$', '', line).strip()

        # Check for: analysis = ...
        if re.match(r'^analysis\s*=.*', line_no_comment):
            # Found analysis assignment - check if followed by transient/ac
            # Look at this line and the next few
            next_lines = '\n'.join(lines[i:i+5])
            next_lines_no_comments = re.sub(r'#.*$', '', next_lines, flags=re.MULTILINE)

            if '.transient(' in next_lines_no_comments or '.ac(' in next_lines_no_comments:
                # Good - analysis is assigned with simulation method
                return True, None

    # If we get here, no proper analysis assignment found
    return False, "Missing analysis assignment (should be: analysis = variable.function().transient(...) or analysis = variable.function().ac(...))"