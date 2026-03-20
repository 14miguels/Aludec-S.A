SECTION3_EXTRACTION_PROMPT = """
You are an expert at extracting structured chemical composition data from Safety Data Sheets (SDS).

Task:
Extract all chemical substances explicitly listed in Section 3 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Do not infer substances that are not explicitly present in the text.
- If a field is missing, use null.
- Preserve percentages exactly as written when possible.
- Preserve CAS numbers exactly as written.
- Ignore headers, footers, page numbers, phone numbers, supplier contacts, regulatory references, and hazard statements unless they belong directly to a listed substance.
- The output must be a JSON array.
- Each array item must have exactly these keys:
  - name
  - cas_number
  - percentage

Example output:
[
  {{
    "name": "n-butyl acetate",
    "cas_number": "123-86-4",
    "percentage": "≥25 - ≤50"
  }},
  {{
    "name": "xylene",
    "cas_number": "1330-20-7",
    "percentage": "≥25 - ≤49"
  }}
]

Section 3 text:
{section_text}
""".strip()


DOCUMENT_SECTION_SPLIT_PROMPT = """
You are an expert at reading Safety Data Sheets (SDS) extracted from PDF text.

Task:
Identify the main SDS sections that appear in the document text below and return them in structured JSON.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Detect sections semantically, even if formatting is noisy or headings vary by language.
- Each section must contain:
  - section_number
  - title
  - raw_text
- section_number must be an integer when clearly identifiable, otherwise null.
- title must be the section heading without extra decoration when possible.
- raw_text must contain the text that belongs to that section.
- The output must be a JSON array.
- Ignore repeated headers, footers, and page numbers when possible.

Example output:
[
  {{
    "section_number": 1,
    "title": "Identification of the substance/mixture and of the company/undertaking",
    "raw_text": "..."
  }},
  {{
    "section_number": 3,
    "title": "Composition/information on ingredients",
    "raw_text": "..."
  }}
]

Document text:
{text}
""".strip()


def build_section3_extraction_prompt(section_text: str) -> str:
    return SECTION3_EXTRACTION_PROMPT.format(section_text=section_text)


def build_document_section_split_prompt(text: str) -> str:
    return DOCUMENT_SECTION_SPLIT_PROMPT.format(text=text)