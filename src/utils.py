import re


def to_camel_case(text: str) -> str:
    """Converts a string to camel case."""
    words = re.split(r"[-_\s]+", text)
    return words[0].lower() + "".join(word.capitalize() for i, word in enumerate(words[1:]))
