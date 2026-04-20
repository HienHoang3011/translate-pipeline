import argparse
import json
import os
from workflow.builder import build_translation_workflow

def process_data(data, app):
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if k == "role":
                new_data[k] = v
            else:
                new_data[k] = process_data(v, app)
        return new_data
    elif isinstance(data, list):
        return [process_data(item, app) for item in data]
    elif isinstance(data, str):
        # Gọi LangGraph để dịch chuỗi
        print(f"\n--- Đang dịch: {data[:100]}... ---")
        initial_state = {
            "input_text": data,
            "source_lang": "en",
            "target_lang": "vi"
        }
        final_state = app.invoke(initial_state)
        final_translation = final_state.get("final_translation")
        
        if final_translation:
            print(f"🌟 Kết quả: {final_translation[:100]}...")
            return final_translation
        else:
            print("❌ Lỗi dịch, giữ nguyên bản gốc do Rule Checker báo lỗi")
            return data
    else:
        return data

def main():
    parser = argparse.ArgumentParser(description="Chạy translation pipeline cho file JSON.")
    parser.add_argument("--input_file", type=str, required=True, help="Đường dẫn đến file JSON đầu vào")
    parser.add_argument("--output_name", type=str, required=True, help="Đường dẫn đến file JSON đầu ra")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Lỗi: Không tìm thấy file '{args.input_file}'.")
        return
        
    with open(args.input_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Lỗi: '{args.input_file}' không phải là file JSON hợp lệ.")
            return

    print("Khởi tạo Workflow LangGraph...")
    app = build_translation_workflow()
    
    print(f"\nBắt đầu xử lý file '{args.input_file}' -> '{args.output_name}'...")
    translated_data = process_data(data, app)
    
    with open(args.output_name, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
    print(f"\nHoàn thành! Đã lưu kết quả tại '{args.output_name}'")

if __name__ == "__main__":
    main()
