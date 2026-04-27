"""Extractor for document-level SDS metadata.

This extractor reads the document header / Section 1 text and asks the LLM to
extract product metadata such as product name, code, supplier, revision date,
version and language.
"""

from src.llm.client import call_llm
from src.llm.prompts import build_document_metadata_extraction_prompt
from src.llm.parser import parse_document_metadata
from src.schema.schema import DocumentMetadata


def extract_document_metadata(section_text: str) -> DocumentMetadata:
    """Extract document metadata from SDS Section 1/header text."""
    if section_text is None:
        return DocumentMetadata()

    section_text = section_text.strip()

    if section_text == "":
        return DocumentMetadata()

    prompt = build_document_metadata_extraction_prompt(section_text)
    response_str = call_llm(prompt)

    if response_str is None:
        return DocumentMetadata()

    return parse_document_metadata(response_str)