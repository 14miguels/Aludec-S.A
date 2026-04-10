import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple

from src.pipeline.run_pipeline import run_pipeline
from src.db.db import init_db, save_extraction

logger = logging.getLogger(__name__)


def get_cli_arguments() -> argparse.Namespace:
    """Build and parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Extract SDS data from a PDF file or all PDFs in a folder."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to a PDF file or a directory containing PDF files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/output/extraction_results.json",
        help="Path of the aggregated JSON output file.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed logging for pipeline progress.",
    )
    return parser.parse_args()


def collect_pdf_paths(target: Path) -> List[Path]:
    """Return a sorted list of PDF files from the provided target path."""
    if not target.exists():
        raise ValueError(f"Input path does not exist: {target}")

    if target.is_file():
        if target.suffix.lower() != ".pdf":
            raise ValueError(f"Input file must have .pdf extension: {target}")
        return [target]

    if target.is_dir():
        pdfs = sorted(p for p in target.glob("*.pdf") if p.is_file())
        if not pdfs:
            raise ValueError(f"No PDF files were found inside: {target}")
        return pdfs

    raise ValueError(f"Unsupported input path type: {target}")


def main() -> int:
    args = get_cli_arguments()
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
    )
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    init_db()

    try:
        pdf_paths = collect_pdf_paths(Path(args.input))
    except ValueError as exc:
        logger.error(exc)
        return 1

    logger.info("Found %d PDF(s) to process.", len(pdf_paths))
    aggregated_results: List[dict] = []
    failures: List[Tuple[str, str]] = []

    for pdf in pdf_paths:
        logger.info("Running pipeline for: %s", pdf.name)
        try:
            sds_document = run_pipeline(pdf)

            save_extraction(file_name=pdf.name, pdf_path=str(pdf), extracted_json=asdict(sds_document))
            
            aggregated_results.append(asdict(sds_document))
        except Exception as exc:
            failures.append((pdf.name, str(exc)))
            logger.exception("Failed to process %s", pdf.name)

    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    # TODO: integrate Excel export via src/export/ when available.
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(aggregated_results, file, indent=4, ensure_ascii=False)

    processed = len(pdf_paths)
    succeeded = processed - len(failures)
    print(f"Processed {processed} PDF(s): {succeeded} succeeded, {len(failures)} failed.")
    print(f"Saved aggregated results to {output_file}")

    if failures:
        print("Failed files:")
        for name, reason in failures:
            print(f" - {name}: {reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
