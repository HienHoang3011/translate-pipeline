from datasets import load_dataset
import json
import os

# Tạo thư mục nếu chưa có
os.makedirs("data", exist_ok=True)

# Load riêng tập bạn cần
dataset = load_dataset("cais/mmlu", "professional_psychology")

# MMLU thường dùng split "test"
data = dataset["test"].to_list()

# Dump thành JSON format (không phải JSONL)
with open("data/professional_psychology.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)