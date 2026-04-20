import torch
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sentence_transformers import util
from workflow.graph.stage import TranslationState
from workflow.utils.model_loader import get_bge_model

def evaluate_node(state: TranslationState) -> TranslationState:
    """
    Node đánh giá chất lượng bằng cách so sánh văn bản tiếng Anh gốc với văn bản dịch ngược.
    Cách chấm:
    - Tính Cosine Similarity bằng mô hình BAAI/bge-m3.
    - Tính BLEU score dùng NLTK.
    - Điểm cuối cùng = 0.8 * Cosine + 0.2 * BLEU.
    """
    original_text = state["input_text"]
    translated_texts = state.get("translated_texts", [])
    back_translated_texts = state.get("back_translated_texts", [])
    
    bge_model = get_bge_model()
    
    # 1. Prepare vectors for Cosine Similarity
    orig_emb = bge_model.encode(original_text, convert_to_tensor=True)
    
    # 2. Prepare tokens and smoothing for BLEU score
    chencherry = SmoothingFunction()
    # Phân tách văn bản gốc thành các tokens cho BLEU tham chiếu
    reference_tokens = [original_text.lower().split()]

    scored_variants = []
    
    for vi_text, back_en_text in zip(translated_texts, back_translated_texts):
        # Cosine similarity
        back_emb = bge_model.encode(back_en_text, convert_to_tensor=True)
        # util.cos_sim trả về ma trận 2D, gọi .item() để lấy giá trị float
        cosine_score = util.cos_sim(orig_emb, back_emb).item()
        
        # BLEU score
        candidate_tokens = back_en_text.lower().split()
        bleu_score = sentence_bleu(
            reference_tokens, 
            candidate_tokens, 
            smoothing_function=chencherry.method1
        )
        
        # Tính Final score
        final_score = 0.8 * cosine_score + 0.2 * bleu_score
        
        scored_variants.append({
            "vi_text": vi_text,
            "back_translated_text": back_en_text,
            "cosine_score": cosine_score,
            "bleu_score": bleu_score,
            "final_score": final_score
        })
        
    # Sort các bản dịch theo điểm (final_score giảm dần - điểm cao nhất lên đầu)
    scored_variants = sorted(scored_variants, key=lambda x: x["final_score"], reverse=True)
    
    # Bản được duyệt làm kết quả cuối cùng phải là bản có điểm cao nhất (đầu mảng)
    # Lưu ý: Sẽ trả về None nếu toàn bộ các bản dịch đều bị loại ở Rule Check Node
    final_translation = scored_variants[0]["vi_text"] if scored_variants else None
    
    return {
        "scored_variants": scored_variants,
        "final_translation": final_translation
    }
