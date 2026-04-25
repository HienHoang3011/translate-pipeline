from workflow.graph.stage import TranslationState
from workflow.prompt import vi_to_en_prompt
from workflow.utils import model_loader
from workflow.utils.model_loader import get_openai_client

def translate_vi_en_node(state: TranslationState) -> TranslationState:
    """
    LangGraph node dịch ngược từ Tiếng Việt sang Tiếng Anh qua vLLM API.
    Temperature = 0.1 (deterministic) để tạo back-translation dùng cho scoring.
    """
    translated_texts = state.get("translated_texts", [])
    is_batch = state.get("is_batch", False)
    batch_delimiter = state.get("batch_delimiter", " ||| ")
    
    client = get_openai_client()
    back_translated_texts = []

    # Back-translate each VI text to EN (1 variant per text)
    for vi_text in translated_texts:
        messages = vi_to_en_prompt.format_messages(text=vi_text)
        
        # Convert to OpenAI format
        openai_messages = []
        for msg in messages:
            role = "system" if msg.type == "system" else "user" if msg.type == "human" else msg.type
            openai_messages.append({"role": role, "content": msg.content})

        # Generate back-translation with low temperature (deterministic)
        response = client.chat.completions.create(
            model=model_loader.MODEL_ID,
            messages=openai_messages,
            temperature=0.1,
            max_tokens=2048,
            top_p=0.95
        )
        
        en_text = response.choices[0].message.content.strip()
        back_translated_texts.append(en_text)

    return {
        "back_translated_texts": back_translated_texts,
        "is_batch": is_batch,
        "batch_delimiter": batch_delimiter
    }
