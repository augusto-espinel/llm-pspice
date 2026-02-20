"""
LLM-PSPICE Configuration

Centralized configuration for LLM-PSPICE simulation data storage.
All simulation data is stored OUTSIDE the workspace context to prevent
context overflow issues with large data files.
"""

import os
from pathlib import Path

# Base directory for all OpenClaw simulation data (outside workspace context)
SIMULATION_DATA_BASE = os.path.expanduser(r"~\.openclaw\simulation_data")

# LLM-PSPICE-specific directories
PSPICE_SIMULATION_DIR = os.path.join(SIMULATION_DATA_BASE, "llm-pspice")
PSPICE_DATA_DIR = os.path.join(PSPICE_SIMULATION_DIR, "data")
PSPICE_PLOTS_DIR = os.path.join(PSPICE_SIMULATION_DIR, "plots")
PSPICE_EXPORTS_DIR = os.path.join(PSPICE_SIMULATION_DIR, "exports")

def ensure_directories():
    """Ensure all configuration directories exist"""
    dirs_to_create = [
        SIMULATION_DATA_BASE,
        PSPICE_SIMULATION_DIR,
        PSPICE_DATA_DIR,
        PSPICE_PLOTS_DIR,
        PSPICE_EXPORTS_DIR
    ]

    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)

def get_data_dir():
    """Get the data directory for CSV exports"""
    ensure_directories()
    return PSPICE_DATA_DIR

def get_plots_dir():
    """Get the plots directory for images"""
    ensure_directories()
    return PSPICE_PLOTS_DIR

def get_exports_dir():
    """Get the exports directory for other simulation outputs"""
    ensure_directories()
    return PSPICE_EXPORTS_DIR

def get_simulation_dir():
    """Get the main LLM-PSPICE simulation directory"""
    ensure_directories()
    return PSPICE_SIMULATION_DIR

if __name__ == "__main__":
    print(f"LLM-PSPICE Configuration")
    print(f"=" * 70)
    print(f"Simulation Data Base: {SIMULATION_DATA_BASE}")
    print(f"LLM-PSPICE Directory: {PSPICE_SIMULATION_DIR}")
    print(f"Data Directory: {PSPICE_DATA_DIR}")
    print(f"Plots Directory: {PSPICE_PLOTS_DIR}")
    print(f"Exports Directory: {PSPICE_EXPORTS_DIR}")
    print(f"\nAll directories created: {ensure_directories()}")