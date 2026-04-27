
SECTION3_EXTRACTION_PROMPT = """
You are an expert at extracting chemical composition data from Safety Data Sheets (SDS/FDS/Fichas de Dados de Segurança).

Task:
Extract the substances/components explicitly listed in Section 3 of the SDS text below.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a JSON array.
- Each item must have exactly these keys:
  - name
  - cas_number
  - ce_number
  - percentage

Important context:
- The text may come from Portuguese, Spanish or English SDS documents.
- Section 3 may be formatted as a broken table because it was extracted from a PDF.
- Names, CAS numbers and percentages may be separated across multiple lines.
- The ingredient name can appear before OR after the CAS/EC/Index block.
- Some suppliers put the name at the far right or below the CAS block.

Main extraction rules:
- Extract ONLY real ingredients/components from Section 3.
- Use CAS numbers as anchors whenever possible.
- However, some real ingredients may not show a CAS number in the extracted text.
- If an ingredient has a clear name and a clear concentration/percentage, extract it even when the CAS number is missing.
- Each real ingredient row should produce exactly one JSON object.
- For each ingredient row, search the nearby block for:
  1. the closest valid ingredient name;
  2. the closest CAS number, if present;
  3. the closest CE/EC/EINECS number, if present;
  4. the closest concentration/percentage value.
- Preserve the CAS number exactly as written when present.
- Preserve the CE/EC/EINECS number exactly as written when present.
- Set cas_number to null only when the ingredient is real but no CAS number is present.
- Set ce_number to null only when the ingredient is real but no CE/EC/EINECS number is present.
- Preserve percentages exactly as written, including ranges and symbols such as ≥, ≤, <, >.
- Valid percentage examples include:
  - "30-40"
  - "10 - 20"
  - "≥25 - ≤50"
  - "≤0.30"
  - "0.1-1"
  - "1-10"
- If a percentage appears as "% [peso]", "% em massa", "% weight", "% w/w", extract only the numeric range/value.
- If a CAS number is present but a name is missing in the local block, use null for name.
- If a CAS number is present but no percentage is present in the local block, use null for percentage.
- If a real ingredient has a name and percentage but no CAS number, set cas_number to null.
- If a real ingredient has a name and percentage but no CE/EC/EINECS number, set ce_number to null.
- Extract CE/EC/EINECS numbers from labels such as "CE", "EC", "EINECS", "Número CE", "CE (Comunidade Europeia)", "N.º CE", "Nº CE".
- Valid CE/EC/EINECS examples include "204-658-1", "215-535-7", "202-849-4".
- Never return placeholder values such as "No Disponible", "Não disponível", "Not available" or "Not applicable" as name, cas_number or percentage.
- Do not invent missing values.

- Valid names are ingredient names such as:
  - "ACETATO DE ETILO"
  - "XILENO, BRUTO"
  - "TOLUENO, BRUTO"
  - "etilbenceno"
  - "NAFTALENO, BRUTO"
  - "acetato de n-butilo"
  - "nafta disolvente (petróleo), fracción aromática pesada"
  - "Oxybis(methyl-2,1-ethandiyl)diacrylat"
  - "2-[[2,2-bis[[(1-oxoallyl)oxy]methyl]butoxy]methyl]-2-ethyl-1,3-propanediyl diacrylate"
  - "2-Propenoic acid, polymer with 2,2-bis(hydroxymethyl)-1,3-propanediol, methyloxirane and oxirane"
  - "2-Propensäure, 2-Methyl-, 2-Hydroxidethylester, Reaktionsprodukte mit Phosphoroxid"
  - "metacrilato de 2-hidroxietilo"
  - "2-Propensäure, Reaktionsprodukte mit Dipentaerythritol"
  - "Methyl-phenylglyoxylat"
  - "2-Propenoic acid, reaction products with pentaerythritol"
  - "Siloxanes and silicones, 3-[3-(acetyloxy)-2-hydroxypropoxy]propyl Me, di-Me, 3-[2-hydroxy-3-[(1-oxo-2-propenyl)oxy]propoxy]propyl Me"
  - "óxido de difenil(2,4,6-trimetilbenzoil)fosfina"
- Names may appear near markers such as:
  - "Nombre"
  - "Nome"
  - "Nombre del Producto/Ingrediente"
  - "Produto/Ingrediente"
  - "Ingredient"
- If the name appears after several CAS/EC/Index lines because of table extraction order, still associate it with the correct CAS block when it is clearly part of that ingredient row.
- Some OCR/text extraction outputs may split words with spaces between individual letters, for example "S il ox a ne s a n d s il ic o ne s". Reconstruct these into the closest chemically meaningful name when the surrounding text clearly identifies the ingredient.
- Some names may contain unnecessary spaces around hyphens, for example "2 - P r o p e n s ä u r e". Remove OCR spacing noise and return the readable chemical name.
- If a line contains only a chemical name followed by a hazard classification and then a percentage, extract the chemical name and the percentage even if no CAS number appears in that block.

- Ignore table headers such as "Nombre", "Nome", "Identificadores", "%", "% [peso]", "% em massa", "Classificação", "Clasificación", "Tipo".
- Ignore placeholder values such as "No Disponible", "Não disponível", "Não aplicável", "Not available", "Not applicable", "N/A", "None" and "null". Never return them as names, CAS numbers or percentages.
- Ignore REACH registration numbers such as "01-2119...".
- Do not ignore EC/CE/EINECS numbers. Extract them into ce_number when present.
- Ignore Index numbers.
- Ignore CLP hazard classes such as:
  - "Flam. Liq. 2"
  - "Skin Irrit. 2"
  - "Eye Irrit. 2"
  - "STOT SE 3"
  - "Aquatic Chronic 3"
  - "Asp. Tox. 1"
- Ignore H-codes and EUH-codes such as H225, H226, H315, H319, H336, EUH066.
- Ignore ATE values, DNEL, PNEC, exposure limits, notes, legends and explanatory paragraphs.
- Ignore statements saying no additional ingredients are present.

Special table pattern often seen in Spanish Chemwatch SDS:
The table may appear like this:
1.141-78-6
2.205-500-4
3.607-022-00-5
4.No Disponible
30-40
...
ACETATO DE ETILO

 In this case, return:
 [
   {{
     "name": "ACETATO DE ETILO",
     "cas_number": "141-78-6",
     "ce_number": "205-500-4",
     "percentage": "30-40"
   }}
 ]

Special table pattern often seen in Peter-Lacke SDS:
The table may appear like this:
CAS: 57472-68-1
EINECS: 260-754-3
Reg.nr.: 01-2119484629-21-XXXX
Oxybis(methyl-2,1-ethandiyl)diacrylat
 Eye Dam. 1, H318; Skin Irrit. 2, H315; Skin Sens. 1, H317
25-50%
Methyl-phenylglyoxylat
 Skin Sens. 1, H317
1-2,5%

 In this case, return:
 [
   {{
     "name": "Oxybis(methyl-2,1-ethandiyl)diacrylat",
     "cas_number": "57472-68-1",
     "ce_number": "260-754-3",
     "percentage": "25-50%"
   }},
   {{
     "name": "Methyl-phenylglyoxylat",
     "cas_number": null,
     "ce_number": null,
     "percentage": "1-2,5%"
   }}
 ]

 Example output:
 [
   {{
     "name": "ACETATO DE ETILO",
     "cas_number": "141-78-6",
     "ce_number": "205-500-4",
     "percentage": "30-40"
   }},
   {{
     "name": "XILENO, BRUTO",
     "cas_number": "1330-20-7",
     "ce_number": "215-535-7",
     "percentage": "10-20"
   }},
   {{
     "name": "etilbenceno",
     "cas_number": "100-41-4",
     "ce_number": "202-849-4",
     "percentage": "1-10"
   }}
 ]

 Before returning JSON, internally verify:
 - every output object represents a real ingredient/component;
 - every output object has a name unless the ingredient is truly unnamed;
 - every output object has one CAS number or null if truly missing;
 - every output object has one CE/EC/EINECS number or null if truly missing;
 - every CAS number in the ingredient table has been considered;
 - every clear ingredient row with name + percentage has been considered, even without CAS;
 - names are not hazard classifications;
 - percentages are not exposure limits, DNEL, PNEC, STEL, VLA or toxicological values;
 - placeholder values such as "No Disponible" or "Não disponível" are not returned.

Section 3 text:
{section_text}
""".strip()


SECTION2_HAZARD_EXTRACTION_PROMPT = """
You are an expert at extracting product-level hazard classifications from Safety Data Sheets (SDS/FDS).

Task:
Extract ONLY the product or mixture hazards explicitly stated in Section 2 of the SDS text below.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a JSON array.
- Each item must have exactly these keys:
  - code
  - description

Extraction rules:
- Extract ONLY product-level hazards from Section 2.
- Do NOT extract hazards that belong only to individual substances/components from Section 3 or later sections.
- Extract all H-codes and EUH-codes that describe the product/mixture classification or label hazards.
- If the code and description appear together, return both.
- If the code appears with only a classification category and no natural-language hazard statement, return the code and set description to null.
- Preserve the original description wording when available.
- Remove duplicates by code.

Valid examples:
- H225 Líquido y vapores muy inflamables.
- H336 Puede provocar somnolencia o vértigo.
- H315 Provoca irritación cutánea.
- Flam. Liq. 3, H226
- EUH066 Pode provocar pele seca ou gretada, por exposição repetida.

Ignore:
- precautionary statements such as P210, P280, P501;
- supplier information;
- emergency contacts;
- Section 3 ingredient classifications;
- Section 16 full legal text unless it is clearly part of Section 2.

Example output:
[
  {{
    "code": "H225",
    "description": "Líquido y vapores muy inflamables."
  }},
  {{
    "code": "H336",
    "description": "Puede provocar somnolencia o vértigo."
  }}
]

Section 2 text:
{section_text}
""".strip()


SECTION9_PHYSICAL_PROPERTIES_EXTRACTION_PROMPT = """
You are an expert at extracting product-level physical and chemical properties from Safety Data Sheets (SDS/FDS).

Task:
Extract ONLY the product-level physical and chemical properties explicitly stated in Section 9 of the SDS text below.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a single JSON object.
- The object must have exactly these keys:
  - state
  - density
  - flash_point
  - voc

Extraction rules:
- Extract ONLY values referring to the product/mixture.
- Preserve original wording and units exactly when present.
- If the value is explicitly "No Disponible", "Não disponível", "Not available" or equivalent, return null.
- Do not invent, convert or calculate values.

Field guidance:
- state:
  - Extract physical state, e.g. "líquido", "Líquido", "Liquid", "Solid".
  - Look for labels such as "Estado Físico", "Estado físico", "Physical state", "Estado".
- density:
  - Extract product density or relative density.
  - Look for "Densidad Relativa", "Densidade relativa", "Density", "Relative density".
  - Examples: "0.9", "0.87", "1.03 g/cm3".
- flash_point:
  - Extract the flash point exactly as written.
  - Look for "Punto de Inflamación", "Ponto de inflamação", "Flash point".
  - Examples: "2", "2 °C", "Vaso fechado: 23°C".
- voc:
  - Extract VOC/COV value exactly as written when present.
  - Look for "COV g/L", "VOC", "COV", "Componente Volatil", "volatile organic compounds", "compostos orgânicos voláteis".
  - If the value is explicitly unavailable, return null.

Example output:
{{
  "state": "líquido",
  "density": "0.9",
  "flash_point": "2",
  "voc": null
}}

Section 9 text:
{section_text}
""".strip()


SECTION14_TRANSPORT_EXTRACTION_PROMPT = """
You are an expert at extracting transport information from Safety Data Sheets (SDS/FDS).

Task:
Extract ONLY product-level transport information explicitly stated in Section 14 of the SDS text below.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a single JSON object.
- The object must have exactly these keys:
  - un_number
  - shipping_name
  - hazard_class
  - packing_group
  - environmental_hazard

Extraction rules:
- Extract transport information from Section 14 only.
- Prefer ADR/RID road transport values when multiple modes are present, unless a general value is clearly shared across all modes.
- Preserve values exactly as written when possible.
- If a value is explicitly not applicable/unavailable, return null.
- Do not invent values.

Field guidance:
- un_number:
  - Look for "Número ONU", "Número UN", "UN number", "14.1".
  - Return values like "UN1263" or "1263" exactly as written.
- shipping_name:
  - Look for "Designación oficial de transporte", "Designação oficial de transporte", "Proper shipping name", "14.2".
  - Extract the official transport name, even if it is long.
- hazard_class:
  - Look for "Clase", "Classe", "Class", "Clase(s) de peligro".
  - Return values like "3".
- packing_group:
  - Look for "Grupo de embalaje", "Grupo de embalagem", "Packing group".
  - Return "I", "II" or "III".
- environmental_hazard:
  - Look for "Peligros para el medio ambiente", "Perigos para o ambiente", "Environmental hazards", "Contaminante marino", "Marine pollutant".
  - Return the explicit value, e.g. "Peligroso para el medio ambiente", "Contaminante marino", "Sim", "Não", "Yes", "No".

Example output:
{{
  "un_number": "1263",
  "shipping_name": "PINTURA (incluye pintura, laca, esmalte, colorante, goma laca, barniz, abrillantador, encáustico y base líquida para lacas) o PRODUCTOS PARA PINTURA (incluye solventes y diluyentes para pinturas)",
  "hazard_class": "3",
  "packing_group": "II",
  "environmental_hazard": "Peligroso para el medio ambiente"
}}

Section 14 text:
{section_text}
""".strip()


SECTION15_SEVESO_EXTRACTION_PROMPT = """
You are an expert at extracting Seveso-related regulatory information from Safety Data Sheets (SDS/FDS).

Task:
Extract ONLY Seveso category information explicitly stated in Section 15 of the SDS text below.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a single JSON object.
- The object must have exactly this key:
  - category

Extraction rules:
- Extract ONLY Seveso category codes.
- Look for phrases such as:
  - "Directiva Seveso"
  - "Diretiva Seveso"
  - "Seveso III"
  - "2012/18/UE"
  - "2012/18/EU"
  - "Información según 2012/18/UE"
  - "Critérios de perigo"
  - "Categorías de peligro"
  - "Seveso Categoría"
- Valid Seveso category examples include:
  - "P5a"
  - "P5b"
  - "P5c"
  - "E1"
  - "E2"
  - "H2"
  - "H3"
- If multiple Seveso categories are present, return them as a single comma-separated string exactly as listed.
- If the document explicitly states that the product is not subject to Seveso, return null.
- If Seveso is not mentioned, return null.
- Do NOT extract REACH, CLP, ECHA, ozone, inventory, exposure limit or industrial emissions information as Seveso values.

Example output:
{{
  "category": "H3, P5a, P5b, P5c, E2"
}}

Section 15 text:
{section_text}
""".strip()


DOCUMENT_METADATA_EXTRACTION_PROMPT = """
You are an expert at extracting structured metadata from Safety Data Sheets (SDS/FDS).

Task:
Extract document-level metadata from the provided SDS text. The text usually contains Section 1 and/or the document header.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a single JSON object.
- The object must have exactly these keys:
  - product_name
  - product_code
  - supplier
  - revision_date
  - version
  - language

General rules:
- Do not invent values.
- If a field is not found, return an empty string "".
- Keep the original product/supplier wording when possible.
- Trim extra spaces and line breaks.
- Do not extract phone numbers, emails or addresses as supplier.
- Do not extract hazard information, substances, CAS numbers or transport data here.
- Do not confuse section titles with product names.

Field guidance:

product_name:
- Extract the commercial/product name.
- Look for labels such as:
  - "Nome comercial"
  - "Nome do Produto"
  - "Nombre del Producto"
  - "Product name"
  - "Trade name"
  - "Identificador do produto"
- If the name appears on the following line, use that following line.
- If the commercial/product name starts with a leading reference/code followed by the actual name, remove the leading code from product_name and put that leading code in product_code.
- Example: "20027246 ESC-165 SBCC Glossy" must become product_code "20027246" and product_name "ESC-165 SBCC Glossy".
- Example: "90:2296/A CLEAR MATT TOPCOAT" must become product_code "90:2296/A" and product_name "CLEAR MATT TOPCOAT".
- Examples:
  - "PEHALUX Multilayer highgloss"
  - "THINNER"
  - "SOSA CAUSTICA LIQUIDA"

product_code:
- Extract the commercial/internal product reference, not the SDS/MSDS document number.
- Prefer a product reference/code embedded in the product title or next to product-name labels.
- If the product title begins with a reference followed by the commercial name, extract that leading reference as product_code and remove it from product_name.
- Look for labels such as:
  - "Código do produto"
  - "Código del producto"
  - "Product code"
  - "Reference"
  - "Referência"
- Do NOT use labels such as "Código do MSDS", "MSDS code", "SDS code", "Código da FDS", or document-control codes as product_code if a product reference exists elsewhere.
- If only an MSDS/SDS code exists and no product reference is visible, return an empty string for product_code.
- Examples:
  - "1811-93"
  - "001/000204/00"
  - "17001"
  - "20027246"
  - "90:2296/A"

supplier:
- Extract only the supplier/manufacturer/company name.
- Look for labels such as:
  - "Fornecedor"
  - "Fabricante/fornecedor"
  - "Nome do Fornecedor"
  - "Nombre del Proveedor"
  - "Supplier"
  - "Manufacturer"
- Return only the company name, not the address, phone, fax, email or website.
- Examples:
  - "PETER-LACKE GmbH"
  - "PPG Cetelon Lackfabrik GmbH"
  - "DAI NIPPON TORYO Co., Ltd."

revision_date:
- Extract the SDS revision/release/printing date.
- Look for labels such as:
  - "Data de lançamento/Data da revisão"
  - "Data da revisão"
  - "Data de revisão"
  - "data da impressão"
  - "Revisão"
  - "Fecha de revisión"
  - "Fecha de emisión"
  - "Revision date"
  - "Issue date"
- Return only the date value.
- Examples:
  - "3 Janeiro 2024"
  - "31.01.2023"
  - "21/12/2022"

version:
- Extract the SDS version number.
- Look for labels such as:
  - "Versão"
  - "Número da versão"
  - "Version"
  - "Número de versión"
- Return only the version value when possible.
- Examples:
  - "1.04"
  - "7"
  - "23"

language:
- Detect the main language of the document.
- Return one of:
  - "Português"
  - "Español"
  - "English"
- If uncertain, return an empty string "".

Example output:
{{
  "product_name": "PEHALUX Multilayer highgloss",
  "product_code": "1811-93",
  "supplier": "PETER-LACKE GmbH",
  "revision_date": "31.01.2023",
  "version": "7",
  "language": "Português"
}}

If the SDS text contains:
"20027246 ESC-165 SBCC Glossy"
and also contains:
"Código do MSDS 029129"
return:
{{
  "product_name": "ESC-165 SBCC Glossy",
  "product_code": "20027246",
  "supplier": "Akzo Nobel Car Refinishes S.L.",
  "revision_date": "10/16/2019",
  "version": "11",
  "language": "Português"
}}

SDS text:
{section_text}
""".strip()

DOCUMENT_SECTION_SPLIT_PROMPT = """
You are an expert at reading Safety Data Sheets (SDS/FDS) extracted from PDF text.

Task:
Identify the main SDS sections in the document text below and return them as structured JSON.

Return format:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- The output must be a JSON array.
- Each item must have exactly these keys:
  - section_number
  - title
  - raw_text

Rules:
- Detect sections semantically, even if formatting is noisy.
- Support Portuguese, Spanish and English headings:
  - "SECÇÃO", "SEÇÃO", "SECCIÓN", "SECCION", "SECTION".
- Keep the original section order.
- Do not invent sections.
- raw_text must contain only the text belonging to that section.
- Preserve enough local structure for tables, especially Section 3.
- Do not include repeated page headers/footers when obvious.

Example output:
[
  {{
    "section_number": 1,
    "title": "Identificación de la sustancia o la mezcla y de la sociedad o la empresa",
    "raw_text": "..."
  }},
  {{
    "section_number": 3,
    "title": "Composición/información sobre los componentes",
    "raw_text": "..."
  }}
]

Document text:
{text}
""".strip()


SUBSTANCES_VERIFICATION_PROMPT = """
You are an expert reviewer of chemical composition data extracted from Safety Data Sheets (SDS/FDS).

Task:
Verify and correct the extracted substances using ONLY the original Section 3 text.

You will receive:
1. The original Section 3 text extracted from the PDF.
2. A JSON array of substances previously extracted by another model.

Your job:
- Correct OCR/text-extraction spacing errors in chemical names.
- Correct broken chemical names split across lines.
- Correct wrong or missing CAS numbers when the correct CAS is clearly present in Section 3.
- Correct wrong or missing percentages when the correct percentage is clearly present in Section 3.
- Add missing substances if they are clearly present in Section 3.
- Remove entries that are not real substances/components.
- Remove placeholders such as "No Disponible", "Não disponível", "Not available", "Não aplicável", "Not applicable", "N/A".

Strict rules:
- Return ONLY valid JSON.
- Do not include markdown fences.
- Do not include explanations.
- Do not invent substances.
- Do not invent CAS numbers.
- Do not invent percentages.
- Use Section 3 text as the source of truth.
- Keep the original language/name style when possible.
- If a real substance has no CAS number in Section 3, use null for cas_number.
- If a real substance has no percentage in Section 3, use null for percentage.
- Do not include hazard classifications as substance names.
- Do not include H-codes, EUH-codes, ATE values, DNEL, PNEC, exposure limits or notes as substance names.
- Do not include table headers as substance names.

Output format:
Return a JSON array.
Each item must have exactly these keys:
- name
- cas_number
- percentage

Examples of corrections:
- "2 - P r o p e n s ä u r e" should become "2-Propensäure" when the surrounding text clearly shows that chemical name.
- "S il ox a ne s a n d s il ic o ne s" should become "Siloxanes and silicones" when the surrounding text clearly shows that chemical name.
- A substance with name + percentage but no visible CAS should be kept with cas_number set to null.

Original Section 3 text:
{section_text}

Previously extracted substances JSON:
{extracted_substances_json}
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


def build_document_metadata_extraction_prompt(section_text: str) -> str:
    return DOCUMENT_METADATA_EXTRACTION_PROMPT.format(section_text=section_text)

