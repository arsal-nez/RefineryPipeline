# ⚙️ ADVANCED CONFIGURATION GUIDE

## 🎯 OPTIMIZE FOR YOUR USE CASE

### 1. CHOOSE YOUR LLM MODEL

Different models have different speeds and quality:

#### Available Models (all free):

```bash
# LLAMA2 (Default - Balanced)
ollama pull llama2
# Speed: Medium | Quality: Good | Memory: 7GB | Best for: General Q&A

# MISTRAL (Better reasoning)
ollama pull mistral
# Speed: Medium | Quality: Better | Memory: 7GB | Best for: Complex technical

# NEURAL-CHAT (Fast Q&A)
ollama pull neural-chat
# Speed: Fast | Quality: Good | Memory: 5GB | Best for: Quick answers

# OPENCHAT (Fastest)
ollama pull openchat
# Speed: Very Fast | Quality: Good | Memory: 3.5GB | Best for: Real-time chat

# ORCA-MINI (Smallest)
ollama pull orca-mini
# Speed: Very Fast | Quality: Fair | Memory: 2GB | Best for: Low-power systems
```

#### How to Use:

Edit `app.py` line 40:
```python
# Current
OLLAMA_MODEL = "llama2"

# Change to any model above
OLLAMA_MODEL = "mistral"
```

Then pull the model:
```bash
ollama pull mistral
```

### 2. ADJUST CHUNK SIZE FOR QUALITY vs SPEED

Smaller chunks = faster but less context
Larger chunks = slower but more comprehensive

Edit `app.py` line ~475:

```python
# Fast (good for real-time, loses some context)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30
)

# Balanced (current)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Comprehensive (slow but very accurate)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
```

### 3. RETRIEVAL SEARCH DEPTH

Number of document chunks to consider:

Edit `app.py` line ~390:

```python
# Fast (3 chunks)
retriever=vectorstore.as_retriever(search_kwargs={"k": 3})

# Balanced (current)
retriever=vectorstore.as_retriever(search_kwargs={"k": 3})

# Thorough (slower, better results)
retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
```

### 4. ENABLE GPU ACCELERATION

If you have NVIDIA GPU:

```bash
# Remove CPU-only PyTorch
pip uninstall torch -y

# Install CUDA-enabled version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

### 5. INCREASE CONCURRENT REQUESTS

Edit `app.py` line 556:

```python
# Current (debug mode, single-threaded)
app.run(debug=True, host='0.0.0.0', port=5000)

# Production (multi-threaded, handles multiple uploads)
app.run(
    debug=False,
    host='0.0.0.0',
    port=5000,
    threaded=True,
    processes=4  # Number of worker processes
)
```

---

## 🔐 SECURITY HARDENING

### 1. REMOVE DEBUG MODE

Edit `app.py` line 556:

```python
# Before (development)
app.run(debug=True, ...)

# After (production)
app.run(debug=False, ...)
```

### 2. ADD AUTHENTICATION

Create `auth.py`:

```python
from functools import wraps
from flask import request, jsonify

VALID_TOKENS = ["your_secret_token_here"]

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in VALID_TOKENS:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated
```

Then in `app.py`:

```python
from auth import require_auth

@app.route('/chat', methods=['POST'])
@require_auth
def chat():
    # ... existing code
```

### 3. LIMIT FILE UPLOAD SIZE

Edit `app.py` line ~20:

```python
# Max 50MB per upload
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
```

### 4. SANITIZE FILE UPLOADS

Edit `app.py` upload endpoints:

```python
import secure  # pip install secure

filename = secure.filename(file.filename)
```

### 5. ADD RATE LIMITING

```bash
pip install Flask-Limiter
```

In `app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")  # Max 10 requests/minute
def chat():
    # ...
```

---

## 📊 PERFORMANCE TUNING

### 1. CACHING RESULTS

Add caching for repetitive queries:

```bash
pip install flask-caching
```

In `app.py`:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/search-tag', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def search_tag():
    # ...
```

### 2. DATABASE OPTIMIZATION

```python
# Batch add documents instead of one-by-one
docs = []
for doc_path in document_paths:
    with open(doc_path) as f:
        docs.append(f.read())

# Add all at once (faster)
vectorstore.add_texts(docs)
```

### 3. IMAGE OPTIMIZATION FOR OCR

Preprocess before sending to Tesseract:

```python
# In BlueprintProcessor.load_image()
image = cv2.imread(image_path)

# Resize to optimal size
if image.shape[0] > 3000:
    image = cv2.resize(image, 
                       (int(image.shape[1]*0.5), 
                        int(image.shape[0]*0.5)))

# Enhance contrast
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
image = clahe.apply(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
```

---

## 🌐 DEPLOYMENT OPTIONS

### Option 1: DOCKER CONTAINER

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:

```bash
docker build -t smart-pid .
docker run -p 5000:5000 smart-pid
```

### Option 2: HEROKU DEPLOYMENT

1. Create `Procfile`:
```
web: python app.py
```

2. Create `runtime.txt`:
```
python-3.10.0
```

3. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Option 3: AWS EC2

1. Launch Ubuntu EC2 instance
2. SSH in
3. Run setup script:
```bash
curl -fsSL https://your-setup-script.sh | bash
```

---

## 📈 MONITORING & LOGGING

### Add Structured Logging

Edit `app.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Monitor Performance

```python
import time

start = time.time()
# Your operation
duration = time.time() - start
app.logger.info(f"OCR took {duration:.2f}s")
```

---

## 🚀 PRODUCTION CHECKLIST

- [ ] Set `debug=False`
- [ ] Remove demo SOP setup
- [ ] Add authentication tokens
- [ ] Set rate limits
- [ ] Enable logging
- [ ] Test with real P&ID images
- [ ] Test with large manuals (>10MB)
- [ ] Set up error monitoring
- [ ] Document API endpoints
- [ ] Create backup strategy
- [ ] Test database recovery
- [ ] Setup SSL/HTTPS
- [ ] Plan for scaling

---

## 🔧 MAINTENANCE TASKS

### Weekly:
- Check disk space: `df -h`
- Monitor vector DB size: `du -sh chroma_db/`
- Review logs for errors

### Monthly:
- Rebuild vector DB if degraded
- Update models: `ollama pull llama2`
- Optimize database

### Quarterly:
- Security audit
- Performance review
- Backup documentation

---

## 🎯 NEXT LEVEL: FINE-TUNING

Create custom LLM trained on IOCL documents:

```bash
# Create dataset of Q&A pairs
python create_training_data.py

# Fine-tune (requires GPU)
python finetune_llm.py

# Use custom model
OLLAMA_MODEL = "custom-iocl-llm"
```

---

## 📚 RESOURCES

- **Flask Production:** https://flask.palletsprojects.com/deployment/
- **ChromaDB Optimization:** https://docs.trychroma.com/
- **LangChain Advanced:** https://python.langchain.com/docs/modules/
- **Docker:** https://docs.docker.com/
- **Ollama Models:** https://ollama.ai/library

---

**You've mastered the system! 🎓**
