"""
Utility module for counting tokens in text using tiktoken or simple heuristics.
"""

def count_tokens_simple(text: str) -> int:
    """
    Simple token count using word splitting as a heuristic.
    Approximates tokens by counting words (split by whitespace).
    On average, 1 token ≈ 0.75 words for English.
    This is a rough estimate; for exact counts use tiktoken with model tokenizer.
    """
    if not text:
        return 0
    words = text.split()
    # Rough approximation: 1 token ≈ 0.75 words
    return max(1, len(words))


def count_tokens_by_model(text: str, tokenizer) -> int:
    """
    Count tokens using an actual model tokenizer.
    """
    if not text:
        return 0
    tokens = tokenizer.encode(text)
    return len(tokens)


def combined_token_count(question: str, answer: str, tokenizer=None) -> int:
    """
    Count combined tokens for question + answer.
    """
    combined_text = f"{question} {answer}"
    if tokenizer:
        return count_tokens_by_model(combined_text, tokenizer)
    else:
        return count_tokens_simple(combined_text)
