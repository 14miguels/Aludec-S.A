from section_splitter import dic
import re

section_3 = dic.get("Secção 3", "")


def extract_cas_numbers(section: str) -> list[str]:
    pattern = r"CAS:\s*(\d{2,7}-\d{2}-\d)"
    cas_numbers = re.findall(pattern, section)

    unique_cas = []
    seen = set()

    for cas in cas_numbers:
        if cas in seen:
            continue
        seen.add(cas)
        unique_cas.append(cas)

    return unique_cas


def is_metadata_line(line: str) -> bool:
    stripped = line.strip()

    if stripped == "":
        return True

    metadata_prefixes = [
        "CAS:",
        "CE",
        "REACH",
        "Índice",
        "ATE",
        "Flam.",
        "Acute Tox.",
        "Skin Irrit.",
        "Eye Irrit.",
        "STOT",
        "Asp. Tox.",
        "Aquatic",
        "EUH",
        "Tipo",
        "Identificadores",
        "Limites específicos",
        "Nome do Produto/",
        "% em",
        "massa",
        "Classificação",
        "fatores M e ATEs",
        "Conforme Regulamento",
        "Código SUB",
        "Consultar a Secção",
    ]

    if any(stripped.startswith(prefix) for prefix in metadata_prefixes):
        return True

    if re.fullmatch(r"\d{2,7}-\d{2}-\d", stripped):
        return True

    if re.fullmatch(r"\d{3}-\d{3}-\d{2}-\d", stripped):
        return True

    if re.fullmatch(r"\d{2,3}-\d{3}-\d{1,2}", stripped):
        return True

    if re.fullmatch(r"[\d\s.,/()≥≤-]+", stripped):
        return True

    return False


def find_previous_chemical_name(lines: list[str], cas_index: int) -> str:
    for i in range(cas_index - 1, -1, -1):
        candidate = lines[i].strip()

        if is_metadata_line(candidate):
            continue

        return candidate

    return ""


def extract_chemical_components(section: str) -> list[dict[str, str]]:
    lines = section.split("\n")
    chemicals = []
    seen_cas = set()

    for i, line in enumerate(lines):
        match = re.search(r"CAS:\s*(\d{2,7}-\d{2}-\d)", line)
        if not match:
            continue

        cas_number = match.group(1)
        if cas_number in seen_cas:
            continue

        chemical_name = find_previous_chemical_name(lines, i)
        chemicals.append({
            "name": chemical_name,
            "cas": cas_number,
        })
        seen_cas.add(cas_number)

    return chemicals


print(extract_chemical_components(section_3))
