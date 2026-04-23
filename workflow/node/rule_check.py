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
    - Kiểm tra giữ nguyên số liệu (Numbers Consistency)
    - Kiểm tra cân xứng độ dài từ (Length Ratio)
    
    Cách hoạt động:
    - BATCH: So cả chuỗi merged (không tách item)
    - SINGLE: So chuỗi bình thường
    """
    original_text = state["input_text"]
    translated_texts = state.get("translated_texts", [])
    
    valid_translations = []
    
    for vi_text in translated_texts:
        # Rule 1: Kiểm tra Giữ nguyên số liệu (Numbers Consistency)
        if not check_numbers_rule(original_text, vi_text):
            print(f"[REJECTED by Rule]: Numbers mismatch!\nOriginal: {original_text[:100]}...\nTranslated: {vi_text[:100]}...")
            continue
            
        # Rule 2: Kiểm tra chênh lệch độ dài từ (Length Ratio)
        if not check_length_ratio_rule(original_text, vi_text):
            print(f"[REJECTED by Rule]: Length ratio bad!\nOriginal: {original_text[:100]}...\nTranslated: {vi_text[:100]}...")
            continue
        
        # Passed all rules
        valid_translations.append(vi_text)
        
    return {"translated_texts": valid_translations}
