from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def _header(c, title):
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 15)
    c.drawString(40, y, title)
    return y - 18


def build_report(title: str, sections: list[tuple[str, dict]]):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Cover
    y = _header(c, title)
    c.setFont("Helvetica", 10)
    c.drawString(40, y, "Design code: AMERICAN (AISC/ACI) — Units: SI — Shear path: friction by default")
    c.showPage()

    # Sections
    for sec_title, data in sections:
        y = _header(c, sec_title)
        c.setFont("Helvetica", 9)
        for k, v in data.items():
            c.drawString(40, y, f"{k}: {v}")
            y -= 12
            if y < 60:
                c.showPage()
                y = _header(c, sec_title)
                c.setFont("Helvetica", 9)
        c.showPage()

    # References
    y = _header(c, "References")
    refs = [
        "AISC Design Guide 1: Base Connection Design for Steel Structures, 3rd ed. (2024)",
        "ACI 318-19/22 — Chapter 17 (Anchorage to Concrete)",
    ]
    c.setFont("Helvetica", 9)
    for r in refs:
        c.drawString(40, y, f"• {r}")
        y -= 12
    c.showPage()
    c.save()
    return buf.getvalue()