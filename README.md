# Translate Pipeline

Dự án này cung cấp một workflow (sử dụng LangGraph) để biên dịch nội dung của một file JSON tự động. Script sẽ quét toàn bộ dữ liệu cấu trúc (object, array) trong file JSON, tiến hành dịch tất cả các đoạn văn bản (text API values) và bỏ qua việc biên dịch nếu khoá (key) của text đó là "role".

## Kiến trúc Pipeline

```
Input Text / List Items
    ↓
translate_en_vi (Dịch EN→VI, 3 variants qua vLLM API)
    ↓
rule_check (Kiểm tra numbers consistency, length ratio, choices count)
    ↓
translate_vi_en (Back-translate VI→EN qua vLLM API)
    ↓
evaluate (Cosine similarity + BLEU score, chọn variant tốt nhất)
    ↓
Output Text / List Items
```

## Công nghệ sử dụng

- **LangGraph**: Workflow orchestration framework
- **vLLM**: Local model inference server (OpenAI API compatible)
- **Gemma-4-E4B**: Default translation model
- **BAAI/bge-m3**: Semantic embedding model
- **OpenAI Python SDK**: API client để gọi vLLM server

## Cách chạy chương trình

### Setup vLLM (Bước đầu, chỉ chạy 1 lần):

```bash
python setup_vllm.py
```

Điều này sẽ cài đặt:
- vLLM (nightly build)
- Transformers
- PyTorch (torch)
- Accelerate
- OpenAI Python SDK

### Khởi động vLLM Server (Terminal 1):

```bash
python start_vllm.py
```

Server sẽ bắt đầu tại `http://localhost:5000/v1` với model mặc định `google/gemma-4-e4b-it`

### Chạy Pipeline (Terminal 2):

```bash
# Dùng model mặc định:
python main.py --input_file data.json --output_name result.json
```

### Dùng model custom:

```bash
python main.py --input_file data.json --output_name result.json --model "google/gemma-2-9b-it"
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
- `--model`: Model ID để tải (default: `google/gemma-4-e4b-it`). **(Tùy chọn)**
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

---

## Implementation Details (vLLM Integration)

### Thay đổi chính

#### 1. Model Loading System (workflow/utils/model_loader.py)
**Trước**: Direct model loading với Transformers + PyTorch  
**Sau**: OpenAI client kết nối tới vLLM server

```python
# Cũ:
from transformers import AutoModelForCausalLM, AutoTokenizer
_model, _tokenizer = get_model_and_tokenizer()

# Mới:
from openai import OpenAI
_client = get_openai_client()
_client.chat.completions.create(...)
```

#### 2. Các Node Dịch Được Cập Nhật

**translate_en_vi.py**:
- Dùng `get_openai_client()` thay vì `get_model_and_tokenizer()`
- Gọi `client.chat.completions.create()` với temperature=0.7
- Sinh 3 variants trong vòng lặp

**translate_vi_en.py**:
- Dùng `get_openai_client()` thay vì `get_model_and_tokenizer()`
- Gọi `client.chat.completions.create()` với temperature=0.1
- Back-translate từng variant để scoring


### API Compatibility

vLLM cung cấp OpenAI API compatibility tại:
```
POST http://localhost:5000/v1/chat/completions
```

Điều này có nghĩa OpenAI SDK tương tự hoạt động cho cả vLLM và OpenAI services.
