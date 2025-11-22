# pdfgen.py (REPLACE your old file with this)
from fpdf import FPDF
import io
import textwrap
from typing import Dict

def _safe_write_multi(pdf: FPDF, text: str, width: int = 90, line_height: float = 6):
    """Wrap text and write using multi_cell to avoid very long lines."""
    if not text:
        return
    for line in textwrap.wrap(text, width):
        pdf.multi_cell(0, line_height, line)

def create_pdf_bytes(title: str, source_url: str, notes: Dict) -> bytes:
    """
    Create a PDF from the notes dict and return raw bytes.
    Works across fpdf versions:
      - preferred: pdf.output(dest='S') -> str (then encode)
      - fallback: pdf.output_bytes() -> bytes (fpdf2)
    Encodes non-Latin characters safely by replacing unsupported characters.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=(title or "Document"), ln=True)
    pdf.ln(1)

    # Source
    pdf.set_font("Arial", size=9)
    safe_url = source_url or ""
    pdf.multi_cell(0, 6, txt=f"Source: {safe_url}")
    pdf.ln(3)

    # Summary
    summary = notes.get("summary", "")
    if summary:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Summary", ln=True)
        pdf.set_font("Arial", size=11)
        _safe_write_multi(pdf, summary, width=95, line_height=6)
        pdf.ln(2)

    # Bullets / Key points
    bullets = notes.get("bullets", []) or []
    if bullets:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Key points", ln=True)
        pdf.set_font("Arial", size=11)
        for b in bullets:
            # prefix dash and wrap
            wrapped = textwrap.wrap(b, 85)
            if not wrapped:
                pdf.multi_cell(0, 6, "-")
            else:
                for i, line in enumerate(wrapped):
                    prefix = "- " if i == 0 else "  "
                    pdf.multi_cell(0, 6, prefix + line)
        pdf.ln(3)

    # Concepts
    concepts = notes.get("concepts", []) or []
    if concepts:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Key concepts", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, ", ".join(concepts))
        pdf.ln(3)

    # Definitions
    definitions = notes.get("definitions", []) or []
    if definitions:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Definitions", ln=True)
        pdf.set_font("Arial", size=11)
        for d in definitions:
            term = d.get("term") if isinstance(d, dict) else None
            definition = d.get("definition") if isinstance(d, dict) else None
            if term and definition:
                pdf.multi_cell(0, 6, f"{term}: {definition}")
            else:
                # fallback if definitions are plain strings
                pdf.multi_cell(0, 6, str(d))
        pdf.ln(3)

    # Q&A
    qas = notes.get("qas", []) or []
    if qas:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Q&A (Study)", ln=True)
        pdf.set_font("Arial", size=11)
        for i, qa in enumerate(qas, 1):
            q_text = qa.get("q") if isinstance(qa, dict) else str(qa)
            a_text = qa.get("a") if isinstance(qa, dict) else ""
            pdf.multi_cell(0, 6, f"Q{i}. {q_text}")
            _safe_write_multi(pdf, f"A: {a_text}", width=95, line_height=6)
            pdf.ln(1)

    # MCQs (optional)
    mcqs = notes.get("mcqs", []) or []
    if mcqs:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "MCQs", ln=True)
        pdf.set_font("Arial", size=11)
        for i, m in enumerate(mcqs, 1):
            stem = m.get("stem", "")
            options = m.get("options", []) if isinstance(m.get("options", []), list) else []
            answer = m.get("answer", "")
            pdf.multi_cell(0, 6, f"Q{i}. {stem}")
            for idx, opt in enumerate(options, 1):
                pdf.multi_cell(0, 6, f"   {idx}. {opt}")
            if answer:
                pdf.multi_cell(0, 6, f"Answer: {answer}")
            pdf.ln(1)

    # Flashcards (optional)
    flashcards = notes.get("flashcards", []) or []
    if flashcards:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, "Flashcards", ln=True)
        pdf.set_font("Arial", size=11)
        for i, f in enumerate(flashcards, 1):
            front = f.get("front", "") if isinstance(f, dict) else str(f)
            back = f.get("back", "") if isinstance(f, dict) else ""
            pdf.multi_cell(0, 6, f"Card {i}: {front}")
            _safe_write_multi(pdf, f"→ {back}", width=95, line_height=6)
            pdf.ln(1)

    # Finalize: return bytes (work across fpdf versions)
    try:
        # Most common approach: return as string then encode to bytes
        output_str = pdf.output(dest='S')  # returns str in many fpdf versions
        if isinstance(output_str, str):
            pdf_bytes = output_str.encode('latin-1', errors='replace')
        else:
            # sometimes returns bytes directly
            pdf_bytes = bytes(output_str)
        return pdf_bytes
    except TypeError:
        # older/newer variants: try output_bytes() (fpdf2)
        try:
            pdf_bytes = pdf.output_bytes()
            return pdf_bytes
        except Exception:
            # as last resort, write to BytesIO
            buf = io.BytesIO()
            pdf.output(buf)
            return buf.getvalue()
