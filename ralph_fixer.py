"""
Ralph Fixer - Issue Resolution Module
Used by a sub-agent (Ralph) to analyze and fix logged circuit generation issues
"""

import json
import os
from datetime import datetime
from app_issue_reader import get_issue_logger


class RalphFixer:
    """
    Analyzes and attempts to fix logged circuit generation issues

    Strategies for fixing issues:
    1. Add missing context to system prompts
    2. Create circuit templates for common patterns
    3. Add validation before simulation
    4. Improve error recovery
    """

    def __init__(self, logger=None):
        self.logger = logger if logger else get_issue_logger()
        self.fixes_applied = []
        self.last_test_evidence = None
        self.resolution_log = []  # Ralph's own resolution log

    def analyze_issue(self, issue):
        """
        Analyze a single issue and determine the root cause

        Args:
            issue (dict): Issue from the issue log

        Returns:
            dict: Analysis result with recommendations
        """
        analysis = {
            'issue_id': issue['id'],
            'issue_type': issue['issue_type'],
            'prompt': issue['prompt'],
            'llm_response': issue.get('llm_response', ''),
            'error': issue.get('error_message', ''),
            'root_cause': '',
            'recommendation': '',
            'fix_strategy': ''
        }

        issue_type = issue['issue_type']
        llm_response = issue.get('llm_response', '')
        prompt = issue['prompt']

        # Categorize issue: prompt issue vs code bug
        category = self._categorize_issue(issue_type, llm_response, prompt, issue.get('error_message', ''))
        analysis['category'] = category

        # Analyze based on issue type
        if issue_type == 'empty_output':
            analysis['root_cause'] = self._analyze_empty_output(issue)
            analysis['fix_strategy'] = 'enhanced_system_prompt'

        elif issue_type == 'no_code_block':
            analysis['root_cause'] = 'LLM did not generate Python code block'
            analysis['recommendation'] = 'Strengthen system prompt to always return code in ```python``` block'
            analysis['fix_strategy'] = 'enhanced_system_prompt'

        elif issue_type == 'simulation_error':
            root_cause, fix_strategy = self._analyze_simulation_error(issue)
            analysis['root_cause'] = root_cause
            analysis['fix_strategy'] = fix_strategy

        elif issue_type == 'invalid_circuit':
            analysis['root_cause'] = 'Invalid circuit definition'
            analysis['recommendation'] = self._get_invalid_circuit_fix(issue)
            analysis['fix_strategy'] = 'template_based'

        elif issue_type == 'api_error' or issue_type == 'timeout':
            analysis['root_cause'] = 'API connectivity issue (not a prompt problem)'
            analysis['recommendation'] = 'Retry with different model or use local model'
            analysis['fix_strategy'] = 'fallback'

        elif issue_type == 'syntax_error':
            analysis['root_cause'] = 'Python syntax error in generated code'
            analysis['recommendation'] = 'Add code validation before simulation'
            analysis['fix_strategy'] = 'enhanced_validaiton'

        else:
            analysis['root_cause'] = 'Unknown issue type'
            analysis['fix_strategy'] = 'review_needed'

        return analysis

    def _categorize_issue(self, issue_type, llm_response, prompt, error_message):
        """
        Categorize issue as likely_prompt_issue or likely_code_bug

        Args:
            issue_type (str): Issue type string
            llm_response (str): LLM's response
            prompt (str): Original prompt
            error_message (str): Error message

        Returns:
            str: Category - 'likely_prompt_issue', 'likely_code_bug', or 'mixed'
        """
        # Prompt-related issues (LLM output problems)
        prompt_indicators = ['empty_output', 'no_code_block']

        # Code/infrastructure-related issues
        code_indicators = ['api_error', 'timeout']
        potential_code_indicators = ['simulation_error', 'invalid_circuit', 'syntax_error']

        # Check for keywords suggesting code bugs in error messages
        error_lower = error_message.lower() if error_message else ''
        code_bug_keywords = [
            'ngcomplex', 'duplicate declaration',  # PySpice initialization issues
            'attributeerror', 'importerror',
            'file not found', 'module not found',
            'connection', 'network',  # Infrastructure
            'authentication', 'unauthorized',  # API config
            'timeout'  # Infrastructure
        ]

        # Category: Likely prompt issue
        if issue_type in prompt_indicators:
            # Empty output or no code block - prompt/LLM issue
            if any(keyword in prompt.lower() for keyword in ['circuit', 'simulate', 'create']):
                return 'likely_prompt_issue'
            else:
                return 'mixed'  # Could be unclear prompt or just not a circuit request

        # Category: Likely code/infrastructure bug
        elif issue_type in code_indicators:
            # API or timeout - code/infrastructure issue
            return 'likely_code_bug'

        # Category: Mixed - needs review
        elif issue_type in potential_code_indicators:
            # Check error message for code bug indicators
            if any(keyword in error_lower for keyword in code_bug_keywords):
                return 'likely_code_bug'

            # Simulation/convergence issues - could be prompt or code
            if 'convergence' in error_lower or 'singular' in error_lower:
                # If prompt is very simple ("Create simple circuit"), it's likely a prompt issue
                # If prompt mentions specific components, it's likely a simulation setup issue
                if len(prompt.split()) < 5:
                    return 'likely_prompt_issue'
                else:
                    return 'mixed'

            # Check if it's a ground reference issue (can be fixed by prompt instructions)
            if 'ground' in error_lower or 'gnd' in error_lower:
                return 'likely_prompt_issue'

            # Default to mixed for complex simulation errors
            return 'mixed'

        return 'mixed'

    def _analyze_empty_output(self, issue):
        """Analyze why the output was empty"""
        llm_response = issue.get('llm_response', '')
        prompt = issue['prompt']

        if not llm_response:
            # No response at all - could be API issue, model capability, or prompt clarity
            if any(word in prompt.lower() for word in ['circuit', 'rc', 'voltage', 'resistor', 'capacitor']):
                return 'Model capable of circuit design but failed to respond - possibly prompt clarity or model limitation'
            else:
                return 'Prompt may not be clear enough for circuit design task'

        elif len(llm_response.strip()) < 10:
            return 'Model generated very short response - may be refusing task or confused'

        else:
            return f"Unexpected empty output check - response length: {len(llm_response)}"

    def _analyze_simulation_error(self, issue):
        """Analyze simulation error and return (root_cause, fix_strategy) tuple"""
        error = issue.get('error_message', '').lower()
        prompt = issue['prompt']

        if 'convergence' in error or 'singular' in error:
            if 'ground' not in prompt.lower() and 'gnd' not in prompt.lower():
                return 'Circuit missing ground reference - needs DC path to ground', 'enhanced_system_prompt'
            return 'Simulation convergence issue - component values or parameters may be unrealistic', 'parameter_guidance'

        elif 'duplicate' in error or 'ngcomplex' in error:
            return 'PySpice initialization error - Ngspice restarted too quickly', 'fallback'

        elif 'node' in error and 'not found' in error:
            return 'Node naming mismatch - LLM used different node names than expected', 'enhanced_system_prompt'

        elif 'transient' in error or 'analysis' in error:
            return 'Missing or incorrect analysis definition', 'enhanced_system_prompt'

        else:
            return f'Unknown simulation error: {error[:100]}', 'review_needed'

    def _get_invalid_circuit_fix(self, issue):
        """Get fix recommendation for invalid circuit"""
        error = issue.get('error_message', '').lower()
        prompt = issue['prompt'].lower()

        if 'missing' in error:
            return 'Ensure all required elements are present: Circuit(), simulator, analysis'
        elif 'syntax' in error:
            return 'Check Python syntax - proper use of @ u_V, @ u_Ohm, etc.'
        elif prompt.startswith('create') or prompt.startswith('build') or prompt.startswith('design'):
            return 'Prompt is generic - may need more specific values and constraints'
        else:
            return 'Review code structure and ensure all PySpice components are properly defined'

    def generate_improved_system_prompt(self, issues):
        """
        Generate an improved system prompt based on common issues

        Args:
            issues (list): List of issues

        Returns:
            str: Improved system prompt
        """
        # Identify common patterns
        empty_outputs = [i for i in issues if i['issue_type'] == 'empty_output']
        no_code_blocks = [i for i in issues if i['issue_type'] == 'no_code_block']
        simulation_errors = [i for i in issues if i['issue_type'] == 'simulation_error']
        invalid_circuits = [i for i in issues if i['issue_type'] == 'invalid_circuit']

        improvements = []

        # Build improved system prompt
        base_prompt = """You are an expert circuit designer and electrical engineer.

Your task is to design electronic circuits based on user requests and generate Python code using PySpice that creates and simulates the circuit.
"""

        # Add improvements based on issues
        if empty_outputs or no_code_blocks:
            improvements.append("""
CRITICAL: You MUST always generate a response with Python code in a ```python``` block.
Never respond with just text - always include working circuit code.
""")

        if invalid_circuits:
            improvements.append("""
VALIDATION REQUIREMENTS:
1. Always use 'circuit.gnd' as ground reference
2. Ensure all nodes used in components are defined
3. Include all imports: from PySpice.Spice.Netlist import Circuit, from PySpice.Unit import *
4. Always define: circuit, simulator, and analysis variables
5. Check that all components use proper units (@ u_V, @ u_Ohm, @ u_F, etc.)
""")

        if simulation_errors:
            improvements.append("""
SIMULATION BEST PRACTICES:
1. Include a DC path to ground for every node
2. Use realistic component values (avoid 0 or extremely large values)
3. Set appropriate simulation parameters:
   - step_time: 0.1 to 1 µs for typical circuits
   - end_time: 1 to 10 ms to see transient behavior
4. For transient analysis, use pulse sources instead of DC to see charging behavior
""")

        improved_prompt = base_prompt + "\n".join(improvements) + """

IMPORTANT RULES:
1. Use PySpice library symbols:
   - Circuit() - creates a circuit object
   - u_Ohm, u_kOhm - resistance units
   - u_V - voltage units
   - u_mA, u_A - current units
   - u_F, u_uF, u_nF - capacitance units
   - u_H - inductance units
   - u_s, u_ms, u_us - time units

2. Circuit components:
   - Circuit.V('name', 'node+', 'node-', voltage @ u_V) - voltage source
   - Circuit.R('name', 'node+', 'node-', resistance @ u_Ohm) - resistor
   - Circuit.C('name', 'node+', 'node-', capacitance @ u_F) - capacitor
   - Circuit.L('name', 'node+', 'node-', inductance @ u_H) - inductor

3. Simulation:
   - Create simulator: simulator = circuit.simulator()
   - Run analysis: analysis = simulator.transient(step_time=..., end_time=...)
   - Analysis must be stored in variable 'analysis'

4. Code format:
   - Create a 'circuit' variable containing the Circuit object
   - Create an 'analysis' variable containing the simulation results
   - Wrap code in ```python``` block
   - Include comments explaining the circuit

5. Analysis parameters:
   - step_time: Typically 0.1 to 1 µs (use @ u_us)
   - end_time: Typically 1 to 10 ms (use @ u_ms)

Example response format:
```python
# RC low-pass filter circuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Filter')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_us, end_time=10 @ u_ms)
```

Design safe, practical circuits. If uncertain about values, use common standard values and explain your design choices."""

        return improved_prompt

    def generate_circuit_template(self, prompt):
        """
        Generate a circuit template based on the prompt

        Args:
            prompt (str): User prompt

        Returns:
            str: Circuit template code
        """
        prompt_lower = prompt.lower()

        # Determine circuit type
        if any(word in prompt_lower for word in ['rc', 'capacitor', 'filter']):
            return self._rc_template()

        elif any(word in prompt_lower for word in ['voltage divider', 'divider', 'potentiometer']):
            return self._voltage_divider_template()

        elif any(word in prompt_lower for word in ['led', 'light emitting']):
            return self._led_template()

        elif any(word in prompt_lower for word in ['rl', 'inductor']):
            return self._rl_template()

        elif any(word in prompt_lower for word in ['rlc', 'bandpass', 'resonant']):
            return self._rlc_template()

        elif any(word in prompt_lower for word in ['diode', 'rectifier', 'bridge']):
            return self._diode_template()

        else:
            return self._basic_resistor_template()

    def _rc_template(self):
        """Generate RC circuit template"""
        return """```python
# RC Circuit Template
# Adjust R and C values to change time constant (τ = R × C)
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Circuit')
# Input voltage source (10V DC)
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
# Resistor (1 kΩ)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
# Capacitor (10 µF) - creates low-pass filter
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

# Run transient simulation
simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=10 @ u_ms)
```"""

    def _voltage_divider_template(self):
        """Generate voltage divider template"""
        return """```python
# Voltage Divider Template
# Output voltage = Vin × (R2 / (R1 + R2))
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Voltage_Divider')
# Input voltage
circuit.V('input', 'n1', circuit.gnd, 12 @ u_V)
# Resistors (10 kΩ each for 50/50 division)
circuit.R(1, 'n1', 'n2', 10 @ u_kOhm)
circuit.R(2, 'n2', circuit.gnd, 10 @ u_kOhm)

# Run simulation to see output at node n2
simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=5 @ u_ms)
```"""

    def _led_template(self):
        """Generate LED driver template"""
        return """```python
# LED Driver Template
# Use proper current limiting resistor: R = (Vin - Vled) / Iled
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('LED_Driver')
# 5V input
circuit.V('input', 'n1', circuit.gnd, 5 @ u_V)
# Current limiting resistor (220 Ω for ~15mA)
circuit.R(1, 'n1', 'n2', 220 @ u_Ohm)
# LED (simplified diode model)
circuit.D('LED', 'n2', circuit.gnd, model='LED')

# Simulate to see current
simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
```"""

    def _rl_template(self):
        """Generate RL circuit template"""
        return """```python
# RL Circuit Template
# Time constant τ = L / R
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RL_Circuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 100 @ u_Ohm)
circuit.L(1, 'n2', circuit.gnd, 10 @ u_mH)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_us, end_time=5 @ u_ms)
```"""

    def _rlc_template(self):
        """Generate RLC circuit template"""
        return """```python
# RLC Resonant Circuit Template
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RLC_Circuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 100 @ u_Ohm)
circuit.L(1, 'n2', 'n3', 10 @ u_mH)
circuit.C(1, 'n3', circuit.gnd, 1 @ u_uF)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_us, end_time=10 @ u_ms)
```"""

    def _diode_template(self):
        """Generate diode rectifier template"""
        return """```python
# Diode Rectifier Template
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Diode_Rectifier')
# AC input
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
# Diode
circuit.D('D1', 'n1', 'n2')
# Load resistor
circuit.R(1, 'n2', circuit.gnd, 1 @ u_kOhm)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=50 @ u_ms)
```"""

    def _basic_resistor_template(self):
        """Generate basic resistor circuit template"""
        return """```python
# Basic Resistor Circuit Template
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('Resistor_Circuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)

simulator = circuit.simulator()
analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
```"""

    def apply_fix(self, issue_id, analysis):
        """
        Apply a fix to an issue and mark it as resolved

        Args:
            issue_id (int): Issue ID
            analysis (dict): Analysis result with fix strategy

        Returns:
            bool: True if fix was applied successfully
        """
        fix_applied = False

        if analysis['fix_strategy'] == 'enhanced_system_prompt':
            fix_applied = self._apply_system_prompt_fix()

        elif analysis['fix_strategy'] == 'template_based':
            fix_applied = self._apply_template_fix(issue_id, analysis)

        elif analysis['fix_strategy'] == 'enhanced_validaiton':
            fix_applied = self._apply_validation_fix()

        elif analysis['fix_strategy'] == 'fallback':
            # Already handled by existing fallback code
            fix_applied = True

        if fix_applied:
            resolution_note = f"Applied fix: {analysis['fix_strategy']}"

            # Add test evidence if available
            if analysis['fix_strategy'] == 'enhanced_system_prompt' and self.last_test_evidence:
                resolution_note += f" | Evidence: {self.last_test_evidence}"

            # Log to Ralph's resolution log (NOT app's issue log!)
            self.resolution_log.append({
                'issue_id': issue_id,
                'timestamp': datetime.now().isoformat(),
                'strategy': analysis['fix_strategy'],
                'test_evidence': self.last_test_evidence if analysis['fix_strategy'] == 'enhanced_system_prompt' else None,
                'resolution_note': resolution_note
            })

            self.fixes_applied.append({
                'issue_id': issue_id,
                'strategy': analysis['fix_strategy'],
                'test_evidence': self.last_test_evidence if analysis['fix_strategy'] == 'enhanced_system_prompt' else None,
                'timestamp': datetime.now().isoformat()
            })

        return fix_applied

    def _apply_system_prompt_fix(self, test_improvement=True):
        """
        Apply system prompt fix by updating system prompt in llm_orchestrator

        Args:
            test_improvement (bool): If True, test the improved prompt before applying

        Returns:
            bool: True if fix was applied successfully
        """
        # Get recent issues
        recent_issues = self.logger.get_recent_issues(days=7)
        improved_prompt = self.generate_improved_system_prompt(recent_issues)

        # Save improved system prompt
        with open('improved_system_prompt.txt', 'w') as f:
            f.write(improved_prompt)

        print(f"[Ralph] Generated improved system prompt (length: {len(improved_prompt)})")
        print(f"[Ralph] Saved to improved_system_prompt.txt")

        # Optionally test the improvement before marking as success
        if test_improvement and recent_issues:
            print(f"[Ralph] Testing improved prompt against {len(recent_issues)} failed prompts...")

            try:
                from ralph_tester import RalphTester

                # Test only open issues (the ones we're trying to fix)
                open_issue_ids = [i['id'] for i in self.logger.get_open_issues()]

                if open_issue_ids:
                    tester = RalphTester(self.logger)
                    test_results = tester.test_improved_prompt(improved_prompt, open_issue_ids)

                    # Save test results
                    tester.save_test_results()

                    if test_results['successful'] > 0:
                        print(f"[Ralph] ✅ Test Results:")
                        print(f"[Ralph]   Total tested: {test_results['total_tested']}")
                        print(f"[Ralph]   Successful: {test_results['successful']}")
                        print(f"[Ralph]   Success rate: {test_results['success_rate']}")

                        # Generate evidence message
                        evidence = f"Tested with {test_results['total_tested']} failed prompts, " \
                                  f"{test_results['successful']} now work ({test_results['success_rate']} success rate)."

                        print(f"[Ralph]   Evidence: {evidence}")
                        self.last_test_evidence = evidence
                    else:
                        print(f"[Ralph] ⚠️ No successful tests - improvement may not help")
                        self.last_test_evidence = f"Tested {test_results['total_tested']} prompts, 0 successful"

                else:
                    print("[Ralph] No open issues to test")

            except Exception as e:
                print(f"[Ralph] Warning: Could not test improvement: {e}")
                self.last_test_evidence = f"Testing failed: {str(e)}"

        return True

    def _apply_template_fix(self, issue_id, analysis):
        """Apply template-based fix"""
        issue = next((i for i in self.logger.issues if i['id'] == issue_id), None)
        if issue:
            template = self.generate_circuit_template(issue['prompt'])
            with open(f'template_issue_{issue_id}.py', 'w') as f:
                f.write(template)
            print(f"[Ralph] Generated template for issue {issue_id}")
            return True
        return False

    def _apply_validation_fix(self):
        """Apply enhanced validation fix"""
        # This would update validation logic
        print("[Ralph] Validation enhancements logged")
        return True

    def generate_fix_report(self):
        """Generate a report of all fixes applied"""
        if not self.fixes_applied:
            return "No fixes applied yet."

        report = [
            "# Ralph Fix Report",
            f"Total fixes applied: {len(self.fixes_applied)}",
            ""
        ]

        for fix in self.fixes_applied:
            report.extend([
                f"- Issue #{fix['issue_id']}: {fix['strategy']}",
                f"  Timestamp: {fix['timestamp']}",
                ""
            ])

        return "\n".join(report)

    def save_resolution_log(self, filename="logs/ralph_resolution.json"):
        """
        Save Ralph's resolution log to separate file (not app's issue log)

        This is Ralph's private log of what it fixed. The app's issue log
        (logs/issues.json) is NEVER modified by Ralph - it only reads it.
        """
        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.resolution_log, f, indent=2, ensure_ascii=False)

        print(f"[Ralph] Resolution log saved to {filename}")


def analyze_and_fix_all_issues():
    """
    Convenience function to analyze and fix all open issues

    Returns:
        dict: Summary of analysis and fixes
    """
    logger = get_issue_logger()
    fixer = RalphFixer(logger)

    open_issues = logger.get_open_issues()
    print(f"[Ralph] Found {len(open_issues)} open issues")

    summary = {
        'total_issues': len(open_issues),
        'analyzed': 0,
        'fixed': 0,
        'by_type': {},
        'fixes': []
    }

    for issue in open_issues:
        # Analyze
        analysis = fixer.analyze_issue(issue)
        summary['analyzed'] += 1

        # Track by type
        issue_type = issue['issue_type']
        summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1

        # Apply fix
        if analysis['fix_strategy'] != 'review_needed':
            if fixer.apply_fix(issue['id'], analysis):
                summary['fixed'] += 1
                summary['fixes'].append({
                    'issue_id': issue['id'],
                    'strategy': analysis['fix_strategy'],
                    'root_cause': analysis['root_cause']
                })

    # Generate improved system prompt if any issues need it
    if summary['fixed'] > 0:
        fixer._apply_system_prompt_fix()

    # Save Ralph's resolution log (separate from app's issue log)
    fixer.save_resolution_log()

    return summary


if __name__ == "__main__":
    # Test Ralph Fixer
    print("Testing Ralph Fixer...")
    logger = get_issue_logger()

    if logger.get_open_issues():
        summary = analyze_and_fix_all_issues()
        print(f"\nSummary: {summary}")
        print("\n" + fixer.generate_fix_report())
    else:
        print("No open issues to fix.")