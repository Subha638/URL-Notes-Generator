from fpdf import FPDF

def create_pdf(notes, faq, mcq, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI-Generated Notes", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, notes)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "FAQs", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, faq)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "MCQs", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, mcq)

    pdf.output(filename)
