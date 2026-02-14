# LLM-Powered Circuit Simulation Environment

## 🌟 Proof of Concept

A Streamlit-based interface that lets you chat with an LLM to design, build, and simulate electronic circuits using PySpice (Python interface to Ngspice).

## 🎯 Why This Approach?

**Problems with Traditional Circuit Tools:**
- Steep learning curve (need to learn netlists, GUI interfaces)
- Limited programmatic manipulation
- Poor LLM integration (text-based netslists are hard to parse/generate)

**Our Solution:**
- **Python-native circuit definition**: PySpice lets you build circuits as Python objects
- **LLM-friendly**: Chat interface to describe circuits in natural language
- **Popular stack**: Python + Streamlit + PySpice (all open-source)
- **Quick PoC**: Build in minutes, not days

## 📚 Tech Stack

| Component | Tool | Why? |
|-----------|------|------|
| **Simulation** | PySpice + Ngspice | Python objects, not text netlists ✅ |
| **UI** | Streamlit | Build UI in pure Python in minutes ✅ |
| **LLM** | Multi-provider support | OpenAI, Gemini, Claude, DeepSeek, Ollama (local & cloud) ✅ |
| **Data/Vis** | Pandas + Matplotlib | CSV export + waveform plotting ✅ |

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ngspice** (installed separately):
   - Windows: Download from [ngspice.org](https://ngspice.sourceforge.io/downloads.html)
   - Mac: `brew install ngspice`
   - Linux: `sudo apt install ngspice`

### Installation

```bash
# 1. Navigate to project directory
cd llm-sim-poc

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

**Option 1: OpenAI API Key**

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

**Option 2: Ollama Cloud (Recommended for free users)**

1. Get your Ollama Cloud API key:
   ```bash
   ollama cloud key
   ```

2. In the app sidebar:
   - Select "Ollama" as LLM Provider
   - Check "Use Ollama Cloud"
   - Paste your API key
   - Select a working model (recommended: `cogito-2.1:671b`)

See `OLLAMA_CLOUD_GUIDE.md` for more details.

**Option 3: Local Ollama**

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull deepseek-r1:8b`
3. In the app sidebar, select "Ollama" with cloud disabled

**Without an API key:**
- The app will use **fallback templates** for common circuits
- Not as powerful, but still functional for basic demos

**Gemini, Claude, DeepSeek:**

These providers are also supported - enter your API key in the sidebar after selecting the provider.

### Running the App

```bash
streamlit run app.py
```

The app will open at: `http://localhost:8501`

## 💡 Usage

### Interface Layout

```
┌─────────────────────┬──────────────────────────┐
│   💬 Chat (Left)    │   📊 Results (Right)      │
│                     │                          │
│  - Type requests    │  - Waveform plots        │
│  - View LLM code    │  - Numerical data        │
│  - Chat history     │  - CSV download          │
│                     │                          │
└─────────────────────┴──────────────────────────┘
```

### Example Queries

Try these in the chat:

- *"Create a simple RC circuit with R=1kΩ, C=10µF"*
- *"Design a voltage divider with 12V input"*
- *"Build an LED driver circuit with 5V input"*
- *"Simulate a low-pass filter with cutoff 1kHz"*

### Workflow

1. **Describe circuit** → Type in chat box
2. **LLM generates code** → PySpice circuit definition
3. **Auto-simulate** → Runs Ngspice in background
4. **View results** → Waveforms + CSV export

## 📁 Project Structure

```
llm-sim-poc/
│
├── app.py                       # Streamlit UI (chat + plots)
├── circuit_builder.py           # PySpice circuit integration
├── llm_orchestrator.py          # LLM interface + multi-provider support
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .env.example                 # API key template
├── saved_api_keys.json          # Saved API keys (auto-generated)
│
├── OLLAMA_CLOUD_GUIDE.md        # Ollama Cloud setup guide
├── OLLAMA_CLOUD_TROUBLESHOOTING.md  # Known issues & fixes
│
└── test_*.py                    # Test scripts for development
```

## 🔧 How It Works

### Architecture

```
User Request (Chat)
        ↓
    LLM Orchestrator
        ↓
  Generate PySpice Code
        ↓
    Circuit Builder
        ↓
      Ngspice Simulation
        ↓
    Extract Results
        ↓
  Streamlit Display
   (Plots + CSV)
```

### PySpice Example

**Traditional (Netlist):**
```spice
* RC Circuit
V1 1 0 10
R1 1 2 1k
C1 2 0 10u
.tran 0.1m 10m
.end
```

**PySpice (Python objects):**
```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

circuit = Circuit('RC_Circuit')
circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
circuit.R(1, 'n1', 'n2', 1 @ u_kOhm)
circuit.C(1, 'n2', circuit.gnd, 10 @ u_F)

analysis = circuit.simulator().transient(
    step_time=0.1 @ u_us, 
    end_time=10 @ u_ms
)
```

**Why PySpice wins:**
- ✅ LLM-friendly (Python syntax, not netlist)
- ✅ Type-safe units (can't mix kΩ and Ω)
- ✅ Programmatic manipulation (loops, conditionals)
- ✅ Easy to debug (Python traceback vs cryptic SPICE errors)

## 🐛 Known Limitations (PoC)

1. **Ngspice Binary**: Must be installed separately
2. **LLM Fallback**: Without API key, only basic templates
3. **Circuit Complexity**: Limited to linear components (no diodes, transistors in fallback mode)
4. **Error Handling**: Basic error display (no circuit validation pre-simulation)

## 🚀 Current Features ✅

- [x] Multi-provider LLM support (OpenAI, Gemini, Claude, DeepSeek, Ollama)
- [x] Ollama Cloud API integration with model selection
- [x] Local Ollama model support
- [x] API key persistence across sessions
- [x] Model dropdowns for easy selection
- [x] Fixed PySpice duplicate declaration errors
- [x] Fixed duplicate output (extract first code block)

## 🚀 Future Enhancements

- [ ] Add support for non-linear components (diodes, transistors)
- [ ] Circuit schematic visualization (circuit diagram rendering)
- [ ] Circuit library (save/load designs)
- [ ] AC analysis (frequency response, Bode plots)
- [ ] Parameter sweep (vary R, C, L values automatically)
- [ ] Comparative simulations (compare multiple designs)
- [ ] Enhanced error validation (pre-simulation checks)

## 📖 Resources

- **PySpice Docs**: https://pyspice.fabrice-salvaire.fr/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Ngspice Manual**: http://ngspice.sourceforge.net/docs/manual
- **Circuit Design Guide**: https://www.eevblog.com/

## 🤝 Contributing

This is a PoC. Feel free to fork, experiment, and extend!

## 📝 License

MIT License - Use, modify, distribute freely

---

Built with ⚡ by Augusto Espinel Porras for the OpenClaw workspace