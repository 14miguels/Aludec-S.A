
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