
import fitz
from datetime import datetime

def build_pdf(code, units, fc, fy_plate, fexx, B, L, t_use, d, bf, tf, tw,
              N, Mx, My, Vx, Vy, Vmu, case_id,
              press_dict, t_req, strips, weld_req, anchors_dict):
    doc = fitz.open(); page = doc.new_page(); y = 50
    def text(s, size=10):
        nonlocal y; page.insert_text((40, y), s, fontsize=size); y += size + 6
    text("Base Plate & Anchor Bolts – I2 Prototype"); text(f"Date: {datetime.now():%Y-%m-%d %H:%M}"); text("")
    text("1) Parameters & Materials", 12); text(f"Code: {code} | Units: {units}"); text(f"f'c={fc} MPa, plate fy={fy_plate} MPa, F_EXX≈{fexx} MPa")
    text("2) Geometry"); text(f"Plate: B={B} mm, L={L} mm, t={t_use:.1f} mm  |  Column: d={d} mm, bf={bf} mm")
    text("3) Loads"); text(f"N={N} kN, Mx={Mx} kN·m, My={My} kN·m, Vx={Vx} kN, Vy={Vy} kN, Vμ={Vmu:.1f} kN, CASE={case_id}")
    text("4) Contact pressures (kN/mm²)")
    for k,v in press_dict.items(): text(f"   {k}: {v}")
    text("5) Local method (DG1) – required t"); text(f"t_req={t_req:.1f} mm")
    for s in strips: text(f"   {s.get('strip','strip')}: m_eff={s.get('m_eff_mm',0):.1f} mm, q={s.get('q_kNmm2',0):.5f} kN/mm², t_req={s.get('t_req_mm',0):.1f} mm")
    text("6) Welds (fillet E70XX)"); text(f"Suggested size: w={weld_req:.1f} mm")
    text("7) Anchors")
    for group, data in anchors_dict.items():
        text(f"   {group}:")
        if isinstance(data, dict):
            for k,v in data.items(): text(f"     {k}: {v}")
        else: text(f"     {data}")
    text(""); text("Notes: I2 report (preliminary concrete anchors). Full ACI/EN concrete & shear key in I3.")
    pdf = doc.tobytes(); doc.close(); return pdf
