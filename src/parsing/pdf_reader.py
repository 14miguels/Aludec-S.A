import io

import fitz
import pytesseract #pega numa imagem e tenta ler o texto que esta desenhado
from PIL import Image #serve para abrir e manipular imagens

# O PDF reader foi desenvolvido para lidar com diferentes tipos de PDFs, incluindo documentos estruturados em formato de tabela.
# Inicialmente, verificou-se que o PyMuPDF (fitz) interpretava alguns destes PDFs como imagens,
# não conseguindo extrair texto através dos métodos convencionais (get_text).
# Para resolver este problema, foi implementada uma abordagem híbrida de extração:

# 1. Tentativa de extração direta com get_text(), quando o PDF contém texto selecionável.
# 2. Caso a extração seja insuficiente, utilização de get_text("blocks") para recuperar texto estruturado em blocos.
# 3. Como fallback final, aplicação de OCR (via pytesseract) após conversão da página em imagem.

# Esta estratégia permite garantir robustez na extração de texto, independentemente do formato interno do PDF,
# assegurando que tanto documentos digitais como documentos digitalizados (scanned) são processados corretamente.

MIN_PAGE_TEXT_LEN = 80
OCR_ZOOM = 2.0


def _extract_page_text(page: fitz.Page, pdf_path: str, page_number: int) -> str:
    """Extract text from one page using a hybrid strategy: text -> blocks -> OCR."""
    text = page.get_text() or "" 
    text = text.strip()

    if len(text) >= MIN_PAGE_TEXT_LEN:
        return text

    blocks_text_parts = []
    blocks = page.get_text("blocks")
    for block in blocks:
        block_text = (block[4] or "").strip()
        if block_text:
            blocks_text_parts.append(block_text)

    blocks_text = "\n".join(blocks_text_parts).strip()
    if len(blocks_text) >= MIN_PAGE_TEXT_LEN:
        return blocks_text

    matrix = fitz.Matrix(OCR_ZOOM, OCR_ZOOM)
    pix = page.get_pixmap(matrix=matrix)
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes))

    ocr_text = pytesseract.image_to_string(image).strip()

    return ocr_text



def read_raw_text(pdf_path: str) -> str:
    raw_pages = []

    with fitz.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf, start=1):
            page_text = _extract_page_text(page, pdf_path, page_index)
            raw_pages.append(page_text)

    raw_text = "\n\n".join(raw_pages).strip()

    if not raw_text:
        print(f"[ERROR][pdf_reader] No text could be extracted from: {pdf_path}")

    return raw_text

