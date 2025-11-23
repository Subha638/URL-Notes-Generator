from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# Register a Unicode font (No unicode errors anymore)
pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))

def create_pdf_bytes(title, summary, notes, faqs, mcqs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Plain",
            fontName="DejaVu",
            fontSize=11,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading",
            fontName="DejaVu",
            fontSize=16,
            leading=18,
            spaceAfter=12,
            bold=True,
        )
    )

    content = []

    # Title
    content.append(Paragraph(title, styles["Heading"]))
    content.append(Spacer(1, 0.2 * inch))

    # Summary
    content.append(Paragraph("<b>Summary</b>", styles["Heading"]))
    content.append(Paragraph(summary.replace("\n", "<br/>"), styles["Plain"]))
    content.append(Spacer(1, 0.2 * inch))

    # Notes
    content.append(Paragraph("<b>Key Notes</b>", styles["Heading"]))
    content.append(Paragraph(notes.replace("\n", "<br/>"), styles["Plain"]))
    content.append(Spacer(1, 0.2 * inch))

    # FAQs
    content.append(Paragraph("<b>FAQs</b>", styles["Heading"]))
    content.append(Paragraph(faqs.replace("\n", "<br/>"), styles["Plain"]))
    content.append(Spacer(1, 0.2 * inch))

    # MCQs
    content.append(Paragraph("<b>MCQs</b>", styles["Heading"]))
    content.append(Paragraph(mcqs.replace("\n", "<br/>"), styles["Plain"]))
    content.append(Spacer(1, 0.2 * inch))

    doc.build(content)

    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
