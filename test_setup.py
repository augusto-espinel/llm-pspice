"""
Test script to verify PySpice and Ngspice installation
"""

import sys
from PySpice.Unit import *

def test_imports():
    """Test if required packages are installed"""
    print("📦 Testing package imports...")
    
    packages = {
        "PySpice": "PySpice",
        "streamlit": "streamlit",
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "numpy": "numpy"
    }
    
    failed = []
    for name, module in packages.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name} - Not installed")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print(f"Run: pip install {' '.join(failed)}")
        return False
    
    print("\n✅ All packages installed!")
    return True

def test_pyspice():
    """Test PySpice with Ngspice"""
    print("\n🔧 Testing PySpice + Ngspice...")
    
    try:
        from PySpice.Spice.Netlist import Circuit
        
        # Create a simple circuit
        circuit = Circuit('Test_Circuit')
        circuit.V('input', 'n1', circuit.gnd, 10 @ u_V)
        circuit.R(1, 'n1', circuit.gnd, 1 @ u_kOhm)
        
        print("  ✅ Circuit created successfully")
        
        # Try to create simulator (this tests Ngspice)
        simulator = circuit.simulator()
        print("  ✅ Simulator created successfully")
        
        # Try transient analysis
        analysis = simulator.transient(step_time=0.1 @ u_ms, end_time=1 @ u_ms)
        print("  ✅ Transient analysis completed")
        
        print(f"  📊 Analysis has {len(analysis.time)} time points")
        
        print("\n✅ PySpice + Ngspice working correctly!")
        return True
        
    except ImportError as e:
        print(f"  ❌ PySpice import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Ngspice test failed: {e}")
        print(f"\n💡 Make sure Ngspice is installed and in your PATH")
        print(f"   Windows: Download from https://ngspice.sourceforge.io/downloads.html")
        print(f"   Mac: brew install ngspice")
        print(f"   Linux: sudo apt install ngspice")
        return False

def test_circuit_builder():
    """Test CircuitBuilder class"""
    print("\n🛠️  Testing CircuitBuilder...")
    
    try:
        from circuit_builder import CircuitBuilder
        
        builder = CircuitBuilder()
        print("  ✅ CircuitBuilder imported")
        
        # Test resistor circuit
        circuit = builder.create_simple_resistor_circuit()
        print(f"  ✅ Resistor circuit created: {circuit}")
        
        print("\n✅ CircuitBuilder working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ CircuitBuilder test failed: {e}")
        return False

def test_llm_orchestrator():
    """Test LLM Orchestrator"""
    print("\n🤖 Testing LLM Orchestrator...")
    
    try:
        from llm_orchestrator import LLMOrchestrator
        import os
        
        orchestrator = LLMOrchestrator()
        print("  ✅ LLMOrchestrator imported")
        
        # Check for API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"  ✅ OpenAI API key configured")
        else:
            print(f"  ⚠️  No OpenAI API key (using fallback templates)")
        
        # Test fallback mode
        response = orchestrator.process_request("Create a simple RC circuit")
        if response and "```python" in response:
            print("  ✅ Fallback mode working")
        else:
            print("  ❌ Fallback mode failed")
            return False
        
        print("\n✅ LLM Orchestrator working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ LLM Orchestrator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 LLM-Powered Circuit Simulator - Setup Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "PySpice": test_pyspice(),
        "CircuitBuilder": test_circuit_builder(),
        "LLMOrchestrator": test_llm_orchestrator()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! Run 'streamlit run app.py' to start the app")
    else:
        print("❌ Some tests failed. Fix issues before running the app")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)