from src.schema.schema import Hazard
from src.llm.parser import parse_hazards
from src.llm.client import call_llm
from src.llm.prompts import build_section2_hazard_extraction_prompt

def extract_hazards(text:str)->list[Hazard]:

    if text is None:
        return []
    
    text = text.strip()

    if text == "":
        return []
    
    response = call_llm(build_section2_hazard_extraction_prompt(text))

    if response is None:
        return []
    
    hazards = parse_hazards(response)
    
    return hazards

    