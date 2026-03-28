from src.parsing.pdf_reader import read_raw_text
from src.schema.schema import Substance, SDSDocument
from src.parsing.text_cleaner import remove_dup
from src.parsing.section_splitter import split_sections
from src.extractors.section3_extractor import extract_substances
from src.parsing.fallback import split_sec, extract_chemical_components
from src.pipeline.helpers.metadata_builder import init_metadata,init_sds, confidence_substances, validation_substances, confidence_hazards, validation_hazards, confidence_physical_properties, confidence_seveso, confidence_transport, validation_physical_properties, validation_seveso, validation_transport
from src.extractors.section2_extractor import extract_hazards
from src.extractors.section9_extractor import extract_section9
from src.extractors.section14_extractor import extract_section14
from src.extractors.section15_extractor import extract_section15
from typing import Optional
from src.schema.schema import Section
from pathlib import Path

def find_section(sections: list[Section], number: int) -> Optional[Section]:

    for section in sections:
        if section.section_number == number:
            return section
    
    return None

def run_pipeline(pdf_path: str) -> SDSDocument:
    """Run the full SDS extraction pipeline and return the extracted SDS document."""
    file_name = Path(pdf_path).name

    metadata_splitter = init_metadata()
    metadata_substances = init_metadata()
    metadata_hazards = init_metadata()
    metadata_physical_properties = init_metadata()
    metadata_seveso_info = init_metadata()
    metadata_transport_info = init_metadata()
    sds_document = init_sds(file_name, metadata_splitter, metadata_substances, metadata_hazards, metadata_physical_properties, metadata_seveso_info, metadata_transport_info )
    print("[PIPELINE] Starting SDS extraction pipeline...")

    raw_text = read_raw_text(pdf_path)
    text = remove_dup(raw_text)
    

    #======================================== SECÇÃO SPLIT ========================================#
    print("[STEP 1] Splitting document into sections (LLM)...")
    sections = split_sections(text)
    
    #fall-back caso llm falhe 
    if not sections:
        sections = split_sec(text)
        metadata_splitter.extraction_method= None
        print("[STEP 1] LLM section splitting failed. Falling back to regex...")
    
    else: 
        metadata_splitter.extraction_method = "LLM"
        print("[STEP 1] LLM section splitting succeeded.")

    if not sections:
        metadata_splitter.warnings.append("Section splitter failed")
        return sds_document
    
    #======================================== SECÇÃO 2 ========================================#

    section_2 = find_section(sections, 2)

    if section_2 is None:
        metadata_hazards.warnings.append("Failed to find section 2")
        return sds_document
    
    print("[STEP 2] Extracting hazards from Section 2 (LLM)...")
    hazards = extract_hazards(section_2.raw_text)

    if not hazards : 
        metadata_hazards.warnings.append("Failed to use LLM")
        metadata_hazards.extraction_method = "Regex"
        print("[STEP 2] LLM extraction failed...")
    else:
        metadata_hazards.extraction_method = "LLM"
        print("[STEP 2] Hazards extraction succeeded.")
    
    metadata_hazards.confidence = round(confidence_hazards(hazards)*100,2)
    metadata_hazards.warnings = validation_hazards(hazards)
    

    #======================================== SECÇÃO 3 ========================================#
    section_3 = find_section(sections,3)

    if section_3 is None:
        metadata_substances.warnings.append("Failed to find section 3")
        return sds_document
    
    print("[STEP 3] Extracting substances from Section 3 (LLM)...")
    # extract_substances expects the section text (str), not the Section object
    substances = extract_substances(section_3.raw_text)

    #fall-back caso llm falhex
    if not substances:
        substances = extract_chemical_components(section_3)
        metadata_substances.extraction_method = "Regex"
        print("[STEP 3] LLM extraction failed. Falling back to heuristic parser...")
    else:
        metadata_substances.extraction_method = "LLM"
        print("[STEP 3] Substance extraction succeeded.")
    
  
    metadata_substances.confidence = round(confidence_substances(substances)*100,1)
    metadata_substances.warnings = validation_substances(substances)

    #======================================== SECÇÃO 9 ========================================#

    section_9 = find_section(sections, 9)

    if section_9 is None:
        metadata_physical_properties.warnings.append("Failed to find section 9")
        return sds_document

    print("[STEP 4] Extracting physical properties from Section 9 (LLM)...")
    physical_properties = extract_section9(section_9.raw_text)

    if not physical_properties:
        metadata_physical_properties.warnings.append("Failed to use LLM")
        metadata_physical_properties.extraction_method = "Regex"
        print("[STEP 4] LLM extraction failed...")
    else:
        metadata_physical_properties.extraction_method = "LLM"
        print("[STEP 4] Physical properties extraction succeeded.")

    metadata_physical_properties.confidence = round(confidence_physical_properties(physical_properties) * 100, 2)
    metadata_physical_properties.warnings = validation_physical_properties(physical_properties)

    #======================================== SECÇÃO 14 ========================================#

    section_14 = find_section(sections, 14)

    if section_14 is None:
        metadata_transport_info.warnings.append("Failed to find section 14")
        return sds_document

    print("[STEP 5] Extracting transport info from Section 14 (LLM)...")
    transport = extract_section14(section_14.raw_text)

    if not transport:
        metadata_transport_info.warnings.append("Failed to use LLM")
        metadata_transport_info.extraction_method = "Regex"
        print("[STEP 5] LLM extraction failed...")
    else:
        metadata_transport_info.extraction_method = "LLM"
        print("[STEP 5] Transport extraction succeeded.")

    metadata_transport_info.confidence = round(confidence_transport(transport) * 100, 2)
    metadata_transport_info.warnings = validation_transport(transport)

    #======================================== SECÇÃO 15 ========================================#

    section_15 = find_section(sections, 15)

    if section_15 is None:
        metadata_seveso_info.warnings.append("Failed to find section 15")
        return sds_document

    print("[STEP 6] Extracting Seveso info from Section 15 (LLM)...")
    seveso = extract_section15(section_15.raw_text)

    if not seveso:
        metadata_seveso_info.warnings.append("Failed to use LLM")
        metadata_seveso_info.extraction_method = "Regex"
        print("[STEP 6] LLM extraction failed...")
    else:
        metadata_seveso_info.extraction_method = "LLM"
        print("[STEP 6] Seveso extraction succeeded.")

    metadata_seveso_info.confidence = round(confidence_seveso(seveso) * 100, 2)
    metadata_seveso_info.warnings = validation_seveso(seveso)

    return SDSDocument(
        file_name=file_name,
        language=None,
        sections=sections,
        substances=substances,
        hazards=hazards,
        physical_properties=physical_properties,
        transport=transport,
        seveso=seveso,
        
        splitter_metadata=metadata_splitter,
        substances_metadata=metadata_substances,
        hazards_metadata=metadata_hazards,
        physical_properties_metadata=metadata_physical_properties,
        transport_metadata=metadata_transport_info,
        seveso_metadata=metadata_seveso_info
)
