from slugify import slugify

def slug(text: str) -> str:
    value = slugify(text=text, separator="_")
    if value == "" or value is None:
        return text.lower()
    return value