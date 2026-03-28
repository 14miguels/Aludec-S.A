from src.schema.schema import TransportInfo
from src.llm.parser import parse_transport_info
from src.llm.client import call_llm
from src.llm.prompts import build_section14_transport_extraction_prompt

def extract_section14(text:str)-> TransportInfo | None:

    if text is None:
        return []
    
    text = text.strip()

    if text == "":
        return []
    
    response = call_llm(build_section14_transport_extraction_prompt(text))

    if response is None:
        return []
    
    hazards = parse_transport_info(response)
    
    return hazards

    