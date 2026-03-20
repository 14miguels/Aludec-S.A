from src.llm.parser import parse_substances
from src.llm.client import call_llm
from src.llm.prompts import build_section3_extraction_prompt
from src.schema.schema import Substance

def extract_substances(text:str)->list[Substance]:

    if text == None:
        return []
    
    text = text.strip()

    if text == "":
        return []
    
    response_str = call_llm(build_section3_extraction_prompt(text))

    if response_str == None:
        return []
    
    substances = parse_substances(response_str)
    return substances


