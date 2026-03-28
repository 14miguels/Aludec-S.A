from src.schema.schema import PhysicalProperties
from src.llm.parser import parse_physical_properties
from src.llm.client import call_llm
from src.llm.prompts import build_section9_physical_properties_extraction_prompt

def extract_section9(text:str)-> PhysicalProperties | None:

    if text is None:
        return []
    
    text = text.strip()

    if text == "":
        return []
    
    response = call_llm(build_section9_physical_properties_extraction_prompt(text))

    if response is None:
        return []
    
    hazards = parse_physical_properties(response)
    
    return hazards

    