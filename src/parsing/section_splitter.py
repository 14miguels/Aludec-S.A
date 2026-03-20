from src.extraction.schema import Section

# função para ler o texto 

def read_raw_text(file_path: str) -> str: 
    file = open(file_path, "r", encoding="utf-8")
    text = file.read()
    file.close()
    return text


# função para separar secções

def remove_dup(text_section : str) -> str:

    text = text_section.split("\n") # dividir numa lista por linhas
    seen = set() # vou usar o set para meter as linhas que ja vi e assim ignoro as dups 
    clean_lines = [] # lista final com as linhas nao dups de uma section

    for line in text:

        normalized_line = line.strip() #.strip vai normalizar a linha ou seja remover " " \n e assim

        if(normalized_line in seen):
            continue
        if not normalized_line: #ignora linhas vazias
            continue
        else:
            clean_lines.append(normalized_line)
            seen.add(normalized_line)

    new_text = ""
    for line in clean_lines:  # converter em str 

        new_text += line + "\n"

    return new_text

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


text = read_raw_text("output/raw_text.txt")
sections = split_sec(text)
