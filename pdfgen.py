# pdfgen.py
from fpdf import FPDF
import io
import textwrap
from typing import Dict

def create_pdf_bytes(title: str, source_url: str, notes: Dict) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=title, ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 6, txt=f"Source: {source_url}", ln=True)
    pdf.ln(4)
    # summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Summary", ln=True)
    pdf.set_font("Arial", size=11)
    for line in textwrap.wrap(notes.get("summary", ""), 90):
        pdf.multi_cell(0, 6, line)
    pdf.ln(3)
    # bullets
    if notes.get("bullets"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Key points", ln=True)
        pdf.set_font("Arial", size=11)
        for b in notes["bullets"]:
            for line in textwrap.wrap(b, 85):
                pdf.multi_cell(0, 6, "- " + line)
        pdf.ln(3)
    # concepts
    if notes.get("concepts"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Key concepts", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, ", ".join(notes["concepts"]))
        pdf.ln(3)
    # Add small Q&A section
    if notes.get("qas"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Q&A (Study)", ln=True)
        pdf.set_font("Arial", size=11)
        for i, qa in enumerate(notes["qas"], 1):
            pdf.multi_cell(0, 6, f"Q{i}. {qa['q']}")
            pdf.multi_cell(0, 6, f"A: {qa['a']}")
            pdf.ln(1)
    # return bytes
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
