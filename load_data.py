from datasets import load_dataset
import json
import os
from workflow.utils.token_counter import combined_token_count

# Tạo thư mục nếu chưa có
os.makedirs("data", exist_ok=True)

# Load riêng tập bạn cần
dataset = load_dataset("cais/mmlu", "professional_psychology")

# MMLU thường dùng split "test"
data = dataset["test"].to_list()

# Filter dữ liệu:
# 1. Loại bỏ item có token < 50
# 2. Loại bỏ item có đáp án trùng lặp (deduplication)
filtered_data = []
seen_answers = set()

for item in data:
    question = item.get("question", "")
    answer_idx = item.get("answer", -1)
    choices = item.get("choices", [])
    
    # Validate data
    if not question or answer_idx < 0 or answer_idx >= len(choices):
        continue
    
    answer_text = choices[answer_idx]
    
    # Check token count: question + answer combined must be >= 50
    combined_tokens = combined_token_count(question, answer_text)
    if combined_tokens < 50:
        print(f"[SKIPPED] Token count < 50: {combined_tokens} tokens - {question[:50]}...")
        continue
    
    # Check for duplicate answers
    if answer_text in seen_answers:
        print(f"[SKIPPED] Duplicate answer: {answer_text[:50]}...")
        continue
    
    seen_answers.add(answer_text)
    filtered_data.append(item)

print(f"Original items: {len(data)}")
print(f"Filtered items: {len(filtered_data)}")

# Dump thành JSON format (không phải JSONL)
with open("data/professional_psychology.json", 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)