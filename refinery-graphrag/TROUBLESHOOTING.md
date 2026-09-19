# 🔧 TROUBLESHOOTING GUIDE

## 🚀 BEFORE READING THIS: Run Verification

```bash
python verify_system.py
```

This will tell you exactly what's missing.

---

## ❌ COMMON ERRORS & SOLUTIONS

### "ModuleNotFoundError: No module named 'cv2'"

**Cause:** Virtual environment not activated or packages not installed

**Solution:**
```bash
# 1. Check venv is activated (should see "(venv)" in terminal)
# If not:
source venv/bin/activate          # Mac/Linux
# or
venv\Scripts\activate             # Windows

# 2. Install packages
pip install -r requirements.txt

# 3. Verify
python -c "import cv2; print('✓ OpenCV OK')"
```

---

### "tesseract is not installed or it's not in your PATH"

**Cause:** Tesseract-OCR not installed or not in system PATH

**Solution:**

#### Windows:
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (keep default path: `C:\Program Files\Tesseract-OCR`)
3. Open `app.py` line 47 and verify:
   ```python
   pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```
4. Restart Python

#### Mac:
```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Test it:**
```bash
tesseract --version
```

---

### "Connection refused: ('127.0.0.1', 11434)"

**Cause:** Ollama not running

**Solution:**

1. **Install Ollama** (if not already): https://ollama.ai
2. **Start Ollama** in a separate terminal:
   ```bash
   ollama serve
   ```
   You should see: `Ollama is running on http://localhost:11434`

3. **Keep it running** while using the app

4. **Verify:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

### "Error: Model 'llama2' not found"

**Cause:** Llama2 model not downloaded

**Solution:**

1. **Download it** (one-time, ~4GB):
   ```bash
   ollama pull llama2
   ```

2. **Wait for completion** (5-15 minutes depending on internet)

3. **Verify:**
   ```bash
   ollama list
   ```
   Should show: `llama2  latest  ...`

---

### "CORS error in browser console"

**Cause:** Frontend can't reach backend

**Solution:**

1. **Check backend is running:**
   - Terminal should show: `Running on http://0.0.0.0:5000`
   - Try: `curl http://localhost:5000/health`

2. **Check URL in browser console:**
   - Press F12 in browser
   - Go to Console tab
   - Should say: `✓ Backend initialized`

3. **If still failing:**
   - Restart backend: Ctrl+C then `python app.py`
   - Reload browser: Ctrl+Shift+R (hard refresh)

---

### "Port 5000 already in use"

**Cause:** Something else is using port 5000

**Solution:**

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -i :5000
kill -9 <PID>
```

Or change port in `app.py` line 560:
```python
app.run(debug=True, port=8000)  # Use 8000 instead
```

---

### "Permission denied" on Linux/Mac

**Cause:** Need administrator privileges

**Solution:**
```bash
# Mac
sudo chown -R $USER ~/smart-pid-engine

# Linux
sudo chown -R $USER ~/smart-pid-engine
```

---

### "Frontend won't upload images - empty image message"

**Cause:** Image upload API not working

**Solution:**

1. **Check uploads folder exists:**
   ```bash
   ls uploads/
   # or on Windows: dir uploads
   ```

2. **If missing, create it:**
   ```bash
   mkdir uploads
   ```

3. **Check file permissions:**
   ```bash
   chmod 755 uploads/  # Mac/Linux
   ```

4. **Try uploading test image:**
   ```bash
   python create_demo_files.py
   ```
   Then upload `demo_blueprint.png`

---

### "Chat not responding"

**Cause:** LLM taking too long or Ollama disconnected

**Solution:**

1. **Wait longer** - First query takes ~10 seconds
2. **Check Ollama is still running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```
3. **Restart Ollama** if needed:
   - Stop: Ctrl+C
   - Start: `ollama serve`

4. **Try a simpler question:**
   - Current: "What complex thing is VLV-104 and explain its operation?"
   - Try: "What is VLV-104?"

---

### "torch installation fails or hangs"

**Cause:** PyTorch is large (~2GB) and internet is slow

**Solution:**

```bash
# Cancel current install (Ctrl+C)

# Use PyTorch CPU only (faster)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or pre-download wheel file from:
# https://download.pytorch.org/whl/torch/
```

---

### "OCR can't read P&ID text"

**Cause:** Low image quality or text angle

**Solution:**

1. **Preprocess image** - Edit `app.py` line ~135:
   ```python
   # Add before OCR
   image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)[1]
   image = cv2.GaussianBlur(image, (5, 5), 0)
   ```

2. **Try different PSM mode** - Line ~145:
   ```python
   # Current: '--psm 6'
   # Try: '--psm 3'  (auto page layout)
   # Try: '--psm 4'  (assume single column of text)
   ```

3. **Use higher resolution image:**
   - Scan at 300 DPI instead of 72 DPI
   - Or take photo with modern phone camera

---

### "Not finding equipment tags on blueprint"

**Cause:** Tags formatted differently than expected

**Solution:**

Edit `app.py` line ~57 to match your tag format:

```python
# Current patterns:
"pump": r'\bPMP[_-]?\d{3,4}\b',
"valve": r'\bVLV[_-]?\d{3,4}\b',

# Your tags might be:
"pump": r'\bP\d{3,4}\b',         # P201, P202
"valve": r'\bV[A-Z]?\d{3,4}\b',  # V104, V205, VLV104
```

Test regex online: https://regex101.com/

---

### "Vector database stuck or slow"

**Cause:** ChromaDB corrupted or too much data

**Solution:**

```bash
# 1. Remove old database
rm -rf chroma_db/    # Mac/Linux
rmdir /s chroma_db   # Windows

# 2. Restart backend
# It will create a fresh database

# 3. Re-add documents
```

---

### "Out of memory error"

**Cause:** System doesn't have enough RAM

**Solution:**

1. **Use lighter LLM:**
   - Edit `app.py` line 40:
   ```python
   OLLAMA_MODEL = "neural-chat"  # ~7GB vs Llama2 ~9GB
   ```

2. **Reduce chunk size:**
   - Edit `app.py` line ~475:
   ```python
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=300,  # Reduce from 500
       chunk_overlap=30  # Reduce from 50
   )
   ```

3. **Close other applications** using RAM

---

### "Windows: Python not found"

**Cause:** Python not in PATH

**Solution:**

1. **Uninstall and reinstall Python:**
   - Download: https://www.python.org/downloads/
   - ✓ Check "Add Python to PATH" during install

2. **Or add Python manually:**
   - Find Python: `C:\Users\YourName\AppData\Local\Programs\Python\Python310`
   - Add to PATH (Windows Settings → Environment Variables)

3. **Verify:**
   ```bash
   python --version
   ```

---

## 🔍 DEBUGGING DEEPER

### Enable Debug Logging

Edit `app.py` and add to imports:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Then look at terminal output for detailed error messages.

### Check Individual Components

```bash
# Test OpenCV
python -c "import cv2; print('OpenCV:', cv2.__version__)"

# Test Tesseract
python -c "import pytesseract; pytesseract.pytesseract_cmd='tesseract'; print('✓')"

# Test Torch
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# Test ChromaDB
python -c "from langchain.vectorstores import Chroma; print('✓ ChromaDB')"

# Test Ollama connection
curl http://localhost:11434/api/status
```

### Check API Manually

```bash
# Test health check
curl http://localhost:5000/health

# Test with sample image
curl -X POST -F "file=@demo_blueprint.png" \
  http://localhost:5000/upload-blueprint

# Test chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is VLV-104?"}'
```

---

## 🆘 STILL STUCK?

### Collect Information:

Run this and save output:
```bash
python verify_system.py > verification.txt
```

Include:
- Full error message
- What you were doing when it happened
- Output from `verification.txt`

### Next Steps:

1. **Google the exact error message** - often it's a known issue
2. **Check GitHub issues** for similar projects
3. **Ask in Python community forums:**
   - Stack Overflow
   - Reddit r/learnprogramming
   - Python Discord

---

## 📞 IOCL INTERNSHIP SUPPORT

If this is for your IOCL internship:

1. **Contact your internship mentor** with:
   - Error message
   - Verification output
   - What you tried

2. **Escalate to IT** if it's:
   - Network/proxy issues
   - System permissions
   - Disk space (contact storage team)

3. **Document everything** - this makes great portfolio material!

---

**Good luck! You've got this! 🚀**

Remember: Most errors have been solved by someone before. Search first! 🔍
