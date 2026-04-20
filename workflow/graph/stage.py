from typing import TypedDict, Optional

class VariantScore(TypedDict):
    """
    Representation of the score for a translation variant.
    """
    vi_text: str
    back_translated_text: str
    cosine_score: float
    bleu_score: float
    final_score: float

class TranslationState(TypedDict):
    """
    Representation of the state passed between nodes in the translation graph.
    """
    input_text: str
    source_lang: str
    target_lang: str
    translated_texts: list[str]
    back_translated_texts: list[str]
    scored_variants: list[VariantScore]
    final_translation: Optional[str]
