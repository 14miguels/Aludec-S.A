SECTION3_EXTRACTION_PROMPT = """
You are an expert at extracting structured chemical composition data from Safety Data Sheets (SDS).

Task:
Extract all chemical substances explicitly listed in Section 3 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Extract only substances explicitly listed as ingredients/components in Section 3.
- Extract substances exactly as they appear in the text.
- If the substance information is split across multiple lines, you MUST reconstruct it into a single substance entry.
- The substance name may appear before or after the CAS number and percentage; you must associate them correctly.
- If the substance name is not on the same line as the CAS number, look at the same block and the immediately adjacent lines above or below.
- NEVER return a substance with an empty name if a name exists anywhere near the CAS number or percentage.
- If a field is missing and truly not present, use null.
- Preserve percentages exactly as written when possible.
- Preserve CAS numbers exactly as written.
- Ignore headers, footers, page numbers, contact information, REACH registration numbers, EC numbers, notes, explanatory paragraphs, SVHC/PBT statements, and non-component content.
- Ignore CLP hazard classifications, H-codes, EUH-codes, pictograms, ATE values, and concentration limits unless needed only to identify the correct substance block.
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


SECTION2_HAZARD_EXTRACTION_PROMPT = """
You are an expert at extracting product-level hazard classifications from Safety Data Sheets (SDS).

Task:
Extract ONLY the product or mixture hazards explicitly stated in Section 2 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Extract ONLY product-level hazards from Section 2.
- Do NOT extract hazards that belong to individual substances/components from Section 3 or any later section.
- Prioritize CLP/GHS hazard lines that contain H-codes or EUH-codes.
- If a line contains both a classification and a hazard code, extract the hazard code.
- If a hazard code appears without its description, keep the code and set description to null.
- If a description appears without a clear hazard code, set code to null.
- Ignore supplier information, emergency contacts, page numbers, headers, footers, legal notes, generic explanatory text, and unrelated regulatory references.
- Ignore free-text "other dangers" statements unless they are clearly presented as a product hazard statement.
- Remove duplicates by code+description.
- Preserve the original wording of descriptions when present.
- The output must be a JSON array.
- Each array item must have exactly these keys:
  - code
  - description

Extraction guidance:
- Valid examples of codes include H225, H226, H315, H319, H332, H335, H336, H373, H412, EUH066, EUH208.
- Typical valid source lines include formats such as:
  - Flam. Liq. 3, H226
  - Skin Irrit. 2, H315
  - H336 May cause drowsiness or dizziness
- If Section 2 includes only classification lines such as "Flam. Liq. 3, H226" and does not include the textual description, return the code and set description to null.
- If Section 2 includes textual hazard statements such as "H226 Liquid and vapour flammable", return both code and description.
- Do not invent or infer missing hazard codes or descriptions.

Example output:
[
  {{
    "code": "H225",
    "description": null
  }},
  {{
    "code": "H336",
    "description": "May cause drowsiness or dizziness"
  }},
  {{
    "code": "EUH208",
    "description": "Contains methyl methacrylate. May produce an allergic reaction"
  }}
]

Section 2 text:
{section_text}
""".strip()

SECTION9_PHYSICAL_PROPERTIES_EXTRACTION_PROMPT = """
You are an expert at extracting physical and chemical properties from Safety Data Sheets (SDS).

Task:
Extract ONLY the product-level physical and chemical properties explicitly stated in Section 9 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Extract ONLY product-level properties from Section 9.
- Do NOT extract properties that belong only to individual substances/components unless Section 9 clearly presents them as values for the product or mixture.
- Preserve the original wording and units exactly as written when present.
- If a value is not clearly present, set it to null.
- Do not invent, infer, convert, or calculate missing values.
- Ignore page numbers, headers, footers, legal notes, explanatory paragraphs, and unrelated text.
- Ignore repeated values unless they clearly refer to different properties.
- The output must be a single JSON object.
- The JSON object must have exactly these keys:
  - state
  - density
  - flash_point
  - voc

Extraction guidance:
- "state" should capture the physical state of the product, for example:
  - "Liquid"
  - "Solid"
  - "Gas"
- "density" should capture the density value exactly as written, including units if present.
- "flash_point" should capture the flash point exactly as written, including units and method if present.
- "voc" should capture the VOC value exactly as written, including units if present.
- If Section 9 contains multiple VOC values, extract the one explicitly referring to the product or supplied mixture.
- If Section 9 contains multiple density-like values, extract the one explicitly referring to product density or relative density of the mixture.
- If a field is missing, use null.

Example output:
{{
  "state": "Líquido",
  "density": "0.87",
  "flash_point": "Vaso fechado: 23°C",
  "voc": null
}}

Section 9 text:
{section_text}
""".strip()

SECTION14_TRANSPORT_EXTRACTION_PROMPT = """
You are an expert at extracting transport information from Safety Data Sheets (SDS).

Task:
Extract ONLY the product-level transport information explicitly stated in Section 14 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Extract ONLY transport information from Section 14.
- Do NOT extract transport-related information from any other section.
- Preserve the original wording and codes exactly as written when present.
- If a value is not clearly present, set it to null.
- Do not invent, infer, normalize, translate, or calculate missing values.
- Ignore page numbers, headers, footers, legal notes, explanatory paragraphs, and unrelated text.
- If multiple transport modes are present (ADR/RID, IMDG, IATA, ADN), extract the general product-level values when clearly shared across modes.
- If a field differs by transport mode and there is no single common value, extract the value that is most clearly presented as the main/general one in Section 14.
- The output must be a single JSON object.
- The JSON object must have exactly these keys:
  - un_number
  - shipping_name
  - hazard_class
  - packing_group
  - environmental_hazard

Extraction guidance:
- "un_number" should capture values such as:
  - "UN1263"
- "shipping_name" should capture the official transport name exactly as written.
- "hazard_class" should capture the transport hazard class exactly as written, for example:
  - "3"
- "packing_group" should capture values such as:
  - "I"
  - "II"
  - "III"
- "environmental_hazard" should capture the explicit yes/no style value exactly as written when present, for example:
  - "Sim"
  - "Não"
  - "Yes"
  - "No"
- If Section 14 explicitly says the product is not environmentally hazardous, extract that value.
- If a field is missing, use null.

Example output:
{{
  "un_number": "UN1263",
  "shipping_name": "PAINT RELATED MATERIAL",
  "hazard_class": "3",
  "packing_group": "III",
  "environmental_hazard": "Não"
}}

Section 14 text:
{section_text}
""".strip()

SECTION15_SEVESO_EXTRACTION_PROMPT = """
You are an expert at extracting regulatory information from Safety Data Sheets (SDS), specifically Seveso Directive classifications.

Task:
Extract ONLY the Seveso-related information explicitly stated in Section 15 of the SDS text below.

Rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Extract ONLY Seveso-related information from Section 15.
- Do NOT extract other regulatory frameworks (e.g., REACH, CLP lists, ozone regulations, etc.).
- Preserve the original wording exactly as written.
- If a value is not clearly present, set it to null.
- Do not invent, infer, normalize, or translate missing values.
- Ignore page numbers, headers, footers, legal notes, explanatory paragraphs, and unrelated regulatory references.
- The output must be a single JSON object.
- The JSON object must have exactly these keys:
  - category

Extraction guidance:
- Look specifically for mentions of:
  - "Directiva Seveso"
  - "Seveso Directive"
  - "Critérios de perigo"
  - Seveso category codes such as:
    - "P5c"
    - "P5a"
    - "P5b"
- If multiple Seveso categories are present, extract them as a single string (e.g., "P5c").
- If the document explicitly states that the product is controlled by Seveso, extract the category value.
- If Seveso is mentioned but no category is given, return:
  - "category": null
- If no Seveso reference exists in Section 15, return null for category.

Example output:
{{
  "category": "P5c"
}}

Section 15 text:
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
- Keep the original order of sections.
- Do not invent sections that are not present in the document text.

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


def build_section2_hazard_extraction_prompt(section_text: str) -> str:
    return SECTION2_HAZARD_EXTRACTION_PROMPT.format(section_text=section_text)

def build_section9_physical_properties_extraction_prompt(section_text: str) -> str:
    return SECTION9_PHYSICAL_PROPERTIES_EXTRACTION_PROMPT.format(section_text=section_text)


def build_section14_transport_extraction_prompt(section_text: str) -> str:
    return SECTION14_TRANSPORT_EXTRACTION_PROMPT.format(section_text=section_text)


def build_section15_seveso_extraction_prompt(section_text: str) -> str:
    return SECTION15_SEVESO_EXTRACTION_PROMPT.format(section_text=section_text)


def build_document_section_split_prompt(text: str) -> str:
    return DOCUMENT_SECTION_SPLIT_PROMPT.format(text=text)

