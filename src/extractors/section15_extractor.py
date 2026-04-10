from src.schema.schema import SevesoInfo
from src.llm.parser import parse_seveso_info
from src.llm.client import call_llm
from src.llm.prompts import build_section15_seveso_extraction_prompt


def extract_section15(text: str) -> SevesoInfo | None:
    """LLM extractor for Section 15 (Seveso) information."""
    if not text:
        return None

    response = call_llm(build_section15_seveso_extraction_prompt(text.strip()))
    if response is None:
        return None

    seveso = parse_seveso_info(response)
    return seveso

    
