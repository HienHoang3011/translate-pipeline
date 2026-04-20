import torch
from workflow.graph.stage import TranslationState
from workflow.prompt import vi_to_en_prompt
from workflow.utils.model_loader import get_model_and_tokenizer

def translate_vi_en_node(state: TranslationState) -> TranslationState:
    """
    LangGraph node chuyên thực hiện việc dịch ngược văn bản từ Tiếng Việt sang Tiếng Anh.
    Node này tuỳ chỉnh temperature = 0.1 và nhận đầu vào từ mảng kết quả của node trước (translated_texts).
    """
    translated_texts = state.get("translated_texts", [])
    
    # Lấy model instance dùng chung
    model, tokenizer = get_model_and_tokenizer()

    back_translated_texts = []

    # Xử lý dịch ngược cho TỪNG bản dịch tiếng Việt
    for vi_text in translated_texts:
        messages = vi_to_en_prompt.format_messages(text=vi_text)
        
        hf_messages = []
        for msg in messages:
            role = "system" if msg.type == "system" else "user" if msg.type == "human" else msg.type
            hf_messages.append({"role": role, "content": msg.content})

        prompt_text = tokenizer.apply_chat_template(
            hf_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = tokenizer([prompt_text], return_tensors="pt").to(model.device)
        prompt_length = model_inputs.input_ids.shape[1]

        # Ở đây temperature = 0.1 và chỉ generate 1 bản duy nhất cho 1 đầu vào
        with torch.no_grad():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=2048,
                temperature=0.1,
                do_sample=True,
                num_return_sequences=1
            )
        
        generated_ids = generated_ids[:, prompt_length:]
        en_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        back_translated_texts.append(en_text)

    return {"back_translated_texts": back_translated_texts}
