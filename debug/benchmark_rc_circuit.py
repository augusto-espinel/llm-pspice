"""
RC Circuit Benchmark - Pure Python Implementation

This benchmark calculates RC circuit behavior using analytical differential equations
without using PySpice. It serves as a reference to validate PySpice simulations.

The model considers first-order RC circuits (resistor-capacitor in series).

Author: Benchmark for LLM-PSPICE validation
Date: 2026-02-14
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict


class RCCircuitBenchmark:
    """
    RC Circuit Benchmark Calculator

    Calculates voltage and current responses for RC circuits using analytical solutions.
    """

    def __init__(self, R: float, C: float, V_in: float):
        """
        Initialize RC circuit parameters.

        Args:
            R: Resistance in Ohms
            C: Capacitance in Farads
            V_in: Input voltage in Volts
        """
        self.R = R  # Ohms
        self.C = C  # Farads
        self.V_in = V_in  # Volts
        self.tau = R * C  # Time constant (seconds)

    def charging_response(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate voltage and current for charging transient (step input).

        For an RC circuit with step input V_in:
        - Vc(t) = V_in * (1 - exp(-t / tau))
        - I(t) = (V_in / R) * exp(-t / tau)

        Args:
            t: Time array (seconds)

        Returns:
            Tuple of (voltage_capacitor, current)
        """
        voltage_capacitor = self.V_in * (1 - np.exp(-t / self.tau))
        current = (self.V_in / self.R) * np.exp(-t / self.tau)

        return voltage_capacitor, current

    def discharging_response(self, initial_voltage: float, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate voltage and current for discharging transient.

        For an RC circuit discharging from initial voltage:
        - Vc(t) = V0 * exp(-t / tau)
        - I(t) = (V0 / R) * exp(-t / tau) (negative, flowing out)

        Args:
            initial_voltage: Initial capacitor voltage (V0)
            t: Time array (seconds)

        Returns:
            Tuple of (voltage_capacitor, current)
        """
        voltage_capacitor = initial_voltage * np.exp(-t / self.tau)
        current = (-initial_voltage / self.R) * np.exp(-t / self.tau)

        return voltage_capacitor, current

    def steady_state_ac_response(self, t: np.ndarray, frequency: float,
                                 amplitude: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate AC steady-state response (sinusoidal input).

        For sinusoidal input:
        - Vc(t) = V_in * (1 / sqrt(1 + (wRC)^2)) * sin(wt - phi)
        - phi = arctan(wRC)

        Args:
            t: Time array (seconds)
            frequency: Frequency in Hz
            amplitude: Input voltage amplitude

        Returns:
            Tuple of (voltage_capacitor, current, voltage_input, phase_shift_rad)
        """
        omega = 2 * np.pi * frequency  # Angular frequency
        Xc = 1 / (omega * self.C)  # Capacitive reactance
        Z = np.sqrt(self.R**2 + Xc**2)  # Impedance magnitude

        # Voltagedivider ratio
        ratio = Xc / Z

        # Phase shift (capacitor voltage lags input)
        phase_shift = np.arctan(self.R * omega * self.C)

        # Input voltage
        voltage_input = amplitude * np.sin(omega * t)

        # Capacitor voltage (scaled and phase-shifted)
        voltage_capacitor = amplitude * ratio * np.sin(omega * t - phase_shift)

        # Current (in phase with input voltage scaled by impedance)
        current = (amplitude / Z) * np.sin(omega * t + np.arctan(Xc / self.R))

        return voltage_capacitor, current, voltage_input, phase_shift

    def get_summary(self) -> Dict:
        """
        Get circuit parameters summary.

        Returns:
            Dictionary with circuit parameters
        """
        return {
            'resistance_ohms': self.R,
            'capacitance_farads': self.C,
            'input_voltage_volts': self.V_in,
            'time_constant_seconds': self.tau,
            'cutoff_frequency_hz': 1 / (2 * np.pi * self.tau),
            'initial_current_amps': self.V_in / self.R,
            'steady_state_voltage_volts': self.V_in
        }


def compare_with_analytical(time_data: np.ndarray, v_analytical: np.ndarray,
                             v_simulation: np.ndarray, tolerance_percent: float = 5.0) -> Dict:
    """
    Compare simulation results with analytical solution.

    Args:
        time_data: Time array
        v_analytical: Analytical voltage (benchmark)
        v_simulation: Simulation voltage
        tolerance_percent: Acceptable error percentage

    Returns:
        Dictionary with comparison metrics
    """
    # Ensure arrays are same length
    min_len = min(len(v_analytical), len(v_simulation))
    v_analytical = v_analytical[:min_len]
    v_simulation = v_simulation[:min_len]
    time_data = time_data[:min_len]

    # Calculate absolute and relative errors
    absolute_error = np.abs(v_simulation - v_analytical)
    relative_error = np.abs((v_simulation - v_analytical) / np.maximum(v_analytical, 1e-10)) * 100

    # Calculate metrics
    max_abs_error = np.max(absolute_error)
    max_rel_error = np.max(relative_error)
    mean_abs_error = np.mean(absolute_error)
    mean_rel_error = np.mean(relative_error)
    rms_error = np.sqrt(np.mean(absolute_error**2))

    # Check if within tolerance
    passes = np.all(relative_error <= tolerance_percent)
    pass_rate = np.sum(relative_error <= tolerance_percent) / len(relative_error) * 100

    return {
        'max_absolute_error_volts': max_abs_error,
        'max_relative_error_percent': max_rel_error,
        'mean_absolute_error_volts': mean_abs_error,
        'mean_relative_error_percent': mean_rel_error,
        'rms_error_volts': rms_error,
        'within_tolerance': passes,
        'pass_rate_percent': pass_rate,
        'tolerance_percent': tolerance_percent,
        'data_points': min_len
    }


def plot_comparison(time_data: np.ndarray, v_analytical: np.ndarray,
                     v_simulation: np.ndarray, i_analytical: np.ndarray = None,
                     i_simulation: np.ndarray = None,
                     save_path: str = 'comparison_plot.png') -> None:
    """
    Plot comparison between analytical and simulation results.

    Args:
        time_data: Time array
        v_analytical: Analytical voltage
        v_simulation: Simulation voltage
        i_analytical: Analytical current (optional)
        i_simulation: Simulation current (optional)
        save_path: Path to save figure (optional)
    """
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Voltage comparison
    ax1.plot(time_data * 1000, v_analytical, 'b-', label='Analytical (Benchmark)', linewidth=2)
    ax1.plot(time_data * 1000, v_simulation, 'r--', label='PySpice Simulation', linewidth=1.5, alpha=0.8)
    ax1.set_ylabel('Voltage (V)', fontsize=12)
    ax1.set_title('RC Circuit Response - Voltage Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Current comparison (if provided)
    if i_analytical is not None and i_simulation is not None:
        ax2.plot(time_data * 1000, i_analytical * 1000, 'b-', label='Analytical (Benchmark)', linewidth=2)
        ax2.plot(time_data * 1000, i_simulation * 1000, 'r--', label='PySpice Simulation', linewidth=1.5, alpha=0.8)
    ax2.set_xlabel('Time (ms)', fontsize=12)
    ax2.set_ylabel('Current (mA)', fontsize=12)
    ax2.set_title('RC Circuit Response - Current Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Figure saved to: {save_path}")
    plt.close()  # Close figure instead of showing  # Close figure instead of showing


def main():
    """
    Main function to demonstrate benchmark usage.
    """
    print("="*60)
    print("RC Circuit Benchmark - Pure Python Implementation")
    print("="*60)
    print()

    # Circuit parameters (RC low-pass filter)
    R = 1000  # 1 kOhm
    C = 10e-6  # 10 uF
    V_in = 10  # 10 Volts

    print(f"Circuit Parameters:")
    print(f"  Resistance: {R:.0f} Ohms")
    print(f"  Capacitance: {C*1e6:.1f} uF")
    print(f"  Input Voltage: {V_in:.1f} V")
    print()

    # Create benchmark
    bench = RCCircuitBenchmark(R, C, V_in)

    # Print summary
    summary = bench.get_summary()
    print(f"Circuit Summary:")
    print(f"  Time Constant (tau): {summary['time_constant_seconds']*1000:.2f} ms")
    print(f"  Cutoff Frequency: {summary['cutoff_frequency_hz']:.2f} Hz")
    print(f"  Initial Current: {summary['initial_current_amps']*1000:.1f} mA")
    print(f"  Steady State Voltage: {summary['steady_state_voltage_volts']:.1f} V")
    print()

    # Time array for simulation (5 time constants for full transient)
    time_array = np.linspace(0, 5 * bench.tau, 1000)

    # Calculate response
    v_cap, current = bench.charging_response(time_array)

    print(f"Simulation Results (Analytical Solution):")
    print(f"  Time range: 0 to {time_array[-1]*1000:.2f} ms")
    print(f"  Number of points: {len(time_array)}")
    print(f"  Final capacitor voltage: {v_cap[-1]:.4f} V")
    print(f"  Final current: {current[-1]*1000:.4f} mA")
    print()

    # Create sample data for comparison (simulated PySpice results)
    # In reality, this would come from PySpice simulation
    # Here we add small noise to simulate realistic simulation
    noise_level = 0.01  # 1% noise
    v_simulation = v_cap * (1 + np.random.normal(0, noise_level, len(v_cap)))
    i_simulation = current * (1 + np.random.normal(0, noise_level, len(current)))

    # Compare with benchmark
    comparison = compare_with_analytical(time_array, v_cap, v_simulation)

    print(f"Comparison Metrics (Benchmark vs Simulation):")
    print(f"  Max absolute error: {comparison['max_absolute_error_volts']:.4f} V")
    print(f"  Max relative error: {comparison['max_relative_error_percent']:.2f}%")
    print(f"  Mean absolute error: {comparison['mean_absolute_error_volts']:.4f} V")
    print(f"  Mean relative error: {comparison['mean_relative_error_percent']:.2f}%")
    print(f"  RMS error: {comparison['rms_error_volts']:.4f} V")
    print(f"  Pass rate (within 5% tolerance): {comparison['pass_rate_percent']:.1f}%")
    print()

    # Plot comparison
    print("Generating comparison plot...")
    plot_comparison(time_array, v_cap, v_simulation, current, i_simulation)

    # Save data for later use
    np.savez('benchmark_data.npz',
             time=time_array,
             v_analytical=v_cap,
             i_analytical=current,
             v_simulation=v_simulation,
             i_simulation=i_simulation,
             params=summary)

    print(f"Benchmark data saved to: benchmark_data.npz")
    print()

    # Create a simple test case that Ralph can use
    print("="*60)
    print("TEST CASE FOR RALPH")
    print("="*60)
    print()
    print("Ralph should generate PySpice code for this circuit:")
    print()
    print("  Circuit: RC low-pass filter")
    print(f"  R = {R} Ohms")
    print(f"  C = {C*1e6} uF")
    print(f"  Vin = {V_in} V (step input)")
    print(f"  Simulation: Transient analysis")
    print(f"  Step time: {bench.tau*0.1*1000:.2f} ms")
    print(f"  End time: {bench.tau*5*1000:.2f} ms")
    print()
    print("Expected results (benchmark):")
    print(f"  Time constant: {bench.tau*1000:.2f} ms")
    print(f"  Final voltage: ~{V_in*0.993:.2f} V (99.3% of Vin)")
    print(f"  Final current: ~0 mA")
    print()
    print("Success criteria:")
    print(f"  - Voltage error < 5%")
    print(f"  - Current error < 5%")
    print(f"  - Time constant accurate within 5%")
    print()


if __name__ == "__main__":
    main()