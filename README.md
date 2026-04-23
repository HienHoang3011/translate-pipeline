# Translate Pipeline

Dự án này cung cấp một workflow (sử dụng LangGraph) để biên dịch nội dung của một file JSON tự động. Script sẽ quét toàn bộ dữ liệu cấu trúc (object, array) trong file JSON, tiến hành dịch tất cả các đoạn văn bản (text API values) và bỏ qua việc biên dịch nếu khoá (key) của text đó là "role".

## Kiến trúc Pipeline

```
Input Text / List Items
    ↓
translate_en_vi (Dịch EN→VI, 3 variants)
    ↓
rule_check (Kiểm tra numbers consistency, length ratio)
    ↓
translate_vi_en (Back-translate VI→EN)
    ↓
evaluate (Cosine similarity + BLEU score, chọn variant tốt nhất)
    ↓
Output Text / List Items
```

## Cách chạy chương trình

### Dùng model mặc định (Qwen/Qwen3-30B-A3B-Instruct-2507):

```bash
python main.py --input_file data.json --output_name result.json
```

### Dùng model custom:

```bash
python main.py --input_file data.json --output_name result.json --model "your-model-name"
```

Ví dụ với model khác:
```bash
python main.py --input_file data.json --output_name result.json --model "Mistral/Mistral-7B-Instruct-v0.1"
```

### Bỏ qua dịch một số trường:

```bash
python main.py --input_file data.json --output_name result.json --skip_fields role,id,timestamp
```

### Kết hợp tất cả options:

```bash
python main.py --input_file data.json --output_name result.json --model "your-model" --skip_fields role,id
```

### Tham số truyền vào (Arguments):
- `--input_file`: Đường dẫn đến file JSON đầu vào chứa dữ liệu cần dịch. **(Bắt buộc)**
- `--output_name`: Tên hoặc đường dẫn của file JSON đầu ra tương ứng sau khi chương trình dịch xong. **(Bắt buộc)**
- `--model`: Model ID để tải (default: `Qwen/Qwen3-30B-A3B-Instruct-2507`). **(Tùy chọn)**
- `--skip_fields`: Danh sách các trường bỏ qua việc dịch, cách nhau bằng dấu phẩy. **(Tùy chọn)**

## Xử lý dữ liệu

- **Text field**: Dịch từng text riêng lẻ
- **List of strings**: Gộp items với delimiter ` ||| `, dịch cùng lúc, sau đó tách kết quả

Ví dụ:
```json
{
  "id": 1,
  "question": "What is photosynthesis?",
  "options": ["A process", "Energy from sun", "Plant food"]
}
```

Output:
```json
{
  "id": 1,
  "question": "Quá trình quang hợp là gì?",
  "options": ["Một quá trình", "Năng lượng từ mặt trời", "Thức ăn cho thực vật"]
}
```

## Lưu ý:
- Script đảm bảo giữ nguyên cấu trúc (schema) chính xác giữa file input và output, chỉ các phần nội dung text đã được dịch.
- Cần activate môi trường ảo (virtual environment) và cài đặt đầy đủ các thư viện (`LangGraph`, `torch`, v.v.) trong `pyproject.toml` trước khi chạy.
