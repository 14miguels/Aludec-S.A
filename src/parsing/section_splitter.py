from src.llm.parser import parse_sections
from src.llm.client import call_llm
from src.llm.prompts import build_document_section_split_prompt
from src.schema.schema import Section

def split_sections(text:str) -> list[Section]:

    if text == None:
        return []
    
    text = text.strip()
    
    if text == "":
        return []

    response_str = call_llm(build_document_section_split_prompt(text))

    if response_str == None:
        return []

    sections = parse_sections(response_str)

    return sections
