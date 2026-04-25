from workflow.graph.stage import TranslationState
from workflow.prompt import en_to_vi_prompt
from workflow.utils import model_loader
from workflow.utils.model_loader import get_openai_client

def translate_en_vi_node(state: TranslationState) -> TranslationState:
    """
    LangGraph node dịch từ Tiếng Anh sang Tiếng Việt qua vLLM API.
    Sinh ra 3 bản dịch với temperature = 0.7.
    """
    input_text = state["input_text"]
    client = get_openai_client()
    
    is_batch = state.get("is_batch", False)
    batch_delimiter = state.get("batch_delimiter", " ||| ")

    # Prepare messages using the prompt template
    messages = en_to_vi_prompt.format_messages(text=input_text)
    
    # Convert to OpenAI format
    openai_messages = []
    for msg in messages:
        role = "system" if msg.type == "system" else "user" if msg.type == "human" else msg.type
        openai_messages.append({"role": role, "content": msg.content})

    # Generate 3 translation variants
    n_translations = 3
    translated_texts = []
    
    for _ in range(n_translations):
        response = client.chat.completions.create(
            model=model_loader.MODEL_ID,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.95
        )
        
        translated_text = response.choices[0].message.content.strip()
        translated_texts.append(translated_text)

    return {
        "translated_texts": translated_texts,
        "is_batch": is_batch,
        "batch_delimiter": batch_delimiter
    }
