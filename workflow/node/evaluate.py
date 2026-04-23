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
    
    Node này chỉ chấm điểm và chọn variant tốt nhất (rule_check đã lọc trước).
    """
    original_text = state["input_text"]
    translated_texts = state.get("translated_texts", [])
    back_translated_texts = state.get("back_translated_texts", [])
    is_batch = state.get("is_batch", False)
    batch_delimiter = state.get("batch_delimiter", " ||| ")
    
    bge_model = get_bge_model()
    chencherry = SmoothingFunction()
    
    # Single reference tokens cho cả merged text
    reference_tokens = [original_text.lower().split()]

    scored_variants = []
    
    for vi_text, back_en_text in zip(translated_texts, back_translated_texts):
        # Cosine similarity
        orig_emb = bge_model.encode(original_text, convert_to_tensor=True)
        back_emb = bge_model.encode(back_en_text, convert_to_tensor=True)
        cosine_score = util.cos_sim(orig_emb, back_emb).item()
        
        # BLEU score
        candidate_tokens = back_en_text.lower().split()
        bleu_score = sentence_bleu(
            reference_tokens, 
            candidate_tokens, 
            smoothing_function=chencherry.method1
        )
        
        # Final score
        final_score = 0.8 * cosine_score + 0.2 * bleu_score
        
        scored_variants.append({
            "vi_text": vi_text,
            "back_translated_text": back_en_text,
            "cosine_score": cosine_score,
            "bleu_score": bleu_score,
            "final_score": final_score
        })
        
    # Sort các bản dịch theo điểm (final_score giảm dần)
    scored_variants = sorted(scored_variants, key=lambda x: x["final_score"], reverse=True)
    
    final_translation = scored_variants[0]["vi_text"] if scored_variants else None
    
    return {
        "scored_variants": scored_variants,
        "final_translation": final_translation,
        "is_batch": is_batch,
        "batch_delimiter": batch_delimiter
    }
