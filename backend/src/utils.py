def to_kebab_case(text: str) -> str:
    return "-".join([word.strip() for word in text.strip().lower().split()])
