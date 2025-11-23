from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 50

    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(40, y, line)
        y -= 18

    c.save()
