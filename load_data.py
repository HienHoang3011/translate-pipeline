from datasets import load_dataset
import json
import os

# Tạo thư mục nếu chưa có
os.makedirs("data", exist_ok=True)

# Load riêng tập bạn cần
dataset = load_dataset("cais/mmlu", "professional_psychology")

# MMLU thường dùng split "test"
data = dataset["test"].to_list()

# Filter dữ liệu:
# Loại bỏ item có duplicate choices (2 choice giống nhau trong cùng 1 item)
filtered_data = []

for item in data:
    question = item.get("question", "")
    answer_idx = item.get("answer", -1)
    choices = item.get("choices", [])
    
    # Validate data
    if not question or answer_idx < 0 or answer_idx >= len(choices):
        continue
    
    # Check for duplicate choices within this item
    if len(choices) != len(set(choices)):
        print(f"[SKIPPED] Duplicate choices in item: {question[:50]}...")
        continue
    
    filtered_data.append(item)

print(f"Original items: {len(data)}")
print(f"Filtered items: {len(filtered_data)}")

# Dump thành JSON format (không phải JSONL)
with open("data/professional_psychology_final.json", 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)