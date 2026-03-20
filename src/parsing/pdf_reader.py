import fitz

def read_raw_text(pdf_path: str) -> str:
    raw_text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            raw_text += page.get_text() + "\n"
    return raw_text
