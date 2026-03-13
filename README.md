# Aludec S.A. — PDF Production Data Extractor

A Python tool for automatic extraction of structured production data from technical PDF sheets used in automotive emblem painting processes. Developed as part of an engineering internship at **Aludec S.A.**

---

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Output](#output)
- [Contributing](#contributing)

---

## Project Description

During the automotive emblem painting process at Aludec S.A., technicians work with technical PDF sheets that define the exact paint mixtures, component quantities, and process parameters required for each production order. Manually copying this data into production tracking systems is time-consuming and error-prone.

This tool automates the extraction of key fields from those PDF documents and exports them to a structured Excel file, streamlining the data entry workflow for the production team.

---

## Features

- 📄 **PDF Parsing** — Reads and parses technical PDF sheets used in the emblem painting process.
- 🔍 **Key Field Extraction** — Identifies and extracts fields such as:
  - Paint mixture codes and names
  - Component quantities and ratios
  - Reference numbers and batch identifiers
  - Process parameters (e.g., drying times, layer specifications)
- 📊 **Excel Export** — Exports all extracted data to a structured `.xlsx` file using `openpyxl`/`pandas`.
- ⚙️ **Batch Processing** — Processes multiple PDF files in a single run.
- ✅ **Validation** — Flags incomplete or unrecognised fields for manual review.

---

## Requirements

- Python 3.8 or higher
- The following Python libraries:

| Library | Purpose |
|---|---|
| `pdfplumber` | Extracting text and tables from PDF files |
| `pandas` | Data manipulation and structuring |
| `openpyxl` | Writing output to Excel (`.xlsx`) |
| `re` (stdlib) | Regular expression pattern matching |
| `os` / `pathlib` (stdlib) | File and directory handling |

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/14miguels/Aludec-S.A.git
   cd Aludec-S.A
   ```

2. **Create and activate a virtual environment (recommended):**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Process a single PDF file

```bash
python main.py --input path/to/technical_sheet.pdf --output output/results.xlsx
```

### Process all PDFs in a folder

```bash
python main.py --input path/to/pdf_folder/ --output output/results.xlsx
```

### Command-line arguments

| Argument | Description | Required |
|---|---|---|
| `--input` | Path to a PDF file or a directory of PDF files | ✅ |
| `--output` | Path for the output Excel file (default: `output/results.xlsx`) | ❌ |
| `--verbose` | Print detailed extraction logs to the console | ❌ |

### Example

```bash
python main.py --input data/fichas_tecnicas/ --output resultados/produccion.xlsx --verbose
```

---

## Project Structure

```
Aludec-S.A/
├── data/                   # Input PDF files (not tracked by git)
├── output/                 # Generated Excel files (not tracked by git)
├── src/
│   ├── extractor.py        # PDF parsing and field extraction logic
│   ├── exporter.py         # Excel export using pandas / openpyxl
│   └── utils.py            # Helper functions (validation, logging, etc.)
├── tests/
│   └── test_extractor.py   # Unit tests for extraction logic
├── main.py                 # Entry point — CLI interface
├── requirements.txt        # Python dependencies
└── README.md
```

---

## Output

The tool generates an `.xlsx` file where each row corresponds to one PDF sheet. Typical columns include:

| Column | Description |
|---|---|
| `file_name` | Name of the source PDF file |
| `reference` | Part or order reference number |
| `paint_code` | Paint mixture code |
| `paint_name` | Descriptive name of the paint mixture |
| `component_a_qty` | Quantity of component A |
| `component_b_qty` | Quantity of component B (hardener/catalyst) |
| `thinner_qty` | Quantity of thinner |
| `layer` | Coat layer (primer, base, clearcoat, etc.) |
| `status` | `OK` if all fields were found, `REVIEW` if any field is missing |

---

## Contributing

This project was developed as part of an engineering internship at **Aludec S.A.** Contributions, suggestions, and improvements are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request.
