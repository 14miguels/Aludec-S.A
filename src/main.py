from src.pipeline.run_pipeline import run_pipeline

if __name__ == "__main__":
    substances = run_pipeline("data/raw_pdfs/ACRYTHANE THINNER S-9600_ESP-ES.pdf")

    print("\n[RESULT] Extracted substances:\n")

    if not substances:
        print("No substances found.")
    else:
        for i, sub in enumerate(substances, 1):
            print(f"--- Substance {i} ---")
            print(f"Name: {sub.name}")
            print(f"CAS: {sub.cas_number}")
            print(f"Percentage: {sub.percentage}\n")