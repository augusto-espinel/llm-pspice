# LLM-PSPICE Data Storage Configuration

## Overview

To prevent context overflow errors when large simulation data files are generated (CSV exports, plot images, etc.), all LLM-PSPICE simulation data is **automatically stored outside the OpenClaw workspace context**.

## Storage Locations

All simulation data is stored in: `~/.openclaw/simulation_data/llm-pspice/`

Specifically:
- **Data**: `~/.openclaw/simulation_data/llm-pspice/data/` - CSV files and metadata
- **Plots**: `~/.openclaw/simulation_data/llm-pspice/plots/` - Plot images
- **Exports**: `~/.openclaw/simulation_data/llm-pspice/exports/` - Other simulation outputs

## Configuration Module

The `sim_config.py` module centralizes all data storage configuration:

```python
from sim_config import get_data_dir, get_plots_dir, get_exports_dir

# Get directories (automatically created if they don't exist)
data_dir = get_data_dir()
plots_dir = get_plots_dir()
exports_dir = get_exports_dir()
```

## Why This Matters

Previously, large simulation data files (e.g., 2.7MB GeckoExport1.txt, 1.9MB CSV files) were part of the workspace context. When these files were loaded into the LLM context, they caused:

- **Context overflow**: "prompt too long; exceeded max context length by 50083 tokens"
- **Slow loading**: Large files delayed workspace initialization
- **Token waste**: Simulation data consumed valuable LLM context space

By storing data outside the workspace:
- ✅ **No context overflow**: Large files never enter LLM context
- ✅ **Faster startup**: Workspace loading is faster
- ✅ **More context**: More tokens available for actual work
- ✅ **Persistent storage**: Data persists across sessions

## How It Works

### Automatic Saving

When a simulation completes in the Streamlit app:

1. Results are displayed in the UI
2. CSV can be downloaded via the download button
3. **Data is automatically saved** to `~/.openclaw/simulation_data/llm-pspice/data/` with timestamp
4. A metadata JSON file is also saved with simulation parameters

Example saved files:
```
~/.openclaw/simulation_data/llm-pspice/data/
├── 20260217_123456.csv
├── 20260217_123456_metadata.json
├── 20260217_130001.csv
└── 20260217_130001_metadata.json
```

### Workspace vs. Data

- **Workspace** (`~/.openclaw/workspace/llm-sim-poc/`):
  - Python code (`app.py`, `circuit_builder.py`, etc.)
  - Configuration (`.gitignore`, `.env.example`)
  - Documentation (README.md, guides)
  - **Does NOT contain simulation data**

- **Data Storage** (`~/.openclaw/simulation_data/llm-pspice/`):
  - CSV simulation results
  - Plot images
  - Metadata JSON files
  - Export files
  - **Separate from LLM workspace**

## Updating Your Code

If you need to save simulation data in custom scripts, use the configuration module:

```python
from sim_config import get_data_dir
import pandas as pd

# Your simulation...
df = pd.DataFrame(simulation_results)

# Save to data directory (outside context)
data_dir = get_data_dir()
df.to_csv(f"{data_dir}/my_simulation.csv", index=False)
```

## Troubleshooting

### Data Not Saving

If simulation data is not being saved automatically:

1. Check that `sim_config.py` exists in the project root
2. Verify write permissions to `~/.openclaw/simulation_data/`
3. Check Streamlit console for error messages

### Finding Your Data

Your simulation data is located at:
```bash
# On Windows
C:\Users\<username>\.openclaw\simulation_data\llm-pspice\data\

# On macOS/Linux
~/.openclaw/simulation_data/llm-pspice/data/
```

## Related Documentation

- `sim_config.py` - Configuration module source code
- `.gitignore` - Version control exclusions
- `app.py` - Main Streamlit application with auto-save