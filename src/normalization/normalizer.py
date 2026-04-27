import re
from copy import deepcopy
from typing import Any


# Dicionário local com descrições conhecidas para códigos de perigo.
# Serve para preencher descrições vazias quando o LLM devolve apenas o código H.
HAZARD_DESCRIPTIONS = {
    "H225": "Líquido e vapor facilmente inflamáveis.",
    "H226": "Líquido e vapor inflamáveis.",
    "H304": "Pode ser mortal por ingestão e penetração nas vias respiratórias.",
    "H312": "Nocivo em contacto com a pele.",
    "H315": "Provoca irritação cutânea.",
    "H319": "Provoca irritação ocular grave.",
    "H332": "Nocivo por inalação.",
    "H335": "Pode provocar irritação das vias respiratórias.",
    "H336": "Pode provocar sonolência ou vertigens.",
    "H361d": "Suspeito de afectar o nascituro.",
    "H373": "Pode afectar os órgãos após exposição prolongada ou repetida.",
    "H412": "Nocivo para os organismos aquáticos com efeitos duradouros.",
}

# Dicionário local para corrigir nomes de substâncias a partir do número CAS.
# Isto ajuda a corrigir erros óbvios de alinhamento entre nome e CAS.
KNOWN_CAS_NAMES = {
    "123-86-4": "acetato de n-butilo",
    "1330-20-7": "xileno",
    "100-41-4": "etilbenzeno",
    "108-88-3": "tolueno",
}


def clean_value(value: Any) -> Any:
    """Limpa valores simples antes de serem usados no Excel ou na BD."""
    # Se o valor vier como None, transforma em string vazia para evitar aparecer "None" no Excel.
    if value is None:
        return ""

    # Se não for texto, mantém o valor original. Exemplo: números ou booleanos.
    if not isinstance(value, str):
        return value

    # Remove espaços especiais e compacta múltiplos espaços/quebras de linha num único espaço.
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_product_or_substance_name(value: Any) -> str:
    """Remove referências/códigos soltos que aparecem colados a nomes.

    Esta limpeza é conservadora: atua apenas em códigos no início do texto ou
    códigos longos claramente numéricos, para não destruir nomes químicos.
    """
    value = clean_value(value)

    if not value:
        return ""

    value = str(value).strip()

    # Remove códigos no início do nome, por exemplo:
    # "90:2296/A CLEAR MATT TOPCOAT" -> "CLEAR MATT TOPCOAT"
    # "20027246 ESC-165 SBCC Glossy" -> "ESC-165 SBCC Glossy"
    value = re.sub(r"^\d+(?::\d+)?(?:/[A-Za-z0-9]+)?\s+", "", value)

    # Remove códigos longos isolados no início, por exemplo:
    # "029129 acetato de n-butilo" -> "acetato de n-butilo"
    value = re.sub(r"^\d{5,}\s+", "", value)

    # Remove espaços duplicados gerados pelas substituições anteriores.
    value = re.sub(r"\s+", " ", value).strip()

    return value


def split_leading_product_reference(value: Any) -> tuple[str, str]:
    """Split a leading product reference from a product name.

    Examples:
    - "20027246 ESC-165 SBCC Glossy" -> ("20027246", "ESC-165 SBCC Glossy")
    - "90:2296/A CLEAR MATT TOPCOAT" -> ("90:2296/A", "CLEAR MATT TOPCOAT")
    """
    value = clean_value(value)

    if not value:
        return "", ""

    value = str(value).strip()
    match = re.match(r"^(\d+(?::\d+)?(?:/[A-Za-z0-9]+)?)\s+(.+)$", value)

    if not match:
        return "", value

    product_code = match.group(1).strip()
    product_name = match.group(2).strip()

    return product_code, product_name


def normalize_percentage(value: Any) -> str:
    """Normaliza percentagens para ficarem com um formato mais consistente."""
    value = clean_value(value)

    # Se não houver percentagem, devolve vazio.
    if not value:
        return ""

    # Converte operadores ASCII para símbolos usados nas fichas técnicas.
    value = str(value)
    value = value.replace(">=", "≥")
    value = value.replace("<=", "≤")

    # Normaliza intervalos, por exemplo: "≥25-≤50" passa a "≥25 - ≤50".
    value = value.replace(" - ", "-")
    value = value.replace("-", " - ")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_cas(value: Any) -> str:
    """Extrai e normaliza um número CAS a partir de texto livre."""
    value = clean_value(value)

    # Se não houver CAS, devolve vazio.
    if not value:
        return ""

    # Procura padrões CAS, como 123-86-4 ou 1330-20-7.
    match = re.search(r"\b\d{2,7}-\d{2}-\d\b", str(value))
    return match.group(0) if match else str(value)


def normalize_substances(substances: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Limpa, corrige e remove duplicados da lista de substâncias."""
    normalized = []
    seen_cas = set()

    for substance in substances or []:
        # Normaliza cada campo principal da substância.
        cas_number = normalize_cas(substance.get("cas_number"))
        name = clean_product_or_substance_name(substance.get("name"))
        percentage = normalize_percentage(substance.get("percentage"))

        # Se o CAS for conhecido, usa o nome correto associado ao CAS.
        if cas_number in KNOWN_CAS_NAMES:
            name = KNOWN_CAS_NAMES[cas_number]

        # Remove duplicados quando o mesmo CAS já apareceu antes.
        if cas_number and cas_number in seen_cas:
            continue

        if cas_number:
            seen_cas.add(cas_number)

        # Guarda a substância já limpa numa estrutura estável.
        normalized.append({
            "name": name,
            "cas_number": cas_number,
            "percentage": percentage,
        })

    return normalized


def normalize_hazards(hazards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Limpa códigos de perigo, remove duplicados e preenche descrições em falta."""
    normalized = []
    seen_codes = set()

    for hazard in hazards or []:
        # Limpa código e descrição.
        code = clean_value(hazard.get("code"))
        description = clean_value(hazard.get("description"))

        # Ignora hazards sem código ou repetidos.
        if not code or code in seen_codes:
            continue

        # Se a descrição vier vazia, tenta preencher com o dicionário local.
        if not description and code in HAZARD_DESCRIPTIONS:
            description = HAZARD_DESCRIPTIONS[code]

        seen_codes.add(code)
        normalized.append({
            "code": code,
            "description": description,
        })

    return normalized


def normalize_dict_values(data: dict[str, Any]) -> dict[str, Any]:
    """Aplica limpeza simples a todos os valores de um dicionário."""
    return {
        key: clean_value(value)
        for key, value in (data or {}).items()
    }


def build_validation_status(data: dict[str, Any]) -> str:
    """Classifica a extração como OK ou REVIEW com base em campos mínimos esperados."""
    substances = data.get("substances") or []
    hazards = data.get("hazards") or []
    transport = data.get("transport") or {}
    physical = data.get("physical_properties") or {}

    # Sem substâncias, a extração precisa de revisão manual.
    if not substances:
        return "REVIEW"

    # Sem perigos, a extração também deve ser revista.
    if not hazards:
        return "REVIEW"

    # Para transporte, espera-se pelo menos o número ONU.
    if not transport.get("un_number"):
        return "REVIEW"

    # Para propriedades físicas, espera-se pelo menos densidade ou ponto de inflamação.
    if not physical.get("density") and not physical.get("flash_point"):
        return "REVIEW"

    return "OK"


def normalize_extraction(data: dict[str, Any]) -> dict[str, Any]:
    """Normaliza uma extração completa antes de a enviar para Excel ou outra saída final."""
    # Usa deepcopy para não alterar diretamente o dicionário original vindo da BD/pipeline.
    normalized = deepcopy(data)

    # Normaliza campos gerais da extração.
    normalized["file_name"] = clean_value(normalized.get("file_name"))
    normalized["language"] = clean_value(normalized.get("language")) or "Português"

    document_metadata = normalized.get("document_metadata") or {}
    if isinstance(document_metadata, dict):
        raw_product_name = clean_value(document_metadata.get("product_name"))
        existing_product_code = clean_value(document_metadata.get("product_code"))

        extracted_product_code, cleaned_product_name = split_leading_product_reference(raw_product_name)

        document_metadata["product_name"] = clean_product_or_substance_name(cleaned_product_name or raw_product_name)
        document_metadata["product_code"] = extracted_product_code or existing_product_code
        document_metadata["supplier"] = clean_value(document_metadata.get("supplier"))
        document_metadata["revision_date"] = clean_value(document_metadata.get("revision_date"))
        document_metadata["version"] = clean_value(document_metadata.get("version"))
        document_metadata["language"] = clean_value(document_metadata.get("language"))
        normalized["document_metadata"] = document_metadata

    # Normaliza cada bloco principal da extração.
    normalized["substances"] = normalize_substances(normalized.get("substances") or [])
    normalized["hazards"] = normalize_hazards(normalized.get("hazards") or [])
    normalized["transport"] = normalize_dict_values(normalized.get("transport") or {})
    normalized["seveso"] = normalize_dict_values(normalized.get("seveso") or {})
    normalized["physical_properties"] = normalize_dict_values(normalized.get("physical_properties") or {})

    # Adiciona um estado simples de validação para indicar se a extração parece completa.
    normalized["validation_status"] = build_validation_status(normalized)

    return normalized