
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def _page_header(c, title):
    w,h = A4
    y = h-40
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40,y, title)
    return y-20

def pdf_from_dict(title: str, data: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = _page_header(c, title)
    c.setFont("Helvetica", 9)
    for k,v in data.items():
        c.drawString(40,y, f"- {k}: {v}")
        y -= 12
        if y < 60:
            c.showPage(); y = _page_header(c, title); c.setFont("Helvetica", 9)
    c.showPage(); c.save()
    return buffer.getvalue()

# reports/pdf_sections.py  (añadir al final de pdf_from_dict)
def _draw_references(c, y):
    refs = [
        "AISC Design Guide 1: Base Connection Design for Steel Structures, 3rd ed. (2024).",
        "ACI 318-19/22: Building Code Requirements for Structural Concrete – Chapter 17 (Anchorage).",
    ]
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "References")
    y -= 14
    c.setFont("Helvetica", 9)
    for r in refs:
        c.drawString(50, y, f"• {r}")
        y -= 12
        if y < 60:
            c.showPage(); y = A4[1]-40; c.setFont("Helvetica", 9)
    return y

