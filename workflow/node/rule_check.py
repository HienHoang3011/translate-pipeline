import re
from workflow.graph.stage import TranslationState

def check_length_ratio_rule(source_text: str, target_text: str) -> bool:
    """
    Kiểm tra độ cân xứng số lượng từ giữa bản gốc và bản dịch.
    Tiếng Việt (các âm tiết rời) thường dài hơn tiếng Anh khoảng 1.1x - 1.4x tính theo khoảng trắng.
    Vì vậy, tỉ lệ an toàn cho phép là từ 1/3 đến 3. Khoảng dịch này bao phủ hầu hết các trường hợp dịch thuật thực tế.
    Điều này cho phép chênh lệch tối đa 3 lần giữa bản gốc và bản dịch.
    """
    source_words_count = len(source_text.split())
    target_words_count = len(target_text.split())
    
    if source_words_count == 0:
        return target_words_count == 0
        
    ratio = target_words_count / source_words_count
    return (1/3) <= ratio <= 3  # Cho phép chênh lệch tối đa 3 lần

def check_choices_count_rule(source_text: str, target_text: str) -> bool:
    """
    Kiểm tra số lượng choices trong bản dịch có bằng bản gốc không.
    Tìm các dòng bắt đầu bằng "Choice " và đếm số lượng.
    """
    # Đếm số lượng "Choice N:" trong source
    source_choices = re.findall(r'Choice\s+\d+:', source_text, re.IGNORECASE)
    target_choices = re.findall(r'Choice\s+\d+:', target_text, re.IGNORECASE)
    
    source_count = len(source_choices)
    target_count = len(target_choices)
    
    return source_count == target_count

def rule_check_node(state: TranslationState) -> TranslationState:
    """
    Node Rule-Based kiểm tra các quy tắc cứng.
    - Kiểm tra số lượng choices (phải bằng bản gốc)
    - Kiểm tra cân xứng độ dài từ (Length Ratio): không chênh nhau quá 3 lần
    
    Cách hoạt động:
    - BATCH: So cả chuỗi merged (không tách item)
    - SINGLE: So chuỗi bình thường
    """
    original_text = state["input_text"]
    translated_texts = state.get("translated_texts", [])
    
    valid_translations = []
    
    for vi_text in translated_texts:
        # Rule 1: Kiểm tra số lượng choices
        if not check_choices_count_rule(original_text, vi_text):
            original_count = len(re.findall(r'Choice\s+\d+:', original_text, re.IGNORECASE))
            translated_count = len(re.findall(r'Choice\s+\d+:', vi_text, re.IGNORECASE))
            print(f"[REJECTED by Rule]: Choices count mismatch! Original: {original_count}, Translated: {translated_count}\nOriginal: {original_text[:100]}...\nTranslated: {vi_text[:100]}...")
            continue
        
        # Rule 2: Kiểm tra chênh lệch độ dài từ (Length Ratio)
        if not check_length_ratio_rule(original_text, vi_text):
            print(f"[REJECTED by Rule]: Length ratio exceeds 3x difference!\nOriginal: {original_text[:100]}...\nTranslated: {vi_text[:100]}...")
            continue
        
        # Passed all rules
        valid_translations.append(vi_text)
        
    return {"translated_texts": valid_translations}
