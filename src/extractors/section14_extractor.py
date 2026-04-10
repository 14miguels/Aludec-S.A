from src.schema.schema import TransportInfo
from src.llm.parser import parse_transport_info
from src.llm.client import call_llm
from src.llm.prompts import build_section14_transport_extraction_prompt


def extract_section14(text: str) -> TransportInfo | None:
    """LLM extractor for transport information (Section 14)."""
    if not text:
        return None

    response = call_llm(build_section14_transport_extraction_prompt(text.strip()))
    if response is None:
        return None

    transport = parse_transport_info(response)
    return transport

    
