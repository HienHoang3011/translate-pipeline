import torch
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# vLLM Configuration
DEFAULT_MODEL_ID = "google/gemma-4-E2B-it"
MODEL_ID = DEFAULT_MODEL_ID
VLLM_API_BASE = "http://localhost:5000/v1"

_client = None
_bge_model = None

def set_model_id(model_id):
    """
    Set model ID before using. Should be called before making translation requests.
    """
    global MODEL_ID
    MODEL_ID = model_id
    print(f"Model ID set to: {MODEL_ID}")

def reset_model():
    """
    Reset OpenAI client (for testing or switching models).
    """
    global _client
    _client = None

def get_openai_client():
    """
    Get OpenAI client connected to local vLLM server (Singleton pattern).
    Reuses same client across multiple nodes without recreating.
    """
    global _client
    
    if _client is None:
        print(f"Connecting to vLLM server at {VLLM_API_BASE}...")
        _client = OpenAI(
            api_key="EMPTY",  # vLLM doesn't require real API key
            base_url=VLLM_API_BASE,
        )
        print("Connected to vLLM server successfully.")
        
    return _client

_bge_model = None

def get_bge_model():
    """
    Load model đánh giá cosine similarity dạng Singleton.
    """
    global _bge_model
    if _bge_model is None:
        print("Loading BAAI/bge-m3 for cosine similarity evaluation...")
        _bge_model = SentenceTransformer("BAAI/bge-m3", device="cuda" if torch.cuda.is_available() else "cpu")
    return _bge_model
