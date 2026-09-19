# ⚡ QUICK START - 5 MINUTE SETUP

## 📋 CHECKLIST BEFORE STARTING

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Tesseract installed (see SETUP.md for your OS)
- [ ] Ollama installed and **running in background**
- [ ] 5GB free disk space

---

## 🚀 START HERE

### STEP 1: Open Terminal/PowerShell

```bash
cd smart-pid-engine
```

### STEP 2: Create & Activate Virtual Environment

**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### STEP 3: Install Python Packages

```bash
pip install -r requirements.txt
```

⏳ **This takes 2-3 minutes** (downloading torch is normal and slow)

### STEP 4: Start Ollama (In New Terminal Tab)

**Keep this running in background:**

```bash
ollama serve
```

Or on Windows, just launch the Ollama app.

Wait until you see: `Ollama is running on http://localhost:11434`

### STEP 5: Start Backend (Main Terminal)

```bash
python app.py
```

You should see:
```
╔═══════════════════════════════════════════════════════╗
║   SMART P&ID QUERY ENGINE - Production Server        ║
║   Built for IOCL Guwahati                             ║
╚═══════════════════════════════════════════════════════╝

🔧 Backend running on http://localhost:5000
```

### STEP 6: Open Frontend (Browser)

Simply open `index.html` in your web browser:
- Windows: Double-click `index.html`
- Mac: Right-click → Open with → Browser
- Linux: `firefox index.html` or `chromium index.html`

### STEP 7: Test the System

1. **In the web app**, click "📤 Upload Blueprint"
2. You should see demo SOP loaded automatically
3. Ask a question: *"What is VLV-104?"*
4. Click "Send"

---

## ✅ IF EVERYTHING WORKED

You'll see:
- ✓ Status bar shows "Backend Connected"
- ✓ Chat says "Demo SOP loaded with X knowledge chunks"
- ✓ You can type questions and get answers

---

## ❌ TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'cv2'"
**Fix:** Did you activate venv?
```bash
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### Error: "Tesseract not found"
**Fix:** Check SETUP.md - it's OS-specific. You probably need to add it to PATH or modify app.py line 47.

### Error: "Connection refused" when uploading image
**Fix:** Backend not running. Make sure `python app.py` is executing.

### Error: "Ollama connection failed"
**Fix:** Ollama isn't running. Start it separately:
```bash
ollama serve
```

### Error: "llama2 model not found"
**Fix:** Download it once:
```bash
ollama pull llama2
```
(This is ~4GB, one-time only)

### Frontend shows "Initializing..." forever
**Fix:** 
1. Check browser console (F12 → Console tab)
2. If "CORS error", make sure backend is running
3. Reload page

---

## 📚 ONCE IT'S WORKING: NEXT STEPS

### Add Real Manuals

Instead of demo SOP, add actual PDF manuals:

1. **Convert PDF to text** (or just use .txt files)
   - Mac/Linux: `pdftotext manual.pdf manual.txt`
   - Windows: Use online converter or copy-paste text

2. **Create a `manuals` folder:**
   ```bash
   mkdir manuals
   cp manual1.txt manuals/
   cp manual2.txt manuals/
   ```

3. **Upload via API** or modify `app.py` line ~430 to load them automatically

### Add Real P&ID Images

Just upload PNG/JPG images of actual piping diagrams. System will:
- ✓ Extract all equipment tags
- ✓ Store their locations
- ✓ Highlight them when you ask about them

---

## 🎯 EXAMPLE QUESTIONS TO TRY

After uploading demo:

- "What is the maximum operating pressure of VLV-104?"
- "Tell me about PMP-201"
- "What safety procedures apply to MTR-301?"
- "What is the maintenance interval for VLV-104?"

---

## 📊 PROJECT STRUCTURE

```
smart-pid-engine/
├── app.py                 # Backend Flask server
├── index.html             # Frontend UI
├── requirements.txt       # Python dependencies
├── SETUP.md              # OS-specific setup
├── QUICKSTART.md         # This file
├── uploads/              # Uploaded files (auto-created)
└── chroma_db/            # Vector database (auto-created)
```

---

## 🔐 IMPORTANT FOR IOCL INTERNSHIP

### Before Deploying to Production:

1. **Security:** 
   - Change `debug=True` to `False` in app.py line 556
   - Add authentication if needed

2. **Performance:**
   - Use better LLM model (change `OLLAMA_MODEL`)
   - Increase chunk size for faster queries

3. **Documentation:**
   - Keep this README.md
   - Document any customizations
   - Screenshot of working demo

---

## 📞 SUPPORT

If stuck:
1. Check the error message carefully
2. Google the exact error
3. Consult SETUP.md for your OS
4. Check that all services are running (Ollama, Flask)

---

**You've got this! 🚀**
