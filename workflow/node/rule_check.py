import re
from workflow.graph.stage import TranslationState

def check_numbers_rule(source_text: str, target_text: str) -> bool:
    """
    Sử dụng regex để lọc ra tất cả các cụm chữ số trong văn bản gốc và bản dịch.
    Trả về True nếu mảng số của cả hai khớp nhau (không phân biệt thứ tự hiển thị).
    """
    # Trích xuất tất cả các số (hỗ trợ số nguyên, số thập phân, số có dấu phẩy)
    # Ví dụ: 100, 3.14, 1,000,000
    pattern = r'\b\d+(?:[\.,]\d+)*\b'
    source_numbers = re.findall(pattern, source_text)
    target_numbers = re.findall(pattern, target_text)
    
    # Chuẩn hoá nếu cần thiết, ví dụ "1,000" thành "1000", nhưng tạm thời so sánh text trực tiếp.
    # Sử dụng sorted() để so sánh mà không phụ thuộc vào vị trí thay đổi do ngữ pháp câu
    return sorted(source_numbers) == sorted(target_numbers)

def check_length_ratio_rule(source_text: str, target_text: str) -> bool:
    """
    Kiểm tra độ cân xứng số lượng từ giữa bản gốc và bản dịch.
    Tiếng Việt (các âm tiết rời) thường dài hơn tiếng Anh khoảng 1.1x - 1.4x tính theo khoảng trắng.
    Vì vậy, tỉ lệ an toàn cho phép là từ 0.5 đến 2.0. Khoảng dịch này bao phủ hầu hết các trường hợp dịch thuật thực tế.
    """
    source_words_count = len(source_text.split())
    target_words_count = len(target_text.split())
    
    if source_words_count == 0:
        return target_words_count == 0
        
    ratio = target_words_count / source_words_count
    return 0.5 <= ratio <= 2.0  # Mở rộng khoảng để tránh loại bỏ quá nhiều bản dịch có thể chấp nhận được

def rule_check_node(state: TranslationState) -> TranslationState:
    """
    Node Rule-Based kiểm tra các quy tắc cứng. 
    Node này nên được đặt ngay sau Node dịch Tiếng Anh -> Tiếng Việt.
    
    Hai chế độ:
    - BATCH: Lọc từng item trong batch (so sánh EN item vs VI item)
    - SINGLE: Lọc cả merged text (so sánh EN text vs VI text)
    """
    original_text = state["input_text"]
    translated_texts = state.get("translated_texts", [])
    is_batch = state.get("is_batch", False)
    batch_delimiter = state.get("batch_delimiter", " ||| ")
    
    valid_translations = []
    
    if not is_batch:
        # ===== SINGLE MODE =====
        for vi_text in translated_texts:
            # Rule 1: Kiểm tra Giữ nguyên số liệu (Numbers Consistency)
            if not check_numbers_rule(original_text, vi_text):
                print(f"[REJECTED by Rule]: Lỗi số liệu không khớp!\n- Gốc: {original_text}\n- Bản dịch: {vi_text}\n---")
                continue
                
            # Rule 2: Kiểm tra chênh lệch độ dài từ (Length Ratio)
            if not check_length_ratio_rule(original_text, vi_text):
                print(f"[REJECTED by Rule]: Mất cân đối độ dài từ!\n- Gốc: {original_text}\n- Bản dịch: {vi_text}\n---")
                continue
            
            # Nếu vượt qua tất cả rules:
            valid_translations.append(vi_text)
    else:
        # ===== BATCH MODE =====
        original_items = [item.strip() for item in original_text.split(batch_delimiter)]
        
        for variant_idx, vi_batch in enumerate(translated_texts):
            vi_items = [item.strip() for item in vi_batch.split(batch_delimiter)]
            
            # Check length match
            if len(vi_items) != len(original_items):
                print(f"[REJECTED V{variant_idx}]: Item count mismatch! EN={len(original_items)}, VI={len(vi_items)}")
                continue
            
            # Lọc từng item trong batch
            valid_items = []
            for orig_en, trans_vi in zip(original_items, vi_items):
                # Rule 1: Numbers Consistency
                if not check_numbers_rule(orig_en, trans_vi):
                    print(f"[REJECTED V{variant_idx}]: Numbers mismatch: {orig_en[:50]}... -> {trans_vi[:50]}...")
                    continue
                
                # Rule 2: Length Ratio
                if not check_length_ratio_rule(orig_en, trans_vi):
                    print(f"[REJECTED V{variant_idx}]: Length ratio bad: {orig_en[:50]}... -> {trans_vi[:50]}...")
                    continue
                
                valid_items.append(trans_vi)
            
            # Giữ variant nếu có ít nhất 1 item valid
            if valid_items:
                valid_batch = batch_delimiter.join(valid_items)
                valid_translations.append(valid_batch)
                print(f"[ACCEPT V{variant_idx}]: {len(valid_items)}/{len(original_items)} items passed")
        
    return {"translated_texts": valid_translations}
