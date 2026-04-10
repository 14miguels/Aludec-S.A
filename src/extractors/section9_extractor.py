from src.schema.schema import PhysicalProperties
from src.llm.parser import parse_physical_properties
from src.llm.client import call_llm
from src.llm.prompts import build_section9_physical_properties_extraction_prompt


def extract_section9(text: str) -> PhysicalProperties | None:
    """LLM extractor for Section 9 physical properties."""
    if not text:
        return None

    response = call_llm(build_section9_physical_properties_extraction_prompt(text.strip()))
    if response is None:
        return None

    properties = parse_physical_properties(response)
    return properties

    
