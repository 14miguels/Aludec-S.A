

# SDS Extraction App Workflow

## Goal
Build a system that automatically extracts structured information from SDS (Safety Data Sheets) PDFs, allows human validation, and stores validated data for later use and export.

---

## Main Workflow

1. Upload PDF
2. Run extraction pipeline (LLM-based)
3. Store extracted data as draft (staging)
4. Display:
   - PDF (left side)
   - Extracted data (right side)
5. Human review and correction
6. Approve data
7. Save to final database
8. Allow export to Excel

---

## Data Flow

### 1. Input
- Raw SDS PDF file

### 2. Processing
- PDF text extraction
- Section splitting
- LLM-based extraction of:
  - Substances
  - Hazards
  - Physical properties
  - Transport info
  - Seveso classification

### 3. Draft Storage (Staging Layer)
Store raw extracted JSON before validation.

Fields:
- id
- file_name
- pdf_path
- extracted_json
- status (`pending_review`, `approved`)
- created_at
- updated_at

---

## Human-in-the-loop Validation

After extraction:
- User reviews extracted data
- Can edit/correct fields
- Compares with original PDF
- Approves when data is correct

---

## Final Storage (Approved Data)

After approval, data is stored in structured format:

### Entities
- Document
- Substance
- Hazard
- PhysicalProperties
- TransportInfo
- SevesoInfo

---

## States

- uploaded
- extracted
- pending_review
- approved
- exported

---

## Output

- Structured database records
- Excel export (based on validated data)

---

## Notes

- LLM extraction is considered MVP and may contain errors
- Human validation is required before final storage
- System should be modular to allow future improvements in extraction accuracy