# 🚀 SMART P&ID QUERY ENGINE - SETUP GUIDE
# For IOCL Guwahati Internship Project
# Cost: $0 | Setup Time: 15 minutes

## ⚠️ BEFORE YOU START
# You need:
# 1. Python 3.9+ installed
# 2. ~5GB free disk space
# 3. ~10 minutes of uninterrupted internet

## STEP 1: Install Tesseract (CRITICAL - Different per OS)

### ON WINDOWS:
# 1. Download: https://github.com/UB-Mannheim/tesseract/wiki
# 2. Run installer, choose default path: C:\Program Files\Tesseract-OCR
# 3. Copy this path for later

### ON MACOS:
# Run: brew install tesseract

### ON LINUX (Ubuntu/Debian):
# Run: sudo apt-get install tesseract-ocr

## STEP 2: Verify Tesseract Installation
# Run: tesseract --version

## STEP 3: Create Virtual Environment
# python -m venv venv

## STEP 4: Activate Virtual Environment
### ON WINDOWS:
# venv\Scripts\activate

### ON MAC/LINUX:
# source venv/bin/activate

## STEP 5: Install Python Dependencies
# pip install -r requirements.txt

## STEP 6: Download Ollama (for Local LLM)
# Visit: https://ollama.ai
# Download and install for your OS

## STEP 7: Pull Llama2 Model (One-time, ~4GB download)
# After installing Ollama, open terminal and run:
# ollama pull llama2

## STEP 8: Verify Everything Works
# python
# >>> import cv2; print("✓ OpenCV OK")
# >>> import pytesseract; print("✓ Tesseract OK")
# >>> import torch; print("✓ PyTorch OK")
# >>> exit()

## IF YOU GET ERRORS:
# - Tesseract path wrong? Set in app.py (see below)
# - Torch installation slow? This is normal (~2 minutes)
# - Ollama not starting? Make sure it's running in background

print("✓ Setup complete! Ready to run app.py")
