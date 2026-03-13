import fitz

pdf = fitz.open("data/raw_pdfs/001.000204.00 -Thinner-V1.04.pdf")

num_page = pdf.page_count
raw_text = ""
for n in range(num_page): 
    page = pdf.load_page(n)
    text = page.get_text()
    raw_text += text + "\n"

file = open("src/output/raw_text.txt", "w", encoding="utf-8")
file.write(raw_text)
file.close()