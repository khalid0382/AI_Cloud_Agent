"""
main_pipeline.py — Local test runner
=====================================
Run this directly to test the full pipeline locally without deploying.

Usage:
    python main_pipeline.py

It reads the PDF with pypdf (local only), then delegates all Gemini calls,
DOCX generation, and GCS upload to pipeline.py — the same code the agent uses.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from base_agent.pipeline import process_proposal_text

load_dotenv()

PDF_FILE = "Apex_Solutions_Strategic_Vision_2026_FINAL.pdf"


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract plain text from a local PDF using pypdf."""
    reader = PdfReader(pdf_path)
    return "\n".join(
        (page.extract_text() or "") for page in reader.pages
    ).strip()


def main():
    if not Path(PDF_FILE).exists():
        raise FileNotFoundError(f"PDF not found: {PDF_FILE}")

    print("Reading PDF...")
    proposal_text = extract_text_from_pdf(PDF_FILE)

    if not proposal_text.strip():
        raise ValueError("PDF text extraction returned empty string.")

    print(f"Extracted {len(proposal_text)} chars from PDF.")
    print("Running compliance pipeline (Gemini extraction + DOCX + GCS upload)...")

    result = process_proposal_text(proposal_text)

    print(f"\nCertificate saved: {result['certificate_file']}")
    print(f"GCS URI:           {result['certificate_gcs_uri']}")
    print(f"Browser URL:       {result['certificate_browser_url']}")
    print("\nCompliance result:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
