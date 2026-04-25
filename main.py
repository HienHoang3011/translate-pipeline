import argparse
import json
import os
from workflow.graph.builder import build_translation_workflow
from workflow.utils.model_loader import set_model_id, DEFAULT_MODEL_ID

BATCH_DELIMITER = " ||| "

def translate_text(text, app):
    """
    Helper function to translate a single text.
    """
    if not text:
        return text
    
    initial_state = {
        "input_text": text,
        "source_lang": "en",
        "target_lang": "vi",
        "is_batch": False,
        "batch_delimiter": BATCH_DELIMITER
    }
    final_state = app.invoke(initial_state)
    final_translation = final_state.get("final_translation")
    
    return final_translation if final_translation else text

def translate_qa_item(item, app):
    """
    Translate question and choices in-place. Keep structure intact.
    Only translate text fields: "question" and "choices"
    Other fields like "answer", "subject" remain unchanged.
    Format: Question: {question}
            Choice 1: {choice1}
            Choice 2: {choice2}
            ...
    """
    question = item.get("question", "")
    answer_idx = item.get("answer", 0)
    choices = item.get("choices", [])
    
    if not question or answer_idx < 0 or answer_idx >= len(choices):
        return item
    
    # Format: Question: ... followed by Choice labels
    qa_lines = [f"Question: {question}"]
    for i, choice in enumerate(choices, 1):
        qa_lines.append(f"Choice {i}: {choice}")
    
    merged_text = "\n".join(qa_lines)
    print(f"\n--- INPUT TEXT ---\n{merged_text}\n")
    
    merged_translation = translate_text(merged_text, app)
    
    if not merged_translation:
        print("Loi dich, giu nguyen ban goc do Rule Checker bao loi")
        return item
    
    print(f"--- FULL OUTPUT TRANSLATION ---\n{merged_translation}\n")
    
    # Parse kết quả - preserve delimiters "Question:" và "Choice N:"
    question_translated = ""
    choices_translated = []
    
    lines = merged_translation.split("\n")
    for line in lines:
        if line.startswith("Question:"):
            question_translated = line.replace("Question:", "").strip()
        elif line.startswith("Choice"):
            # Format: "Choice N: text"
            choice_text = line.split(":", 1)[-1].strip()
            if choice_text:
                choices_translated.append(choice_text)
    
    print(f"--- PARSED QUESTION ---\n{question_translated}\n")
    print(f"--- PARSED CHOICES ({len(choices_translated)} items) ---")
    for i, c in enumerate(choices_translated):
        print(f"  {i}: {c}")
    print()
    
    # Replace fields in original item, keep structure
    item["question"] = question_translated if question_translated else question
    item["choices"] = choices_translated if choices_translated else choices
    
    return item

def process_data(data, app, skip_fields=None):
    if skip_fields is None:
        skip_fields = []
    
    if isinstance(data, dict):
        new_data = {}
        for k, v in data.items():
            if k in skip_fields:
                new_data[k] = v
            else:
                new_data[k] = process_data(v, app, skip_fields)
        return new_data
    elif isinstance(data, list):
        # Check nếu list chứa toàn strings - batch translate
        if data and all(isinstance(item, str) for item in data):
            print(f"\n--- Dang batch dich {len(data)} items ---")
            merged_text = BATCH_DELIMITER.join(data)
            
            initial_state = {
                "input_text": merged_text,
                "source_lang": "en",
                "target_lang": "vi",
                "is_batch": True,
                "batch_delimiter": BATCH_DELIMITER
            }
            final_state = app.invoke(initial_state)
            final_translation = final_state.get("final_translation")
            
            if final_translation:
                # Split result back to list
                translated_items = [item.strip() for item in final_translation.split(BATCH_DELIMITER)]
                translated_items = [item for item in translated_items if item]  # Remove empty
                print(f"Ket qua batch ({len(translated_items)} items)")
                return translated_items if translated_items else data
            else:
                print("Loi batch dich, giu nguyen ban goc")
                return data
        else:
            # Nested list hoặc mixed types - xử lý item riêng lẻ
            result = []
            for item in data:
                # Nếu là dict với structure question/answer, dịch và lưu vào translations
                if isinstance(item, dict) and "question" in item and "answer" in item and "choices" in item:
                    translated_item = translate_qa_item(item, app)
                    result.append(translated_item)
                else:
                    # Không phải structure question/answer, xử lý bình thường
                    result.append(process_data(item, app, skip_fields))
            return result
    elif isinstance(data, str):
        # Single string - translate individually
        print(f"\n--- Dang dich: {data[:100]}... ---")
        initial_state = {
            "input_text": data,
            "source_lang": "en",
            "target_lang": "vi",
            "is_batch": False,
            "batch_delimiter": BATCH_DELIMITER
        }
        final_state = app.invoke(initial_state)
        final_translation = final_state.get("final_translation")
        
        if final_translation:
            print(f"Ket qua: {final_translation[:100]}...")
            return final_translation
        else:
            print("Loi dich, giu nguyen ban goc do Rule Checker bao loi")
            return data
    else:
        return data

def main():
    parser = argparse.ArgumentParser(description="Chay translation pipeline cho file JSON.")
    parser.add_argument("--input_file", type=str, required=True, help="Duong dan den file JSON dau vao")
    parser.add_argument("--output_name", type=str, required=True, help="Duong dan den file JSON dau ra")
    parser.add_argument("--skip_fields", type=str, default="", help="Danh sach cac truong bo qua dich, cach nhau bang dau phay (vd: role,id,timestamp)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL_ID, help=f"Model ID de tai (default: {DEFAULT_MODEL_ID})")
    
    args = parser.parse_args()
    
    # Set model ID neu duoc chi dinh
    if args.model != DEFAULT_MODEL_ID:
        print(f"Using custom model: {args.model}")
        set_model_id(args.model)
    else:
        print(f"Using default model: {DEFAULT_MODEL_ID}")
    
    if not os.path.exists(args.input_file):
        print(f"Loi: Khong tim thay file '{args.input_file}'.")
        return
        
    with open(args.input_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Loi: '{args.input_file}' khong phai la file JSON hop le.")
            return

    # Xu ly danh sach skip_fields
    skip_fields = [field.strip() for field in args.skip_fields.split(',') if field.strip()]
    if skip_fields:
        print(f"Cac truong bo qua dich: {', '.join(skip_fields)}")

    print("Khoi tao Workflow LangGraph...")
    app = build_translation_workflow()
    
    print(f"Bat dau xu ly file '{args.input_file}' -> '{args.output_name}'...")
    translated_data = process_data(data, app, skip_fields)
    
    with open(args.output_name, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
    print(f"Hoan thanh! Da luu ket qua tai '{args.output_name}'")

if __name__ == "__main__":
    main()
