import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def _page_header(c, title):
    w,h = A4
    y = h - 40
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
            c.showPage()
            y = _page_header(c, title)
            c.setFont("Helvetica", 9)
    c.showPage(); c.save()
    return buffer.getvalue()
