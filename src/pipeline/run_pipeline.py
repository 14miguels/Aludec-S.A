from src.parsing.pdf_reader import read_raw_text
from src.schema.schema import Substance
from src.parsing.text_cleaner import remove_dup
from src.llm.section_splitter import split_sections
from src.llm.section3_extractor import extract_substances
from src.parsing.fallback import split_sec, extract_chemical_components
from typing import Optional
from src.schema.schema import Section

def find_section(sections: list[Section], number: int) -> Optional[Section]:

    for section in sections:
        if section.section_number == number:
            return section
    
    return None

def run_pipeline(pdf_path: str) -> list[Substance]:
    """Run the full SDS extraction pipeline and return extracted substances."""
    
    print("[PIPELINE] Starting SDS extraction pipeline...")

    raw_text = read_raw_text(pdf_path)
    text = remove_dup(raw_text)

    #chamar o llm para dar split
    print("[STEP 1] Splitting document into sections (LLM)...")
    sections = split_sections(text)
    
    #fall-back caso llm falhe 
    if not sections:
        sections = split_sec(text)
        print("[STEP 1] LLM section splitting failed. Falling back to regex...")
    
    else: 
        print("[STEP 1] LLM section splitting succeeded.")

    if not sections:
        return []
    
    #chamar o llm para extrair dados
    section_3 = find_section(sections,3)

    if section_3 is None:
        return []
    
    print("[STEP 2] Extracting substances from Section 3 (LLM)...")
    # extract_substances expects the section text (str), not the Section object
    substances = extract_substances(section_3.raw_text)

    #fall-back caso llm falhe
    if not substances:
        substances = extract_chemical_components(section_3)
        print("[STEP 2] LLM extraction failed. Falling back to heuristic parser...")
    else:
        print("[STEP 2] Substance extraction succeeded.")

    return substances





