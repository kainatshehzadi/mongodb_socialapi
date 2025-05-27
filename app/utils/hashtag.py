import re

def extract_hashtags(text: str) -> list[str]:
    return re.findall(r"#(\w+)", text)
