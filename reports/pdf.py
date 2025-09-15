import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build_pdf(data, press, anchors_res, plate_res):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w,h = A4

    y = h-40
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40,y, "Reporte — Placa Base (MVP)")
    y -= 20
    c.setFont("Helvetica", 9)
    c.drawString(40,y, "Entradas principales:")
    y -= 14

    for k,v in {
        "f'c (MPa)": data.materials.concrete.fc_MPa,
        "fy placa (MPa)": data.materials.plate.fy_MPa,
        "a x b (mm)": f"{data.geometry.a_mm} x {data.geometry.b_mm}",
        "tp (mm)": data.geometry.tp_mm,
        "N (kN)": data.loads.N_kN,
        "Mx (kN·m)": data.loads.Mx_kNm
    }.items():
        c.drawString(50,y, f"- {k}: {v}")
        y -= 12

    y -= 6
    c.setFont("Helvetica-Bold", 10); c.drawString(40,y, "Presiones")
    y -= 14; c.setFont("Helvetica", 9)
    for k,v in press.items():
        c.drawString(50,y, f"{k}: {v}")
        y -= 12

    y -= 6
    c.setFont("Helvetica-Bold", 10); c.drawString(40,y, "Anclajes (resumen)")
    y -= 14; c.setFont("Helvetica", 9)
    for k,v in anchors_res.items():
        c.drawString(50,y, f"{k}: {v}")
        y -= 12

    y -= 6
    c.setFont("Helvetica-Bold", 10); c.drawString(40,y, "Placa (resumen)")
    y -= 14; c.setFont("Helvetica", 9)
    for k,v in plate_res.items():
        c.drawString(50,y, f"{k}: {v}")
        y -= 12

    c.showPage(); c.save()
    pdf = buffer.getvalue(); buffer.close()
    return pdf
