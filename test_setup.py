#!/usr/bin/env python3
"""
Quick test script to verify the ECPC-IDS Dashboard setup
Run this to ensure all dependencies and modules are properly installed
"""

import sys
import importlib

def test_imports():
    """Test that all required modules can be imported"""
    required_modules = {
        'gradio': 'Gradio UI Framework',
        'numpy': 'NumPy for numerical arrays',
        'PIL': 'PIL for image processing',
        'requests': 'HTTP library for API calls'
    }
    
    print("=" * 60)
    print("Testing ECPC-IDS Dashboard Dependencies")
    print("=" * 60)
    
    all_ok = True
    for module_name, description in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name:15} {description}")
        except ImportError as e:
            print(f"✗ {module_name:15} NOT FOUND - {e}")
            all_ok = False
    
    print("\n" + "=" * 60)
    print("Testing Local Modules")
    print("=" * 60)
    
    local_modules = {
        'config': 'Application configuration',
        'utils.helpers': 'Helper utilities',
        'components.ui_components': 'UI component functions',
        'services.api_client': 'Backend API client'
    }
    
    for module_name, description in local_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name:25} {description}")
        except ImportError as e:
            print(f"✗ {module_name:25} NOT FOUND - {e}")
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✓ All dependencies OK! Ready to run:")
        print("  python app.py")
        return 0
    else:
        print("✗ Some dependencies are missing. Run:")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
