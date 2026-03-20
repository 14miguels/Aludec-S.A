from src.parsing import section_splitter
from src.extraction.schema import Substance
from src.extraction.schema import Section
import re

text = section_splitter.read_raw_text("output/raw_text.txt")
sections = section_splitter.split_sec(text)
section_3 = sections[2]

def is_metadata_line(line: str) -> bool: #o objetivo desta func é ignorar tudo que podem nao ser nomes de quimicos
    stripped = line.strip() #pego na linha e removo os espaços

    if stripped == "":
        return True     #se a linha nao tiver nada quero que mais tarde seja ignorada 

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
    #nesta funcao estou vou devolver o nome do quimico para o cas no index x 
    #caso a str atras seja lixo ele da continue
    #caso contrario é um potencial nome de quimico e dou return do candidato 
    for i in range(cas_index - 1, -1, -1):
        candidate = lines[i].strip()

        if is_metadata_line(candidate):
            continue
        if re.fullmatch(r"(<|>|<=|>=)?\s*\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\s*%|(<|>|<=|>=)?\s*\d+(\.\d+)?\s*%", candidate):
            continue

        return candidate

    return ""

def find_chemical_percent(lines :list[str], cas_index:int) ->str:

    for i in range(cas_index-1,-1,-1):
        candidate = lines[i].strip()

        if is_metadata_line(candidate):
            continue

        if re.fullmatch(r"(<|>|<=|>=)?\s*\d+(\.\d+)?\s*-\s*\d+(\.\d+)?\s*%|(<|>|<=|>=)?\s*\d+(\.\d+)?\s*%", candidate):
            return candidate
    
    return ""


def extract_chemical_components(section: Section) -> list[Substance]:
    section_txt = section.raw_text
    lines = section_txt.split("\n") #lines é umas lista com strings de linhas ["linha1","linha2"...]
    substances = []
    seen_cas = set()

    for i, line in enumerate(lines): #enumerate lines transforma a lista de linhas em pairs do tipo (i,str->line)
        match = re.search(r"CAS:\s*(\d{2,7}-\d{2}-\d)", line) #vou à linha em causa e vejo se é um cas 
        if not match: #se não der match ao regex é pq não é cas, então ignoro 
            continue

        cas_number = match.group(1) #devolve apenas o numero do cas
        if cas_number in seen_cas: #se for repetido ignoro 
            continue

        chemical_name = find_previous_chemical_name(lines, i) #chamo a funcao que criei em cima para encontrar o nome
        percent = find_chemical_percent(lines, i)

        substance = Substance(
            name= chemical_name,
            cas_number= cas_number,
            percentage= percent
        )
        seen_cas.add(cas_number)
        substances.append(substance)

    return substances


print(extract_chemical_components(section_3)[0])
