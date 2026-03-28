from src.schema.schema import SevesoInfo
from src.llm.parser import parse_seveso_info
from src.llm.client import call_llm
from src.llm.prompts import build_section15_seveso_extraction_prompt

def extract_section15(text:str)-> SevesoInfo | None:

    if text is None:
        return []
    
    text = text.strip()

    if text == "":
        return []
    
    response = call_llm(build_section15_seveso_extraction_prompt(text))

    if response is None:
        return []
    
    hazards = parse_seveso_info(response)
    
    return hazards

    