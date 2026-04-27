"""Funções de pré-processamento de texto extraído dos PDFs.

Este módulo trabalha com texto bruto vindo do PDF, antes da extração estruturada.
A função principal é reduzir ruído para melhorar a separação de secções e as chamadas ao LLM.
"""

import re


PAGE_NUMBER_PATTERN = re.compile(r"^\d+\s*/\s*\d+$")
MULTIPLE_SPACES_PATTERN = re.compile(r"[ \t]+")


def clean_line(line: str) -> str:
    """Limpa uma linha individual de texto extraído do PDF."""
    line = line.replace("\u00a0", " ")
    line = MULTIPLE_SPACES_PATTERN.sub(" ", line)
    return line.strip()


def is_noise_line(line: str) -> bool:
    """Identifica linhas que normalmente são ruído em fichas SDS."""
    if not line:
        return True

    # Remove numeração de páginas, por exemplo: 4/26, 12 / 26, etc.
    if PAGE_NUMBER_PATTERN.match(line):
        return True

    return False


def normalize_section_keywords(line: str) -> str:
    """Normaliza pequenas variações comuns nos títulos de secções."""
    line = line.replace("SEÇÃO", "SECÇÃO")
    line = line.replace("Secção", "SECÇÃO")
    line = line.replace("Seção", "SECÇÃO")
    return line


def clean_raw_text(text: str, remove_duplicates: bool = True) -> str:
    """
    Limpa texto bruto extraído do PDF.

    Faz:
    - remoção de linhas vazias;
    - remoção de números de página;
    - normalização de espaços;
    - normalização de palavras-chave de secção;
    - remoção opcional de linhas duplicadas.
    """
    seen = set()
    clean_lines = []

    for line in text.splitlines():
        normalized_line = clean_line(line)
        normalized_line = normalize_section_keywords(normalized_line)

        if is_noise_line(normalized_line):
            continue

        if remove_duplicates and normalized_line in seen:
            continue

        seen.add(normalized_line)
        clean_lines.append(normalized_line)

    return "\n".join(clean_lines)


def remove_dup(text_section: str) -> str:
    """
    Mantém compatibilidade com o código antigo.

    Antes esta função apenas removia duplicados. Agora chama o pré-processador completo.
    """
    return clean_raw_text(text_section, remove_duplicates=True)