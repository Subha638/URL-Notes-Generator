# pdf_utils.py
from fpdf import FPDF
import io
from typing import List, Dict

class PDF(FPDF):
    def header(self):
        # Override to add small header if needed
        self.set_font("Arial", "B", 12)
        self.cell(0, 8, "Study Pack", ln=True, align="C")
        self.ln(4)

def create_pdf_bytes(title: str, url: str, summary: str, bullets: List[str], faqs: List[Dict], mcqs: List[Dict]) -> bytes:
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 6, f"Source: {url}")
    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "Summary", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, summary)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, "Key Points", ln=True)
    pdf.set_font("Arial", size=10)
    for i, b in enumerate(bullets, 1):
        pdf.multi_cell(0, 6, f"{i}. {b}")
    pdf.ln(3)

    if faqs:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, "FAQs", ln=True)
        pdf.set_font("Arial", size=10)
        for i, qa in enumerate(faqs,1):
            q = qa.get("q") or qa.get("question") or ""
            a = qa.get("a") or qa.get("answer") or ""
            pdf.multi_cell(0, 6, f"Q{i}. {q}")
            pdf.multi_cell(0, 6, f"A: {a}")
            pdf.ln(1)

    if mcqs:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, "MCQs", ln=True)
        pdf.set_font("Arial", size=10)
        for i, m in enumerate(mcqs, 1):
            q = m.get("question") or ""
            opts = m.get("options") or []
            ans = m.get("answer") or ""
            pdf.multi_cell(0, 6, f"Q{i}. {q}")
            for idx, o in enumerate(opts, 1):
                pdf.multi_cell(0, 6, f"   {chr(64+idx)}. {o}")
            pdf.multi_cell(0, 6, f"Answer: {ans}")
            pdf.ln(1)

    b = pdf.output(dest="S").encode("latin-1")
    return b
