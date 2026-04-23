import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer

# Default model
DEFAULT_MODEL_ID = "Qwen/Qwen3-30B-A3B-Instruct-2507"
MODEL_ID = DEFAULT_MODEL_ID

_tokenizer = None
_model = None

def set_model_id(model_id):
    """
    Set model ID before loading. Should be called before get_model_and_tokenizer().
    """
    global MODEL_ID
    MODEL_ID = model_id
    print(f"Model ID set to: {MODEL_ID}")

def reset_model():
    """
    Reset loaded model (for testing or switching models).
    """
    global _tokenizer, _model
    _model = None
    _tokenizer = None

def get_model_and_tokenizer():
    """
    Load model dạng Singleton để có thể tái sử dụng (reuse) trên nhiều Node 
    mà không phải load lại model nhiều lần tốn VRAM.
    """
    global _tokenizer, _model
    
    if _model is None or _tokenizer is None:
        print(f"Loading tokenizer and model {MODEL_ID}...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            device_map="auto",
            torch_dtype="auto" # Tự động nhận dạng datatype (Hỗ trợ tốt quantize model)
        )
        print("Model loaded successfully.")
        
    return _model, _tokenizer

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
