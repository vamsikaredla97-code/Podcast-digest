"""
PDF generation for transcripts and full articles.
Saves PDFs to ./pdfs/ and returns the file path.
"""
import os
import re
from pathlib import Path
from fpdf import FPDF

PDF_DIR = Path(__file__).parent / "pdfs"
PDF_DIR.mkdir(exist_ok=True)


def _sanitise_filename(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name)[:80]


def _add_text_to_pdf(pdf: FPDF, text: str) -> None:
    for line in text.split("\n"):
        pdf.multi_cell(0, 6, line)


def generate_pdf(title: str, content: str, source_name: str) -> str:
    """
    Create a PDF from content text.

    Returns the absolute path to the generated PDF file.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)

    # Source
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.cell(0, 6, f"Source: {source_name}", ln=True)
    pdf.ln(6)

    # Body
    pdf.set_font("Helvetica", size=10)
    _add_text_to_pdf(pdf, content)

    filename = f"{_sanitise_filename(source_name)}_{_sanitise_filename(title)}.pdf"
    out_path = PDF_DIR / filename
    pdf.output(str(out_path))
    return str(out_path)
