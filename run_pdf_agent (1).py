from pathlib import Path
import os

from pypdf import PdfReader
from google import genai
from base_agent.prompts import return_instructions_root


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from all pages of a PDF file."""
    reader = PdfReader(pdf_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text() or ""
        text_parts.append(text)

    return "\n".join(text_parts).strip()


def main():
    pdf_file = "Apex_Solutions_Strategic_Vision_2026_FINAL.pdf"

    if not Path(pdf_file).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_file}")

    extracted_text = extract_text_from_pdf(pdf_file)

    instruction = return_instructions_root()

    full_prompt = f"""
{instruction}

Here is the vendor proposal text to analyze:

{extracted_text}
"""

    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "abc-applicants-01"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )

    response = client.models.generate_content(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-pro"),
        contents=full_prompt,
    )

    print("\n===== MODEL OUTPUT =====\n")
    print(response.text)
    print("\n===== END =====\n")


if __name__ == "__main__":
    main()