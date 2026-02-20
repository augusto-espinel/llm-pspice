"""
Ralph Tester - Automated testing module for verifying fixes
Retries failed prompts with improved system prompts to verify they work

UPDATED: Uses the same API keys and models as Streamlit app
"""

import json
import os
from datetime import datetime
from app_issue_reader import get_issue_logger
from llm_orchestrator import LLMOrchestrator
from circuit_builder import CircuitBuilder

# Same API key file as Streamlit app
API_KEY_FILE = "saved_api_keys.json"


def load_api_key(provider):
    """Load API key from file (same as Streamlit app)"""
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                keys = json.load(f)
                return keys.get(provider, None)
        return None
    except Exception as e:
        print(f"[RalphTester] Error loading API key: {e}")
        return None


class RalphTester:
    """
    Tests improved system prompts and fixes to verify they actually work

    UPDATED: Uses the same models, providers, and API keys as Streamlit app
    """

    def __init__(self, logger=None, test_all=False):
        self.logger = logger if logger else get_issue_logger()
        self.test_all = test_all
        self.test_results = []

    def test_improved_prompt(self, improved_prompt_text, issues_to_test=None):
        """
        Test improved system prompt against failed prompts

        Args:
            improved_prompt_text (str): The improved system prompt to test
            issues_to_test (list): List of issue IDs to test (optional)

        Returns:
            dict: Test results summary
        """
        print(f"[RalphTester] Testing improved prompt against failed prompts...")
        print(f"[RalphTester] Using same models and API keys as Streamlit app")

        # Get issues to test
        all_issues = self.logger.read_all_issues()

        if issues_to_test:
            issues = [i for i in all_issues if i.get('id') in issues_to_test]
        else:
            # Test recent open issues
            issues = self.logger.get_open_issues()

        if not issues:
            print("[RalphTester] No issues to test!")
            return {
                'total_tested': 0,
                'successful': 0,
                'failed': 0,
                'inconclusive': 0,
                'results': []
            }

        # Test each issue
        results = []
        successful_count = 0
        failed_count = 0
        inconclusive_count = 0

        for issue in issues:
            print(f"\n[RalphTester] Testing issue #{issue['id']}: {issue['prompt'][:50]}...")

            test_result = self._test_single_prompt(
                prompt=issue['prompt'],
                improved_prompt=improved_prompt_text,
                original_issue=issue
            )

            results.append(test_result)

            if test_result['status'] == 'success':
                successful_count += 1
                print(f"  [OK] SUCCESS: {test_result['reason']}")
            elif test_result['status'] == 'failed':
                failed_count += 1
                print(f"  [FAIL] FAILED: {test_result['reason']}")
            else:
                inconclusive_count += 1
                print(f"  [WARN] INCONCLUSIVE: {test_result['reason']}")

            self.test_results.append(test_result)

        summary = {
            'total_tested': len(issues),
            'successful': successful_count,
            'failed': failed_count,
            'inconclusive': inconclusive_count,
            'success_rate': f"{(successful_count / len(issues) * 100):.1f}%" if issues else "N/A",
            'timestamp': datetime.now().isoformat(),
            'results': results
        }

        print(f"\n{'='*60}")
        print(f"[RalphTester] Test Summary:")
        print(f"  Total tested:   {summary['total_tested']}")
        print(f"  Successful:     {summary['successful']} [OK]")
        print(f"  Failed:         {summary['failed']} [FAIL]")
        print(f"  Inconclusive:   {summary['inconclusive']} [WARN]")
        print(f"  Success rate:   {summary['success_rate']}")
        print(f"{'='*60}")

        return summary

    def _test_single_prompt(self, prompt, improved_prompt, original_issue):
        """
        Test a single prompt with improved system prompt
        Uses the SAME model, provider, and API key as Streamlit app

        Args:
            prompt (str): Original failed prompt
            improved_prompt (str): Improved system prompt to use
            original_issue (dict): Original issue data

        Returns:
            dict: Test result with status and details
        """
        try:
            # Extract original model and provider info
            original_model = original_issue.get('llm_model', 'deepseek-r1:8b')
            original_provider = original_issue.get('provider', 'ollama').lower()

            # Determine if this was a cloud model
            # Cloud models typically have ":" in name (e.g., cogito-2.1:671b)
            is_cloud_model = ':' in original_model and original_provider == 'ollama'

            use_cloud = is_cloud_model

            print(f"  Model:    {original_model}")
            print(f"  Provider: {original_provider}")
            print(f"  Use Cloud: {use_cloud}")

            # Load API key if cloud
            api_key = None
            if use_cloud:
                api_key = load_api_key('ollama_cloud')
                if not api_key:
                    print(f"  [WARN] No Ollama Cloud API key found, falling back to local")
                    use_cloud = False
                    original_model = 'deepseek-r1:8b'
                else:
                    print(f"  [OK] Using Ollama Cloud API key")

            # Create LLM orchestrator with SAME settings as Streamlit app
            llm = LLMOrchestrator(
                provider='ollama',
                model_name=original_model,
                use_cloud=use_cloud,
                api_key=api_key
            )

            # Replace system prompt temporarily
            original_system_prompt = llm._get_system_prompt()
            llm._get_system_prompt = lambda: improved_prompt

            # Get LLM response (same as Streamlit app)
            print(f"  [RalphTester] Getting LLM response...")
            response = llm.process_request(prompt)

            # Check if response is valid
            if not response or not response.strip():
                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'failed',
                    'reason': 'Empty response from LLM (same error)',
                    'prompt': prompt,
                    'llm_response': '',
                    'simulation_result': None,
                    'error_type': 'empty_output'
                }

            # Check if response contains Python code
            if '```python' not in response:
                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'failed',
                    'reason': 'No Python code block generated (same error)',
                    'prompt': prompt,
                    'llm_response': response[:200],
                    'simulation_result': None,
                    'error_type': 'no_code_block'
                }

            # Extract code block (same as Streamlit app)
            code_blocks = []
            parts = response.split('```')
            for part in parts:
                if part.startswith('python'):
                    code = part[6:].strip()
                    code_blocks.append(code)

            if not code_blocks:
                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'failed',
                    'reason': 'Could not extract code block',
                    'prompt': prompt,
                    'llm_response': response[:200],
                    'simulation_result': None,
                    'error_type': 'extraction_failed'
                }

            circuit_code = code_blocks[0]

            print(f"  [RalphTester] Running circuit simulation (same as Streamlit)...")

            # Try to run simulation (same CircuitBuilder as Streamlit app)
            builder = CircuitBuilder()
            results = builder.run_simulation(circuit_code)

            # Check simulation results
            if results.get('error'):
                error_msg = results['error']

                # Check if it's the same error type as original
                original_error = original_issue.get('error_message', '').lower()

                if 'convergence' in error_msg.lower() or 'singular' in error_msg.lower():
                    if 'ground' not in original_error:
                        # Improved prompt should have fixed ground reference
                        return {
                            'issue_id': original_issue['id'],
                            'original_model': original_model,
                            'use_cloud': use_cloud,
                            'status': 'failed',
                            'reason': f'Simulation failed: convergence issue (ground reference not fixed)',
                            'prompt': prompt,
                            'llm_response': response[:300],
                            'simulation_result': {'error': error_msg},
                            'error_type': 'simulation_error'
                        }

                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'inconclusive',
                    'reason': f'Simulation error: {error_msg[:100]}',
                    'prompt': prompt,
                    'llm_response': response[:300],
                    'simulation_result': {'error': error_msg},
                    'error_type': 'different_error'
                }

            elif not results.get('data') or len(results.get('data', [])) == 0:
                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'inconclusive',
                    'reason': 'Simulation ran but produced no data (possible improvement but not full fix)',
                    'prompt': prompt,
                    'llm_response': response[:300],
                    'simulation_result': results,
                    'error_type': 'no_data'
                }

            else:
                # SUCCESS!
                data_points = len(results.get('data', []))
                return {
                    'issue_id': original_issue['id'],
                    'original_model': original_model,
                    'use_cloud': use_cloud,
                    'status': 'success',
                    'reason': f'Working circuit! Simulation ran successfully with {data_points} data points',
                    'prompt': prompt,
                    'llm_response': response[:300],
                    'simulation_result': {
                        'data_points': data_points,
                        'has_plots': 'plots' in results
                    },
                    'evidence': f'Generated {data_points} simulation data points using {original_model}',
                    'tested_with': f'{original_model} (cloud={use_cloud})'
                }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return {
                'issue_id': original_issue['id'],
                'original_model': original_issue.get('llm_model', 'unknown'),
                'use_cloud': False,
                'status': 'inconclusive',
                'reason': f'Error during testing: {str(e)[:100]}',
                'prompt': prompt,
                'llm_response': 'error',
                'simulation_result': None,
                'error_type': 'test_error',
                'traceback': error_trace[:500]
            }

    def generate_test_report(self):
        """Generate a test report for all tests run"""
        if not self.test_results:
            return "No tests run yet."

        lines = [
            "# Ralph Test Report",
            f"Tests run: {len(self.test_results)}",
            f"Timestamp: {datetime.now().isoformat()}",
            "",
            "## Results by Status",
            ""
        ]

        successful = [r for r in self.test_results if r['status'] == 'success']
        failed = [r for r in self.test_results if r['status'] == 'failed']
        inconclusive = [r for r in self.test_results if r['status'] == 'inconclusive']

        lines.extend([
            f"✅ Successful: {len(successful)}",
            f"❌ Failed: {len(failed)}",
            f"⚠️ Inconclusive: {len(inconclusive)}",
            ""
        ])

        # Group by model
        models = {}
        for r in self.test_results:
            model = r.get('original_model', 'unknown')
            if model not in models:
                models[model] = {'total': 0, 'success': 0, 'failed': 0}
            models[model]['total'] += 1
            if r['status'] == 'success':
                models[model]['success'] += 1
            else:
                models[model]['failed'] += 1

        lines.extend(["## Results by Model", ""])
        for model, stats in sorted(models.items()):
            lines.append(f"{model}:")
            lines.append(f"  Total: {stats['total']}, Success: {stats['success']}, Failed: {stats['failed']}")
            lines.append(f"  Success rate: {(stats['success']/stats['total']*100):.1f}% if stats['total'] > 0 else 'N/A'")
            lines.append("")

        if successful:
            lines.extend(["## Successful Tests", ""])
            for r in successful[:5]:  # Show top 5
                tested_with = r.get('tested_with', 'unknown')
                lines.extend([
                    f"Issue #{r['issue_id']}: {r['reason']}",
                    f"  Tested with: {tested_with}",
                    f"  Prompt: {r['prompt'][:60]}...",
                    ""
                ])

        if failed:
            lines.extend(["## Failed Tests", ""])
            for r in failed[:5]:  # Show top 5
                lines.extend([
                    f"Issue #{r['issue_id']}: {r['reason']}",
                    f"  Tested with: {r.get('original_model', 'unknown')}",
                    f"  Prompt: {r['prompt'][:60]}...",
                    ""
                ])

        return "\n".join(lines)

    def save_test_results(self, filename="logs/ralph_test_results.json"):
        """Save test results to file"""
        log_dir = os.path.dirname(filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        print(f"[RalphTester] Test results saved to {filename}")


# Convenience function
def test_improvements(improved_prompt_text, issues_to_test=None):
    """
    Test improved system prompt using same models as Streamlit app

    Args:
        improved_prompt_text (str): Improved system prompt to test
        issues_to_test (list): List of issue IDs to test (optional)

    Returns:
        dict: Test results
    """
    tester = RalphTester()
    return tester.test_improved_prompt(improved_prompt_text, issues_to_test)


if __name__ == "__main__":
    print("="*60)
    print("Ralph Tester - Testing with Streamlit App Settings")
    print("="*60)

    # Test with existing improved prompt
    if os.path.exists('improved_system_prompt.txt'):
        with open('improved_system_prompt.txt', 'r', encoding='utf-8') as f:
            improved_prompt = f.read()

        print("\nTesting improved_system_prompt.txt...")
        print("Using same models, providers, and API keys as Streamlit app")
        print("="*60)

        results = test_improvements(improved_prompt)

        print(f"\nTest results saved to logs/ralph_test_results.json")
        print(f"Test report: logs/ralph_test_report.md")

        # Save report
        tester = RalphTester()
        report = tester.generate_test_report()
        with open('logs/ralph_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
    else:
        print("No improved_system_prompt.txt found.")
        print("Run Ralph first to generate one: python test_ralph.py")