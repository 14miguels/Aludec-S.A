from src.schema.schema import Section
from src.parsing.text_cleaner import remove_dup
from src.schema.schema import Section, Substance
import re
# função para ler o texto 

def find_section_end(text: str, start: int, next_section_number: int) -> int: #problema que isto resolve, podem haver 2 markers que é secçao n ou n.1

  ###
  # isto resolve o problema de encontrar o fim pq pode ser secção n ou n.1
  # por isso criei 2 candidatos ao fim que são os que disse 
  # e verifiquei se eles existiam depois do inicio definifo 
  # se sim meto na lista 
  # se nao ignoro
  # depois escolho o com index menor indicando onde comeca a nova secção 
                                                               
    next_section_marker = f"SECÇÃO {next_section_number}"
    next_subsection_marker = f"{next_section_number}.1"

    end_candidates = []

    next_section_index = text.find(next_section_marker, start)
    if next_section_index != -1:
        end_candidates.append(next_section_index)

    next_subsection_index = text.find(next_subsection_marker, start)
    if next_subsection_index != -1:
        end_candidates.append(next_subsection_index)

    if not end_candidates:
        return -1

    return min(end_candidates)


def split_sec(text : str) -> list[Section]:

    sections = []
    for n in range(1,17):
        
        current_marker = f"SECÇÃO {n}"
        next_section_number = n + 1

        start = text.find(current_marker)
        
        if start == -1:
            continue
        
        end = find_section_end(text, start, next_section_number)

        if end == -1:
            sec_text = text[start:]
        else:
            sec_text = text[start:end]

        sec_text = remove_dup(sec_text)
        first_line = sec_text.splitlines()[0]

        # remove "SECÇÃO X:" ou "SECÇÃO X"
        if ":" in first_line:
            sec_title = first_line.split(":", 1)[1].strip()
        else:
            # fallback caso não exista :
            parts = first_line.split(maxsplit=2)
            sec_title = parts[-1].strip() if len(parts) >= 3 else first_line.strip()

        sec_number = n

        section_obj = Section(
            section_number = sec_number,
            title = sec_title,
            raw_text = sec_text
        )
        sections.append(section_obj)
    
    return sections

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
