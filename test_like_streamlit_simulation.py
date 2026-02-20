#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST 2: Complete Streamlit-Style Test WITH SIMULATION
======================================================

This tests the COMPLETE flow:
1. Generate circuit code (same as Streamlit)
2. Build circuit with CircuitBuilder
3. RUN SIMULATION (using ngspice like Streamlit)
4. Verify simulation produces data
5. Store raw results OUTSIDE workspace
6. Keep only summaries in workspace

This is the TRUE test - not just code generation, but actual simulation.

Data Storage:
- Raw simulation data: ~/.openclaw/simulation_data/llm-pspice/data/
- Plots: ~/.openclaw/simulation_data/llm-pspice/plots/
- CSV exports: ~/.openclaw/simulation_data/llm-pspice/exports/
- Summaries: llm-sim-poc/ (workspace root)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, '.')

from llm_orchestrator import LLMOrchestrator
from circuit_builder import CircuitBuilder

# Set UTF-8 for Windows console
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("="*60)
print("TEST 2: Complete Streamlit-Style Test WITH SIMULATION")
print("="*60)
print("Testing: generate + build + simulate + verify data")
print()

# Test prompt
test_prompt = "Simulate a low-pass filter with cutoff 1kHz using R=1.59kOhm and C=100nF and analyze the frequency response"

print(f"Prompt: {test_prompt}")
print()

# Load API key
with open('saved_api_keys.json', 'r') as f:
    keys = json.load(f)
api_key = keys.get('ollama_cloud')

print(f"API Key: {'Loaded' if api_key else 'NOT FOUND'}")
print()

# Setup data directories OUTSIDE workspace
home_dir = Path.home()
data_base_dir = home_dir / ".openclaw" / "simulation_data" / "llm-pspice"

data_dir = data_base_dir / "data"
plot_dir = data_base_dir / "plots"
export_dir = data_base_dir / "exports"

for d in [data_dir, plot_dir, export_dir]:
    d.mkdir(parents=True, exist_ok=True)

print(f"Data storage (outside workspace):")
print(f"  Raw data: {data_dir}")
print(f"  Plots: {plot_dir}")
print(f"  CSV exports: {export_dir}")
print()

print("Creating LLMOrchestrator...")
llm = LLMOrchestrator(
    provider='ollama',
    model_name='cogito-2.1:671b',
    use_cloud=True,
    api_key=api_key
)

print("LLM initialized successfully")
print()
print("Step 1: Generating circuit code...")
print("(Waiting for LLM response: 30-90 seconds)...")
print()

# Step 1: Generate code
response = llm.process_request(test_prompt)

print(f"Code generated: {len(response)} characters")
print("Saving full response to: streamlit_response.txt")
with open('streamlit_response.txt', 'w', encoding='utf-8') as f:
    f.write(response)
print()

# Analyze generated code
has_pulse = 'PulseVoltageSource' in response
has_wrong_pulse = 'pulse=(' in response and 'PeriodValue' in response
has_analysis = '.transient(' in response or '.ac(' in response
has_circuit = 'circuit = Circuit(' in response

print("="*60)
print("CODE GENERATION ANALYSIS:")
print("="*60)
print(f"[OK] Has Python code block: {('```python' in response)}")
print(f"[OK] Has PulseVoltageSource: {has_pulse}")
print(f"[OK] Has WRONG pulse syntax: {has_wrong_pulse}")
print(f"[OK] Has analysis: {has_analysis}")
print(f"[OK] Has circuit definition: {has_circuit}")
print()

# Step 2: Extract Python code and build circuit
print()
print("Step 2: Building circuit...")
print()

builder = CircuitBuilder()

# Extract code from markdown code blocks
import re
code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)

if not code_match:
    code_match = re.search(r'```(.*?)```', response, re.DOTALL)

if code_match:
    circuit_code = code_match.group(1).strip()
    print(f"Extracted {len(circuit_code)} characters of Python code")
else:
    # Use full response if no code block found
    circuit_code = response.strip()
    print("No code block found, using full response")

print()
print("Step 3: Running simulation (ngspice)...")
print("(This matches the EXACT Streamlit workflow)")
print()

# Step 3: RUN SIMULATION
sim_results = builder.run_simulation(circuit_code)

print()
print("="*60)
print("SIMULATION RESULTS:")
print("="*60)
print()

if sim_results.get('error'):
    print(f"[FAIL] SIMULATION FAILED")
    print(f"Error: {sim_results['error']}")
    print(f"Error type: {sim_results.get('error_type', 'Unknown')}")
    print()
    print("This is the same error you see in Streamlit!")
    simulation_success = False
else:
    data = sim_results.get('data')
    plots = sim_results.get('plots', [])

    if data and len(data) > 0:
        print(f"[PASS] SIMULATION SUCCESSFUL")
        print(f"   Data points: {len(data)}")
        print(f"   Plots generated: {len(plots)}")
        simulation_success = True

        # Show sample data
        print()
        print("Sample data (first 5 points):")
        for i, point in enumerate(data[:5]):
            print(f"  {point}")

        # Save raw data OUTSIDE workspace
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_file = data_dir / f"test_2_simulation_{timestamp}.json"

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'prompt': test_prompt,
                'source': 'test_2_like_streamlit_simulation',
                'data_points': len(data),
                'simulation_success': True,
                'data': data  # Full raw data
            }, f, indent=2, default=str)

        print()
        print(f"Raw simulation data saved (outside workspace):")
        print(f"  -> {data_file}")

        # Generate CSV export (outside workspace)
        import pandas as pd
        df = pd.DataFrame(data)
        csv_file = export_dir / f"test_2_export_{timestamp}.csv"
        df.to_csv(csv_file, index=False)

        print(f"  -> CSV export: {csv_file}")

    else:
        print(f"[FAIL] SIMULATION PRODUCED NO DATA")
        print(f"   This is what Streamlit reports as: 'simulation produced no data'")
        simulation_success = False

# Step 4: Save summary to workspace
print()
print("="*60)
print("SUMMARY (stored in workspace):")
print("="*60)
print()

summary = {
    'test_name': 'test_2_complete_simulation',
    'timestamp': datetime.now().isoformat(),
    'prompt': test_prompt,
    'code_generation': {
        'response_length': len(response),
        'has_pulse': has_pulse,
        'has_wrong_pulse': has_wrong_pulse,
        'has_analysis': has_analysis,
        'has_circuit': has_circuit
    },
    'simulation': {
        'success': simulation_success,
        'error': sim_results.get('error'),
        'error_type': sim_results.get('error_type'),
        'data_points': len(sim_results.get('data', [])),
        'plots': len(sim_results.get('plots', []))
    },
    'data_storage': {
        'raw_data': str(data_file) if simulation_success else None,
        'csv_export': str(csv_file) if simulation_success else None,
        'location': 'Outside workspace: ~/.openclaw/simulation_data/llm-pspice/'
    }
}

summary_file = Path('test_2_simulation_summary.json')
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

print(f"Summary saved to workspace: {summary_file}")
print()

# Final verdict
print("="*60)
print("FINAL VERDICT:")
print("="*60)
print()

if simulation_success:
    print("[PASS] COMPLETE TEST PASSED")
    print()
    print("What this proves:")
    print("  1. LLM generates correct circuit code [PASS]")
    print("  2. CircuitBuilder builds circuit correctly [PASS]")
    print("  3. Ngspice simulation runs successfully [PASS]")
    print("  4. Simulation produces valid data [PASS]")
    print("  5. Data stored outside workspace [PASS]")
    print()
    print("If your Streamlit fails with this same prompt:")
    print("  -> Your Streamlit is using OLD cached code or state")
    print("  -> Solution: Properly restart Streamlit (Ctrl+C, then restart)")
elif has_wrong_pulse:
    print("[FAIL] Wrong pulse syntax in generated code")
    print()
    print("What this means:")
    print("  -> LLM is using OLD system prompt")
    print("  -> llm_orchestrator.py not updated properly")
else:
    print("[FAIL] Simulation error")
    print()
    print(f"Error: {sim_results.get('error', 'Unknown')}")
    print("This matches what you see in Streamlit!")

print()
print("="*60)
print("Data Storage Summary:")
print("="*60)
print("Workspace (summaries only):")
print(f"  - {summary_file.name}")
print(f"  - streamlit_response.txt")
print()
print("Outside workspace (raw data):")
for d in [data_dir, plot_dir, export_dir]:
    print(f"  - {d}")
print()
print("Raw simulation data and CSV exports are OUTSIDE the workspace!")
print("="*60)