# Translate Pipeline

Dự án này cung cấp một workflow (sử dụng LangGraph) để biên dịch nội dung của một file JSON tự động. Script sẽ quét toàn bộ dữ liệu cấu trúc (object, array) trong file JSON, tiến hành dịch tất cả các đoạn văn bản (text API values) và bỏ qua việc biên dịch nếu khoá (key) của text đó là "role".

## Cách chạy chương trình

Bạn có thể chạy dự án thông qua Terminal / Command Prompt bằng lệnh sau:

```bash
python main.py --input_file <đường-dẫn-file-input> --output_name <đường-dẫn-file-output>
```

### Tham số truyền vào (Arguments):
- `--input_file`: Đường dẫn đến file JSON đầu vào chứa dữ liệu cần dịch. (Bắt buộc).
- `--output_name`: Tên hoặc đường dẫn của file JSON đầu ra tương ứng sau khi chương trình dịch xong. (Bắt buộc).

### Ví dụ thao tác chạy mẫu:
Nếu bạn có một file tên là `data.json` và muốn lưu kết quả đầu ra thành `result.json`, bạn gõ lệnh như sau:

```bash
python main.py --input_file data.json --output_name result.json
```

### Lưu ý:
- Script đảm bảo giữ nguyên cấu trúc (schema) chuẩn xác giữa file `input_file` và `output_name`, chỉ là các phần nội dung text đã được chuyển ngữ.
- Cần activate môi trường ảo (virtual environment) và cài đặt đầy đủ các thư viện (`LangGraph`, v.v.) trong `requirements.txt` / `pyproject.toml` trước khi tiến hành chạy lệnh.
