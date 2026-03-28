from dataclasses import asdict
from pathlib import Path
import json

from src.pipeline.run_pipeline import run_pipeline


PDFS = [
    "001.000204.00 -Thinner-V1.04.pdf",
]

PDFS_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/output")


def process_pdf(pdf_name: str):
    pdf_path = PDFS_DIR / pdf_name

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"\n[START] {pdf_name}")
    doc = run_pipeline(str(pdf_path))
    print(f"\n[DONE] {pdf_name}")
    return pdf_name, doc


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_by_name = {}

    for pdf_name in PDFS:
        try:
            finished_pdf_name, doc = process_pdf(pdf_name)
            results_by_name[finished_pdf_name] = doc
        except Exception as e:
            print(f"[ERROR] Failed to process {pdf_name}: {type(e).__name__}: {e}")

    ordered_results = [results_by_name[pdf_name] for pdf_name in PDFS if pdf_name in results_by_name]

    print("\nAll PDFs processed.")
    print(f"Total documents processed: {len(ordered_results)}")

    output_file = OUTPUT_DIR / "extraction_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([asdict(doc) for doc in ordered_results], f, indent=2, ensure_ascii=False)

    print(f"Results saved to: {output_file}")

    for i, doc in enumerate(ordered_results, start=1):
        file_path = OUTPUT_DIR / f"result_{i}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(asdict(doc), f, indent=2, ensure_ascii=False)