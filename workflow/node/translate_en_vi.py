import torch
from workflow.graph.stage import TranslationState
from workflow.prompt import en_to_vi_prompt
from workflow.utils.model_loader import get_model_and_tokenizer

def translate_en_vi_node(state: TranslationState) -> TranslationState:
    """
    LangGraph node chuyên thực hiện việc dịch văn bản từ Tiếng Anh sang Tiếng Việt.
    Node này tuỳ chỉnh temperature = 0.7.
    """
    input_text = state["input_text"]
    
    # Lấy model instance dùng chung
    model, tokenizer = get_model_and_tokenizer()
    is_batch = state.get("is_batch", False)
    batch_delimiter = state.get("batch_delimiter", " ||| ")

    # Dùng prompt chuyên Anh -> Việt
    messages = en_to_vi_prompt.format_messages(text=input_text)
    
    # Chuyển đổi format messages
    hf_messages = []
    for msg in messages:
        role = "system" if msg.type == "system" else "user" if msg.type == "human" else msg.type
        hf_messages.append({"role": role, "content": msg.content})

    # Áp dụng format chat chuẩn của model
    prompt_text = tokenizer.apply_chat_template(
        hf_messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([prompt_text], return_tensors="pt").to(model.device)

    prompt_length = model_inputs.input_ids.shape[1]

    # Cấu hình generation cho node này (temp = 0.7, trả ra 3 bản dịch)
    n_translations = 3
    with torch.no_grad():
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2048,
            temperature=0.7,
            do_sample=True,
            num_return_sequences=n_translations
        )
    
    # Loại bỏ phần prompt đầu vào, chỉ lấy các token mới sinh ra cho cả 3 sequence
    generated_ids = generated_ids[:, prompt_length:]

    translated_texts = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

    return {
        "translated_texts": translated_texts,
        "is_batch": is_batch,
        "batch_delimiter": batch_delimiter
    }
