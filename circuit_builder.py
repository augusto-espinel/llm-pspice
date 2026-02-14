"""
Circuit Builder - PySpice Integration
Builds and simulates circuits from Python code
"""

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import io
from error_handler import handle_llm_error, validate_circuit_code

class CircuitBuilder:
    """
    Builds and simulates circuits using PySpice (Ngspice backend)
    """
    
    def __init__(self):
        self.circuit = None
        self.analysis = None

    def _filter_pyspice_imports(self, code):
        """
        Filter out PySpice import statements to prevent duplicate Ngspice initialization errors.

        The LLM often generates code with import statements like:
            from PySpice.Spice.Netlist import Circuit
            from PySpice.Unit import *

        Since we already provide these in the namespace, executing these imports
        multiple times causes Ngspice to try to re-initialize, resulting in:
            "duplicate declaration of struct ngcomplex"

        Args:
            code (str): Raw LLM-generated code

        Returns:
            str: Code with PySpice imports removed
        """
        import re

        # Lines to remove (PySpice imports)
        import_patterns = [
            r'^\s*from PySpice[^#]*$',
            r'^\s*import PySpice[^#]*$',
            r'^\s*from pyspice[^#]*$',
            r'^\s*import pyspice[^#]*$',
            r'^\s*from ngspice[^#]*$',
            r'^\s*import ngspice[^#]*$',
        ]

        lines = code.split('\n')
        filtered_lines = []

        for line in lines:
            # Check if this line matches any import pattern
            is_import = False
            for pattern in import_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_import = True
                    print(f"[FILTER] Removed PySpice import: {line.strip()}")
                    break

            if not is_import:
                filtered_lines.append(line)

        # Also remove comments that are just PySpice-related import info
        # But keep other comments
        return '\n'.join(filtered_lines)

    def run_simulation(self, circuit_code):
        """
        Execute circuit code and run simulation
        
        Args:
            circuit_code (str): Python code that builds a PySpice circuit
            
        Returns:
            dict: Simulation results with plots and data
        """
        results = {
            'plots': [],
            'data': None,
            'error': None
        }
        
        try:
            # Filter out PySpice import statements to avoid duplicate initialization errors
            # LLM-generated code often includes imports which cause Ngspice to re-initialize
            filtered_code = self._filter_pyspice_imports(circuit_code)

            # Create a namespace for executing the circuit code
            # We provide Pre-imported PySpice objects to avoid duplication
            namespace = {
                'Circuit': Circuit,
                'u_kOhm': u_kOhm,
                'u_Ohm': u_Ohm,
                'u_V': u_V,
                'u_mA': u_mA,
                'u_A': u_A,
                'u_F': u_F,
                'u_H': u_H,
                'u_s': u_s,
                'u_ms': u_ms,
                'u_us': u_us,
                'u_mV': u_mV,
                'u_nF': u_nF,
                'u_pF': u_pF,
                'u_GHz': u_GHz,
                'u_MHz': u_MHz,
                'u_kHz': u_kHz,
                'u_Hz': u_Hz,
                'u_m': u_m,
                'u_mm': u_mm,
                'u_cm': u_cm,
                'u_km': u_km,
                'circuit': None,
                'analysis': None,
                'simulator': None  # Pre-declare simulator
            }

            # Pre-simulation validation
            is_valid, validation_error = validate_circuit_code(filtered_code)
            if not is_valid:
                raise ValueError(f"❌ Circuit validation failed:\n\n{validation_error}")

            # Execute the filtered circuit code
            try:
                exec(compile(filtered_code, '<string>', 'exec'), namespace)
            except Exception as e:
                error_msg = str(e)
                if 'duplicate declaration' in error_msg.lower() or 'struct ngcomplex' in error_msg.lower():
                    raise ValueError(
                        "❌ PySpice initialization error!\n\n"
                        "This happens when the LLM-generated code includes PySpice import statements.\n"
                        "The code has been filtered, but an error still occurred.\n\n"
                        f"Technical error: {error_msg}\n\n"
                        "Try:\n"
                        "1. Refreshing the page and trying again\n"
                        "2. Using a simpler circuit description"
                    )
                else:
                    raise

            self.circuit = namespace.get('circuit')

            if not self.circuit:
                raise ValueError("❌ No circuit defined. Your code should create a 'circuit' variable using Circuit().")

            # Get analysis results
            analysis = namespace.get('analysis')

            if analysis is None:
                raise ValueError("❌ No analysis results defined. Your code should create an 'analysis' variable using simulator.transient().")

            # Debug: Print what we got
            print(f"\n=== DEBUG INFO ===")
            print(f"Analysis type: {type(analysis)}")
            print(f"Analysis has time: {hasattr(analysis, 'time')}")

            if hasattr(analysis, 'time'):
                if hasattr(analysis.time, '__len__'):
                    print(f"Time length: {len(analysis.time)}")
                    if len(analysis.time) > 0:
                        print(f"Time range: {float(analysis.time[0]):.4f} to {float(analysis.time[-1]):.4f}")
                else:
                    print(f"Time: {analysis.time}")
            else:
                print("⚠️ Warning: No time data found!")

            if hasattr(analysis, 'nodes'):
                print(f"Analysis nodes: {analysis.nodes}")
            else:
                print("⚠️ Warning: No nodes attribute found!")

            # List all available variables in the analysis
            print("\nAvailable variables:")
            for attr in dir(analysis):
                if not attr.startswith('_'):
                    try:
                        val = getattr(analysis, attr)
                        if not callable(val):
                            if hasattr(val, '__len__'):
                                print(f"  - {attr}: array of {len(val)} {type(val).__name__}")
                            else:
                                print(f"  - {attr}: {type(val).__name__} = {val}")
                    except:
                        pass

            print("=== END DEBUG ===\n")

            results['data'] = self._extract_analysis_data(analysis)
            results['plots'] = self._generate_plots(analysis)

            # Debug: Check results
            print(f"Data rows: {len(results['data']) if results['data'] else 0}")
            print(f"Plots: {len(results['plots'])}")
            
        except Exception as e:
            results['error'] = str(e)
            results['error_type'] = type(e).__name__
            
        return results
    
    def _extract_analysis_data(self, analysis):
        """
        Extract numerical data from PySpice analysis

        Args:
            analysis: PySpice analysis object

        Returns:
            list: List of dictionaries with time and voltage/current data
        """
        data = []

        if analysis is None:
            print("Analysis is None")
            return data

        try:
            # Get time vector
            time = analysis.time if hasattr(analysis, 'time') else None

            if time is None:
                print("No time data found in analysis")
                return data

            # Convert time to numpy array if it isn't already
            if not isinstance(time, np.ndarray):
                time = np.array(time)

            print(f"Time data shape: {time.shape}")

            # For transient analysis, get all node voltages and branch currents
            # Try different ways to access variables
            if hasattr(analysis, 'nodes'):
                var_names = analysis.nodes
                print(f"Using nodes attribute: {var_names}")
            else:
                # Try to get all attributes that look like signals
                var_names = []
                for attr in dir(analysis):
                    if not attr.startswith('_') and attr not in ['time', 'frequency']:
                        try:
                            val = getattr(analysis, attr)
                            if hasattr(val, '__len__') and len(val) == len(time):
                                var_names.append(attr)
                                print(f"Found array variable: {attr} (length {len(val)})")
                        except:
                            pass

            # If no nodes found, try using bracket notation
            if not var_names:
                print("No nodes found, trying bracket notation...")
                # Try common node names
                common_nodes = ['out', 'n1', 'n2', 'input', 'v(in)', 'v(out)']
                for node in common_nodes:
                    try:
                        val = analysis[node]
                        if hasattr(val, '__len__') and len(val) == len(time):
                            var_names.append(node)
                            print(f"Found accessible node: {node}")
                    except:
                        pass

            print(f"Final variables to extract: {var_names}")

            for var_name in var_names:
                # Extract variable data
                try:
                    # Try bracket notation first
                    try:
                        values = analysis[str(var_name)]
                        print(f"✓ {var_name}: accessed via bracket notation")
                    except:
                        # Fall back to getattr
                        values = getattr(analysis, str(var_name))
                        print(f"✓ {var_name}: accessed via getattr")

                    # Convert unit to float
                    if hasattr(values, 'value'):
                        values = float(values.value)
                    else:
                        values = float(values)

                    # Handle single value vs array
                    if isinstance(values, np.ndarray) and len(values) == len(time):
                        print(f"  -> Array of {len(values)} values: [{values[0]:.4f} ... {values[-1]:.4f}]")
                        for i, t in enumerate(time):
                            data.append({
                                'time': float(t),
                                'variable': str(var_name),
                                'value': float(values[i])
                            })
                    else:
                        # Single value - repeat for all time points
                        print(f"  -> Single value: {values}")
                        for i, t in enumerate(time):
                            data.append({
                                'time': float(t),
                                'variable': str(var_name),
                                'value': float(values)
                            })
                except Exception as e:
                    print(f"✗ Error extracting '{var_name}': {e}")

            print(f"Extracted {len(data)} data points total")

        except Exception as e:
            print(f"Error extracting data: {e}")
            import traceback
            traceback.print_exc()

        return data
    
    def _generate_plots(self, analysis):
        """
        Generate matplotlib plots from analysis

        Args:
            analysis: PySpice analysis object

        Returns:
            list: List of matplotlib figure objects
        """
        plots = []

        if analysis is None:
            return plots

        try:
            fig, ax = plt.subplots(figsize=(10, 5))

            # Get time vector
            time = analysis.time if hasattr(analysis, 'time') else None

            if time is None:
                return plots

            # Get variable names - try nodes first, then try all attributes
            if hasattr(analysis, 'nodes'):
                var_names = analysis.nodes
            else:
                var_names = []
                for attr in dir(analysis):
                    if not attr.startswith('_') and attr not in ['time', 'frequency']:
                        try:
                            val = getattr(analysis, attr)
                            if hasattr(val, '__len__') and len(val) == len(time):
                                var_names.append(attr)
                        except:
                            pass

            print(f"Plotting variables: {var_names}")

            # Plot each variable
            plotted = False
            for var_name in var_names:
                try:
                    values = analysis[str(var_name)]

                    # Convert unit to float
                    if hasattr(values, 'value'):
                        values = float(values.value)
                    else:
                        values = float(values)

                    if len(time) > 1 and (isinstance(values, np.ndarray) and len(values) > 1):
                        ax.plot(time, values, label=str(var_name), linewidth=2)
                        plotted = True
                except Exception as e:
                    print(f"Error plotting '{var_name}': {e}")

            if plotted:
                ax.set_xlabel('Time', fontsize=12)
                ax.set_ylabel('Voltage (V) / Current (A)', fontsize=12)
                ax.set_title('Circuit Simulation Results', fontsize=14, fontweight='bold')
                ax.legend(loc='best', fontsize=10)
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                plots.append(fig)
            else:
                plt.close(fig)

        except Exception as e:
            print(f"Error generating plots: {e}")
            import traceback
            traceback.print_exc()

        return plots
    
    def create_simple_resistor_circuit(self):
        """
        Example: Create a simple resistor circuit
        """
        circuit = Circuit('Simple_Resistor')
        circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
        circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)
        
        return circuit
    
    def create_rc_circuit(self, R=1, C=10, source_voltage=10, duration=10):
        """
        Example: Create an RC circuit
        
        Args:
            R (float): Resistance in kΩ
            C (float): Capacitance in µF
            source_voltage (float): Source voltage in V
            duration (float): Simulation duration in ms
        """
        circuit = Circuit('RC_Circuit')
        circuit.V('input', 'n1', circuit.gnd, source_voltage @ u_V)
        circuit.R(1, 'n1', 'n2', R @ u_kOhm)
        circuit.C(1, 'n2', circuit.gnd, C @ u_F)
        
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=duration @ u_ms)
        
        return circuit, analysis
    
    def create_voltage_divider(self, R1=10, R2=10, source_voltage=12):
        """
        Example: Create a voltage divider circuit
        
        Args:
            R1 (float): Top resistance in kΩ
            R2 (float): Bottom resistance in kΩ
            source_voltage (float): Source voltage in V
        """
        circuit = Circuit('Voltage_Divider')
        circuit.V('input', 'n1', circuit.gnd, source_voltage @ u_V)
        circuit.R(1, 'n1', 'n2', R1 @ u_kOhm)
        circuit.R(2, 'n2', circuit.gnd, R2 @ u_kOhm)
        
        return circuit


if __name__ == "__main__":
    # Test the circuit builder
    builder = CircuitBuilder()
    
    # Test RC circuit
    circuit, analysis = builder.create_rc_circuit(R=1, C=10, source_voltage=10, duration=10)
    
    print(f"Circuit: {builder.circuit}")
    print(f"Analysis type: {type(analysis)}")