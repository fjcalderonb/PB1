import fitz
from datetime import datetime

def pdf_header(page, y, title):
    page.insert_text((40,y), title, fontsize=14); y+=22
    page.insert_text((40,y), f"Date: {datetime.now():%Y-%m-%d %H:%M}", fontsize=9); y+=16
    return y

def build_pdf(project: dict, images: dict, tables: dict) -> bytes:
    doc = fitz.open()
    # Page 1
    p = doc.new_page(); y=50
    y = pdf_header(p,y, 'Base Plate & Anchor Bolts – I3 Report (Extended)')
    p.insert_text((40,y), f"Code: {project.get('code','AISC/ACI (US)')} | Units: {project.get('units','SI')}", fontsize=10); y+=14
    p.insert_text((40,y), f"Plate: B={project.get('B',0)} mm, L={project.get('L',0)} mm, t={project.get('t',0):.1f} mm", fontsize=10); y+=14
    p.insert_text((40,y), f"Column: d={project.get('d',0)} mm, bf={project.get('bf',0)} mm", fontsize=10); y+=14
    p.insert_text((40,y), f"Anchors: Ø={project.get('D',0)} mm, hef={project.get('hef',0)} mm, grade={project.get('grade','')}", fontsize=10); y+=20
    img = images.get('plan_png')
    if img:
        rect = fitz.Rect(40,y, 550, y+300)
        p.insert_image(rect, stream=img); y+=320
    p.insert_text((40,y), 'Governing by mechanism:', fontsize=11); y+=14
    for k,v in (tables.get('governing') or {}).items():
        p.insert_text((60,y), f"- {k}: {v}", fontsize=9); y+=12

    # Other pages
    for name, df in (tables.get('sheets') or {}).items():
        p = doc.new_page(); y=50
        y = pdf_header(p,y, name)
        lines = df.to_string(index=False).split('\n')[:45]
        for ln in lines:
            p.insert_text((40,y), ln, fontsize=8); y+=10
            if y>770: p = doc.new_page(); y=50
    out = doc.tobytes(); doc.close(); return out