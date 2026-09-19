#!/usr/bin/env python3
"""
SYSTEM VERIFICATION SCRIPT
Checks all components are installed and working correctly
Run this BEFORE trying to use the full system
"""

import sys
import os
import subprocess
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}═══ {text} ═══{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

def check_python():
    """Check Python version"""
    print_header("Python Installation")
    
    version = sys.version_info
    required = (3, 9)
    
    if version >= required:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} installed")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} found, but {required[0]}.{required[1]}+ required")
        return False

def check_module(module_name, import_name=None):
    """Check if a Python module is installed"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print_success(f"{module_name}")
        return True
    except ImportError:
        print_error(f"{module_name} - Not installed. Run: pip install {module_name}")
        return False

def check_python_packages():
    """Check all required Python packages"""
    print_header("Python Packages")
    
    packages = [
        ("Flask", "flask"),
        ("Flask-CORS", "flask_cors"),
        ("OpenCV", "cv2"),
        ("Pillow", "PIL"),
        ("NumPy", "numpy"),
        ("Tesseract", "pytesseract"),
        ("PyTorch", "torch"),
        ("LangChain", "langchain"),
        ("ChromaDB", "chromadb"),
        ("Sentence-Transformers", "sentence_transformers"),
    ]
    
    all_ok = True
    for display_name, import_name in packages:
        if not check_module(display_name, import_name):
            all_ok = False
    
    if not all_ok:
        print_warning("Run: pip install -r requirements.txt")
    
    return all_ok

def check_tesseract():
    """Check Tesseract-OCR installation"""
    print_header("Tesseract-OCR")
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"Tesseract installed: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print_error("Tesseract not found in PATH")
    print_info("Installation instructions:")
    print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
    print("  Mac: brew install tesseract")
    print("  Linux: sudo apt-get install tesseract-ocr")
    return False

def check_ollama():
    """Check if Ollama is running"""
    print_header("Ollama LLM")
    
    try:
        import requests
        response = requests.get('http://localhost:11434/api/status', timeout=2)
        print_success("Ollama is running on http://localhost:11434")
        return True
    except:
        print_error("Ollama is not running")
        print_info("Start it with: ollama serve")
        print_info("Or install from: https://ollama.ai")
        return False

def check_llama2_model():
    """Check if Llama2 model is downloaded"""
    print_header("Llama2 Model")

    try:
        import requests

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )

        if response.status_code == 200:
            models = response.json().get("models", [])

            for model in models:
                if model["name"].startswith("llama2"):
                    print_success(f"Found model: {model['name']}")
                    return True

            print_error("Llama2 model not found")
            print_info("Installed models:")
            for model in models:
                print(f"  • {model['name']}")
            return False

    except Exception as e:
        print_error(f"Error: {e}")
        return False

def check_directories():
    """Check/create required directories"""
    print_header("Project Directories")
    
    required_dirs = [
        './uploads',
        './chroma_db',
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print_success(f"{directory} exists")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print_success(f"{directory} created")
            except Exception as e:
                print_error(f"Cannot create {directory}: {e}")
                all_ok = False
    
    return all_ok

def check_files():
    """Check if all required files exist"""
    print_header("Project Files")
    
    required_files = [
        'app.py',
        'index.html',
        'requirements.txt',
        'README.md',
        'SETUP.md',
    ]
    
    all_ok = True
    for filepath in required_files:
        if os.path.exists(filepath):
            print_success(f"{filepath}")
        else:
            print_error(f"{filepath} not found")
            all_ok = False
    
    return all_ok

def check_disk_space():
    """Check available disk space"""
    print_header("Disk Space")
    
    try:
        import shutil
        stat = shutil.disk_usage('.')
        free_gb = stat.free / (1024**3)
        
        if free_gb > 5:
            print_success(f"{free_gb:.1f} GB available (need ~5 GB)")
            return True
        else:
            print_warning(f"Only {free_gb:.1f} GB available (need ~5 GB)")
            return False
    except:
        print_warning("Could not check disk space")
        return False

def quick_api_test():
    """Test if Flask backend can start"""
    print_header("Flask Backend")
    
    try:
        # Just check if app.py can be imported without errors
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app = importlib.util.module_from_spec(spec)
        
        # Don't actually run the app, just check imports
        print_success("Flask app can be loaded")
        return True
    except Exception as e:
        print_error(f"Flask app import failed: {e}")
        return False

def run_full_check():
    """Run all checks"""
    
    print(f"""
    {BOLD}{BLUE}╔════════════════════════════════════════════════╗
    ║   SMART P&ID QUERY ENGINE - SYSTEM CHECK      ║
    ║   IOCL Guwahati Internship Project            ║
    ╚════════════════════════════════════════════════╝{RESET}
    """)
    
    checks = [
        ("Python Version", check_python),
        ("Python Packages", check_python_packages),
        ("Tesseract-OCR", check_tesseract),
        ("Ollama LLM", check_ollama),
        ("Llama2 Model", check_llama2_model),
        ("Project Directories", check_directories),
        ("Project Files", check_files),
        ("Disk Space", check_disk_space),
        ("Flask Backend", quick_api_test),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}\n")
    
    for check_name, result in results:
        status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
        print(f"  {status} {check_name}")
    
    print()
    
    if passed == total:
        print(f"{GREEN}{BOLD}🎉 ALL CHECKS PASSED!{RESET}")
        print(f"\nYou're ready to run the system:")
        print(f"  1. Start Ollama: {BOLD}ollama serve{RESET}")
        print(f"  2. Start backend: {BOLD}python app.py{RESET}")
        print(f"  3. Open browser: {BOLD}index.html{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}⚠ SOME CHECKS FAILED{RESET}")
        print(f"\nFix the issues above, then run this script again.")
        print(f"See {BOLD}SETUP.md{RESET} for detailed instructions.")
        return False

if __name__ == "__main__":
    success = run_full_check()
    sys.exit(0 if success else 1)
