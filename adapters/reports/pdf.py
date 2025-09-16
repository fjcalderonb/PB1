
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def _header(c, title):
    w,h = A4; y = h-50
    c.setFont("Helvetica-Bold", 15)
    c.drawString(40, y, title)
    return y-18

def build_report(title: str, sections: list[tuple[str, dict]]):
    buf = BytesIO(); c = canvas.Canvas(buf, pagesize=A4)
    y = _header(c, title)
    c.setFont("Helvetica", 10)
    c.drawString(40, y, "Design code: AMERICAN (AISC/ACI) — Units: SI — Shear path: friction")
    c.showPage()
    for sec_title, data in sections:
        y = _header(c, sec_title); c.setFont("Helvetica", 9)
        for k,v in data.items():
            c.drawString(40, y, f"{k}: {v}"); y -= 12
            if y < 60: c.showPage(); y = _header(c, sec_title); c.setFont("Helvetica", 9)
        c.showPage()
    y = _header(c, "References"); c.setFont("Helvetica", 9)
    for r in ["AISC DG1 (2024)", "ACI 318-19/22 Ch.17"]:
        c.drawString(40, y, "• "+r); y -= 12
    c.showPage(); c.save(); return buf.getvalue()
