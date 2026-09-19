#!/usr/bin/env python3
"""
SMART P&ID QUERY ENGINE
Enterprise-Grade: Multimodal Vision + GraphRAG System
Production Version for IOCL Guwahati Internship
"""

import os
import io
import json
import base64
import re
import logging
import requests
import networkx as nx 
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

# Flask & API
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# Computer Vision
import cv2
cv2.setNumThreads(6)  
import numpy as np
import pytesseract
from PIL import Image

# NLP & RAG
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

def _detect_tesseract() -> str:
    """Auto-detect Tesseract path across platforms."""
    import shutil
    # Linux / Mac: tesseract is usually on PATH
    if shutil.which("tesseract"):
        return shutil.which("tesseract")
    # Windows default install location
    win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(win_path):
        return win_path
    return "tesseract"  # last resort: hope it's on PATH

@dataclass
class Config:
    # Set DEBUG=true in your shell for development; never True in production
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    HOST: str = os.environ.get("HOST", "127.0.0.1")  # safer default than 0.0.0.0
    PORT: int = int(os.environ.get("PORT", "5000"))
    OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_TEXT_MODEL: str = os.environ.get("OLLAMA_TEXT_MODEL", "llama2")
    OLLAMA_VISION_MODEL: str = os.environ.get("OLLAMA_VISION_MODEL", "llava-phi3")
    DB_PATH: str = os.environ.get("DB_PATH", "./chroma_db")
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "./uploads")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    TESSERACT_PATH: str = os.environ.get("TESSERACT_PATH", _detect_tesseract())
        CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("P&ID_Engine")
    logger.setLevel(getattr(logging, log_level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    fh = logging.FileHandler('pid_engine.log', encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = setup_logging()
config = Config()
pytesseract.pytesseract.pytesseract_cmd = config.TESSERACT_PATH

# ============================================================================
# OCR TARGETS
# ============================================================================
INDUSTRIAL_TAGS: Dict[str, str] = {
    "pump": r'\bP[_-]?\d{3,4}\b|\bPMP[_-]?\d{3,4}\b',
    "valve": r'\bV[_-]?\d{3,4}\b|\bVLV[_-]?\d{3,4}\b',
    "motor": r'\bM[_-]?\d{3,4}\b|\bMTR[_-]?\d{3,4}\b',
    "sensor": r'\bSEN[_-]?\d{3,4}\b',
    "controller": r'\bCTL[_-]?\d{3,4}\b',
    "vessel": r'\bT[_-]?\d{3,4}\b|\bVSL[_-]?\d{3,4}\b',
    "heat_exchanger": r'\bHX[_-]?\d{3,4}\b|\bHEX[_-]?\d{3,4}\b',
    "process_unit": r'(?i)\b(distillation|hydrotreating|reforming|cracking|coking|fcc|isomerization|asphalt)\b',
    "fluid": r'(?i)\b(crude oil|naphtha|gasoline|diesel|lpg|hydrogen)\b'
}

# ============================================================================
# GRAPH DATABASE (Pathfinder Logic)
# ============================================================================
class PIDKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        logger.info("Knowledge Graph initialized")

    def load_topology(self, data: Dict[str, Any]):
        self.graph.clear()
        for node_id, attrs in data.get("equipment_nodes", {}).items():
            self.graph.add_node(node_id.upper(), **attrs)
        
        for edge in data.get("pipeline_connections", []):
            self.graph.add_edge(edge["source"].upper(), edge["destination"].upper(), medium=edge.get("medium", "Unknown Fluid"))
        
        logger.info(f"Loaded {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} connections into Graph.")

    def trace_connections(self, tag_ids: List[str]) -> str:
        if not tag_ids:
            return "No specific equipment tag identified in your query."
            
        context_blocks = []
        for tag_id in tag_ids:
            tag_id = tag_id.upper()
            if tag_id not in self.graph:
                continue

            upstream = list(self.graph.predecessors(tag_id))
            downstream = list(self.graph.successors(tag_id))
            node_data = self.graph.nodes[tag_id]

            context = f"- EQUIPMENT TARGET: {tag_id} ({node_data.get('type', 'Unknown Component')})\n"
            
            if upstream:
                sources = ", ".join([f"[{u}] via {self.graph[u][tag_id].get('medium')}" for u in upstream])
                context += f"  > RECEIVES INLET FROM: {sources}\n"
            else:
                context += "  > RECEIVES INLET FROM: Process Start / Unmapped\n"
                
            if downstream:
                dests = ", ".join([f"[{d}] via {self.graph[tag_id][d].get('medium')}" for d in downstream])
                context += f"  > DISCHARGES OUTLET TO: {dests}\n"
            else:
                context += "  > DISCHARGES OUTLET TO: Process End / Unmapped\n"
            
            context_blocks.append(context)
            
        return "\n".join(context_blocks) if context_blocks else "Topology data not mapped for these items."

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
app = Flask(__name__)

cors_origins = [
    origin.strip()
    for origin in config.CORS_ORIGINS.split(",")
    if origin.strip()
]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": cors_origins
        }
    }
)

os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.DB_PATH, exist_ok=True)

logger.info("======================================================================")
logger.info("SMART MULTIMODAL P&ID ENGINE - STARTING UP")
logger.info("======================================================================")

# ============================================================================
# PHASE 1: COMPUTER VISION - BLUEPRINT PROCESSOR
# ============================================================================

@dataclass
class EquipmentTag:
    id: str; type: str; x: int; y: int; width: int; height: int; confidence: int

class BlueprintProcessor:
    def __init__(self):
        self.image = None
        self.tags = []
    
    def _preprocess_for_ocr(self, bgr_image: np.ndarray):
        """
        Image preprocessing pipeline to improve OCR accuracy on
        low-contrast, dark, or noisy P&ID blueprints.

        Returns: (processed_image, scale_factor)
        scale_factor is how much the image was enlarged — callers must
        DIVIDE all OCR bounding-box coordinates by this value to map
        them back onto the original image.

        Pipeline:
          1. Convert to grayscale (Tesseract works best on single channel)
          2. Upscale if too small (Tesseract needs ~300 DPI minimum)
          3. CLAHE contrast enhancement (local contrast boost)
          4. Gaussian blur to remove sensor/compression noise
          5. Adaptive thresholding — clean black/white, handles uneven lighting
        """
        gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # Track the upscale factor so callers can reverse-map coordinates
        scale = 1.0
        h, w = gray.shape
        if w < 1500:
            scale = 1500 / w
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            logger.info(f"Image upscaled by {scale:.2f}x for OCR (coords will be divided by {scale:.2f})")

        # CLAHE: adaptive contrast boost
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Denoise
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Adaptive threshold — produces clean black text on white background
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=15,
            C=8
        )
        return binary, scale

    def process(self, image_path: str) -> Dict[str, Any]:
        try:
            self.image = cv2.imread(image_path)
            if self.image is None:
                return {'success': False, 'error': f'Could not read image file: {image_path}'}

            # Preprocess and capture scale factor used during upscaling
            processed, ocr_scale = self._preprocess_for_ocr(self.image)

            # Run OCR on the preprocessed (grayscale binary) image
            # --psm 6: single uniform block  --oem 3: LSTM engine
            data = pytesseract.image_to_data(
                processed,
                output_type=pytesseract.Output.DICT,
                config='--psm 6 --oem 3'
            )
            
            extracted = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                conf = int(data['conf'][i])
                # Filter out empty strings, single chars, and very low-confidence results
                if text and len(text) > 1 and conf > 30:
                    # BUGFIX: Tesseract coords are in the UPSCALED image space.
                    # Divide by ocr_scale to convert back to original image coords.
                    extracted.append({
                        'text': text,
                        'x': int(data['left'][i]   / ocr_scale),
                        'y': int(data['top'][i]    / ocr_scale),
                        'w': int(data['width'][i]  / ocr_scale),
                        'h': int(data['height'][i] / ocr_scale),
                        'conf': conf
                    })
            
            self.tags = []
            seen_ids = set()  # deduplicate tags with same ID
            for block in extracted:
                text = block['text'].upper()
                for eq_type, pattern in INDUSTRIAL_TAGS.items():
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if match not in seen_ids:
                            seen_ids.add(match)
                            self.tags.append(EquipmentTag(
                                id=match, type=eq_type,
                                x=block['x'], y=block['y'],
                                width=block['w'], height=block['h'],
                                confidence=block['conf']
                            ))
            
            # Annotate on the ORIGINAL (colour) image — coords are now correct
            annotated = self.image.copy()
            for tag in self.tags:
                cv2.rectangle(
                    annotated,
                    (tag.x, tag.y),
                    (tag.x + tag.width, tag.y + tag.height),
                    (0, 255, 0), 2
                )
                cv2.putText(
                    annotated, tag.id,
                    (tag.x, max(tag.y - 5, 10)),  # clamp so text doesn't go off top edge
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
                )
            
            _, buffer = cv2.imencode('.png', annotated)
            return {
                'success': True,
                'tags': [asdict(t) for t in self.tags],
                'annotated_image': base64.b64encode(buffer).decode(),
                'total_equipment': len(self.tags)
            }
        except Exception as e:
            logger.error(f"ERROR: Blueprint processing failed: {e}")
            return {'success': False, 'error': str(e)}

# ============================================================================
# PHASE 2: HYBRID GRAPHRAG + VISION SYSTEM
# ============================================================================

class RAGSystem:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(base_url=config.OLLAMA_BASE_URL, model="nomic-embed-text")
        self.vectorstore = Chroma(persist_directory=config.DB_PATH, embedding_function=self.embeddings)
        self.llm = Ollama(base_url=config.OLLAMA_BASE_URL, model=config.OLLAMA_TEXT_MODEL, temperature=0.2)
    
    def add_documents(self, document_paths: List[str]) -> int:
        all_documents = []
        for doc_path in document_paths:
            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
            chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_text(content)
            all_documents.extend([{'content': c, 'source': Path(doc_path).name} for c in chunks])
        if all_documents:
            self.vectorstore.add_texts([d['content'] for d in all_documents], [{'source': d['source']} for d in all_documents])
            self.vectorstore.persist()
        return len(all_documents)
    
    # FIX 3: Detect casual / non-technical messages so they don't get routed
    # through the heavy refinery prompt pipeline.
    _CASUAL_PATTERNS = re.compile(
        r'^(hi|hello|hey|howdy|thanks|thank you|bye|goodbye|ok|okay|cool|great|yes|no|'  
        r'what can you do|help|who are you|what are you|good morning|good evening|'  
        r'good afternoon|nice|awesome|perfect|got it|understood|sure|alright)[\.!\?]?$',
        re.IGNORECASE
    )

    def _is_casual(self, question: str) -> bool:
        """Return True if the question is a casual greeting or filler phrase."""
        return bool(self._CASUAL_PATTERNS.match(question.strip()))

    def _stream_ollama(self, payload: dict) -> str:
        """
        FIX 1: Stream tokens from Ollama and yield them as SSE (Server-Sent Events).
        This replaces stream=False so the user sees words appear in real time
        instead of waiting for the entire response.
        """
        full_response = ""
        with requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={**payload, "stream": True},
            stream=True,
            timeout=120
        ) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    full_response += token
                    yield token
                    if chunk.get("done", False):
                        break
        return full_response

    def query(self, question: str, topology_data: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        try:
            # FIX 3: Short-circuit casual messages with a lightweight conversational prompt
            if self._is_casual(question):
                logger.info(f"Casual message detected: '{question}' — using conversational path")
                casual_prompt = (
                    f"You are a helpful AI assistant for an industrial refinery P&ID system. "
                    f"The user said: '{question}'. "
                    f"Reply naturally and briefly. If it's a greeting, greet back and mention you can "
                    f"help them query P&ID blueprints, equipment specs, and pipeline connections."
                )
                answer = self.llm.invoke(casual_prompt)
                return {'success': True, 'answer': answer.strip(), 'sources': []}

            docs = self.vectorstore.as_retriever(search_kwargs={"k": 3}).invoke(question)
            context = "\n\n---\n\n".join([doc.page_content for doc in docs]) if docs else "No text manuals found."
            sources = list(set([doc.metadata.get('source', 'unknown') for doc in docs])) if docs else []
            
            prompt = f"""You are an advanced industrial refinery AI. You are looking at a blueprint image, but YOU MUST TRUST THE TOPOLOGY MAP for all pipeline connections.
Do not attempt to trace lines visually. Use the TOPOLOGY MAP to answer questions about flow and connections. Use the DOCUMENTATION for safety rules.
If the answer is not explicitly in the TOPOLOGY MAP or DOCUMENTATION, reply: INSUFFICIENT DATA TO ANSWER SAFELY.
Answer in full, complete sentences.

[TOPOLOGY MAP (Absolute Factual Trace)]:
{topology_data}

[DOCUMENTATION (Text Manuals)]:
{context}

QUESTION: {question}
ANSWER:"""
            
            if image_path and os.path.exists(image_path):
                logger.info(f"Sending Image + Graph Context to Vision Model ({config.OLLAMA_VISION_MODEL})...")
                with Image.open(image_path) as img:
                    if img.mode in ('RGBA', 'P', 'LA'): img = img.convert('RGB')
                    img.thumbnail((800, 800))
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG", quality=85)
                    image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                # Vision model: stream=True not yet universally supported for images;
                # keep stream=False here but with a reasonable timeout.
                payload = {"model": config.OLLAMA_VISION_MODEL, "prompt": prompt, "stream": False, "images": [image_b64]}
                response = requests.post(f"{config.OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
                
                if response.status_code == 200:
                    answer = response.json().get("response", "")
                    logger.info("Vision Model successfully responded.")
                else:
                    answer = f"Vision Error: {response.text}"
                return {'success': True, 'answer': answer.strip(), 'sources': sources}
            else:
                # FIX 1: Text model uses streaming — return a generator
                logger.info("Streaming response from text model...")
                payload = {"model": config.OLLAMA_TEXT_MODEL, "prompt": prompt}
                return {
                    'success': True,
                    'answer': self._stream_ollama(payload),  # generator
                    'sources': sources,
                    'streaming': True
                }

        except Exception as e:
            logger.error(f"ERROR: Query failed: {e}")
            return {'success': False, 'answer': f'Query Error: {str(e)}', 'sources': []}

# ============================================================================
# API ENDPOINTS
# ============================================================================

blueprint_proc = BlueprintProcessor()
rag_system = RAGSystem()
knowledge_graph = PIDKnowledgeGraph() 

@app.route('/api/health', methods=['GET'])
def health_check():
    """Return live status of all system components."""
    # Check Ollama connectivity
    ollama_ok = False
    try:
        r = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        pass

    # Check ChromaDB doc count
    try:
        doc_count = rag_system.vectorstore._collection.count()
    except Exception:
        doc_count = 0

    return jsonify({
        'status': 'online',
        'version': '2.0.0 (Multimodal GraphRAG)',
        'components': {
            'ollama': 'connected' if ollama_ok else 'unreachable',
            'chromadb': f'{doc_count} chunks indexed',
            'knowledge_graph': f'{knowledge_graph.graph.number_of_nodes()} nodes, '
                               f'{knowledge_graph.graph.number_of_edges()} edges',
            'blueprint': 'loaded' if getattr(app, 'blueprint_data', None) else 'not loaded'
        }
    })

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Return the current knowledge graph topology as JSON.
    Useful for visualising the P&ID equipment network externally."""
    nodes = [
        {"id": n, **knowledge_graph.graph.nodes[n]}
        for n in knowledge_graph.graph.nodes
    ]
    edges = [
        {"source": u, "destination": v, **knowledge_graph.graph[u][v]}
        for u, v in knowledge_graph.graph.edges
    ]
    return jsonify({
        "node_count": knowledge_graph.graph.number_of_nodes(),
        "edge_count": knowledge_graph.graph.number_of_edges(),
        "nodes": nodes,
        "edges": edges
    })

@app.route('/api/upload-blueprint', methods=['POST'])
def upload_blueprint():
    file = request.files.get('file')
    if not file or file.filename == '': return jsonify({'success': False, 'error': 'No file'}), 400
    temp_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
    file.save(temp_path)
    result = blueprint_proc.process(temp_path)
    if result['success']: app.blueprint_data = {'path': temp_path, 'tags': result['tags']}
    return jsonify(result)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'success': False, 'error': 'Empty question'}), 400
    
    image_path = None
    mentioned_tag = None
    topology_data = "No specific equipment tag identified in your query."
    
    blueprint_data = getattr(app, 'blueprint_data', None)
    if blueprint_data:
        image_path = blueprint_data.get('path')
        detected_tags = blueprint_data.get('tags', [])
        
        if any(word in question.lower() for word in ['each', 'all', 'everything']):
            tag_ids = [t['id'] for t in detected_tags]
            topology_data = knowledge_graph.trace_connections(tag_ids)
            if detected_tags: mentioned_tag = detected_tags[0] 
        else:
            for tag in detected_tags:
                if tag['id'].lower() in question.lower():
                    mentioned_tag = tag
                    topology_data = knowledge_graph.trace_connections([tag['id']])
                    break
                
    rag_response = rag_system.query(question, topology_data=topology_data, image_path=image_path)

    # FIX 1: If the RAG system returned a streaming generator, send it as SSE
    if rag_response.get('streaming'):
        sources = rag_response['sources']

        def generate():
            # First event: metadata (sources + equipment location)
            meta = json.dumps({
                'type': 'meta',
                'sources': sources,
                'equipment_location': mentioned_tag
            })
            yield f"data: {meta}\n\n"

            # Stream tokens
            for token in rag_response['answer']:
                payload = json.dumps({'type': 'token', 'token': token})
                yield f"data: {payload}\n\n"

            # Final done signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'   # Disable Nginx buffering if behind proxy
            }
        )

    # Non-streaming path (vision model or casual responses)
    return jsonify({
        'success': rag_response['success'],
        'question': question,
        'answer': rag_response['answer'],
        'sources': rag_response['sources'],
        'equipment_location': mentioned_tag
    })

@app.route('/api/demo-setup', methods=['GET'])
def demo_setup():
    logger.info("DEMO: Loading Graph Topology and Manuals")
    
    graph_data = {
        "equipment_nodes": {
            "VLV-104": {"type": "Safety Pressure Relief Valve"},
            "P-201": {"type": "Crude Oil Transfer Pump"},
            "HX-211": {"type": "Main Heat Exchanger"},
            "FCC": {"type": "Fluid Catalytic Cracker"},
            "REFORMING": {"type": "Catalytic Reformer"},
            "ASPHALT": {"type": "Asphalt Blow Unit"},
            "DISTILLATION": {"type": "Atmospheric Distillation"}
        },
        "pipeline_connections": [
            {"source": "Feed Tank", "destination": "P-201", "medium": "Crude Oil"},
            {"source": "P-201", "destination": "HX-211", "medium": "Crude Oil"},
            {"source": "DISTILLATION", "destination": "FCC", "medium": "Gas Oil"},
            {"source": "FCC", "destination": "REFORMING", "medium": "Naphtha"},
            {"source": "Vacuum Residuum", "destination": "ASPHALT", "medium": "Heavy Residuum"}
        ]
    }
    knowledge_graph.load_topology(graph_data)
    
    demo_sop = """
STANDARD OPERATING PROCEDURES - INDUSTRIAL REFINERY UNIT
----------------------------------------------------
FCC (FLUID CATALYTIC CRACKER): Converts heavy gas oils into lighter, more valuable products like gasoline.
REFORMING (CATALYTIC REFORMER): Restructures naphtha molecules to increase octane rating.
ASPHALT (ASPHALT BLOW UNIT): Processes heavy vacuum residuum into commercial asphalt.
----------------------------------------------------
"""
    demo_path = os.path.join(config.UPLOAD_FOLDER, 'demo_sop.txt')
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(demo_sop)
    
    count = rag_system.add_documents([demo_path])
    return jsonify({'success': True, 'message': 'Graph Topology loaded', 'chunks': count})

if __name__ == '__main__':
    print("**********************************************************************")
    print("SMART P&ID QUERY ENGINE (MULTIMODAL: LLaVA-Phi3 + GraphRAG)")
    print("**********************************************************************")
    app.blueprint_data = None
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
