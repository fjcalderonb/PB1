import streamlit as st
import pandas as pd
from core.models import (InputData, Materials, Concrete, PlateSteel, AnchorSteel, PhiFactors,
                         Geometry, Anchors, AnchorLine, Loads, Method, Options)
from core.pressure import pressure_distribution
from core.anchors import design_anchors
from core.plate import plate_checks
from core.combinations import compute_equiv, pick_worst
from reports.pdf import build_pdf
from reports.pdf_sections import pdf_from_dict

st.set_page_config(page_title="Placa Base AISC/ACI", layout="wide")
st.title("Placa Base — AISC/ACI")

# ---------- Sidebar: Materiales/Geometría/Cargas (igual que versión anterior) ----------
with st.sidebar:
    st.header("Materiales")
    fc = st.number_input("f'c (MPa)", 10.0, 70.0, 31.0, 0.5)
    fy_plate = st.number_input("fy placa (MPa)", 200.0, 500.0, 235.0, 5.0)
    grade = st.selectbox("Grado anclaje (F1554)", ["F1554-36","F1554-55","F1554-105"])
    if grade == "F1554-36":
        fu_anchor, fy_anchor = 400.0, 250.0
    elif grade == "F1554-55":
        fu_anchor, fy_anchor = 620.0, 380.0
    else:
        fu_anchor, fy_anchor = 860.0, 720.0

    st.header("Placa")
    a = st.number_input("a (mm)", 200.0, 3000.0, 1054.0, 1.0)
    b = st.number_input("b (mm)", 200.0, 3000.0, 800.0, 1.0)
    tp = st.number_input("tp (mm)", 8.0, 150.0, 76.0, 1.0)

    st.header("Anclajes (línea 1)")
    diam_in = st.selectbox("Diámetro (pulgadas)", ["1/2","5/8","3/4","7/8","1","1-1/8","1-1/4"])
    DIAM_TO_MM = {"1/2":12.7,"5/8":15.875,"3/4":19.05,"7/8":22.225,"1":25.4,"1-1/8":28.575,"1-1/4":31.75}
    d_mm = DIAM_TO_MM[diam_in]
    n_bolts = st.number_input("N° de pernos (línea 1)", 2, 16, 4, 1)
    g1 = st.number_input("g1 (mm, borde→perno)", 20.0, 400.0, 114.0, 1.0)
    v1 = st.number_input("v1 (mm, margen lateral)", 20.0, 600.0, 241.5, 0.5)
    resist_shear = st.checkbox("Anclajes resisten cortante", value=False)

    st.header("Cargas")
    N = st.number_input("N (kN) (compresión + / tracción -)", -5000.0, 5000.0, -1454.627, 1.0)
    Mx = st.number_input("Mx (kN·m)", -5000.0, 5000.0, 1981.823, 0.1)
    Vx = st.number_input("Vx (kN)", -2000.0, 2000.0, -102.319, 0.1)

    st.header("Métodos")
    case = st.selectbox("Caso de presiones", ["CASE_1","CASE_2","CASE_3","CASE_4"])
    plate_method = st.selectbox("Método placa", ["ROARK","ELASTIC","PLASTIC"])

materials = Materials(
    concrete=Concrete(fc_MPa=fc),
    plate=PlateSteel(fy_MPa=fy_plate),
    anchors=AnchorSteel(grade=grade, fu_MPa=fu_anchor, fy_MPa=fy_anchor),
    phi=PhiFactors()
)
geom = Geometry(a_mm=a, b_mm=b, tp_mm=tp, g1_mm=g1, v1_mm=v1)
anchors = Anchors(lines=[AnchorLine(index=1, n_bolts=int(n_bolts), edge_dist_mm=g1, bolt_d_mm=d_mm)],
                  resist_shear=resist_shear)
loads = Loads(N_kN=N, Mx_kNm=Mx, Vx_kN=Vx)
method = Method(pressure_case=case, plate_method=plate_method)
data = InputData(materials=materials, geometry=geom, anchors=anchors, loads=loads, method=method)

tab_main, tab_comb, tab_pdf = st.tabs(["Diseño/Checks", "Combinaciones", "Reportes"])

with tab_main:
    st.subheader("Resultados")
    press = pressure_distribution(data)

    # reparto simple de esfuerzos a perno (placeholder)
    # 2ª iteración: calc exacto de Z por línea/perno con palanca y patrón
    tension_per_bolt = max(0.0, (abs(N)/max(n_bolts,1)))  # placeholder
    shear_per_bolt   = abs(Vx)/max(n_bolts,1) if resist_shear else 0.0
    anch = design_anchors(data, tension_per_bolt_N=tension_per_bolt, shear_per_bolt_N=shear_per_bolt)

    plate = plate_checks(data, q_max_Pa=press.get("sigma_max_MPa",0.0)*1e6)

    c1, c2 = st.columns(2)
    with c1:
        st.write("### Presiones")
        st.json(press)
        st.write("### Placa")
        st.json(plate)
    with c2:
        st.write("### Anclajes (acero)")
        st.json(anch)

with tab_comb:
    st.write("### Cargar combinaciones (CSV/Excel)")
    up = st.file_uploader("Sube CSV/XLSX con columnas: N, Mx, My, Vx, Vy, d1, d2, n1, n2, Condition", type=["csv","xlsx"])
    if up:
        df = pd.read_excel(up) if up.name.endswith(".xlsx") else pd.read_csv(up)
        df = compute_equiv(df)
        st.dataframe(df.head(50), use_container_width=True)

        disc = st.selectbox("Disciplina", ["Concreto","Pernos","Placa"])
        if st.button("Usar peor caso en el Diseñador"):
            row = pick_worst(df, disc)
            # volcamos fuerzas básicas al diseñador (lo simple para esta iteración)
            loads.N_kN = float(row["N"])
            loads.Mx_kNm = float(row.get("Mequiv", row["Mx"]))
            loads.Vx_kN = float(row.get("Vequiv", row["Vx"]))
            st.success(f"Se cargó la combinación {disc}: N={loads.N_kN}, Mx={loads.Mx_kNm}, Vx={loads.Vx_kN}")

with tab_pdf:
    st.write("### Reportes por disciplina")
    if st.button("PDF — Concreto"):
        pdf = pdf_from_dict("Concreto", {"Presiones":pressure_distribution(data)})
        st.download_button("Descargar RESULTS_CONCRETE.pdf", pdf, "RESULTS_CONCRETE.pdf")
    if st.button("PDF — Pernos"):
        pdf = pdf_from_dict("Pernos", {"Anclajes acero":design_anchors(data, tension_per_bolt, shear_per_bolt)})
        st.download_button("Descargar RESULTS_BOLTS.pdf", pdf, "RESULTS_BOLTS.pdf")
    if st.button("PDF — Placa"):
        pdf = pdf_from_dict("Placa", {"Placa":plate_checks(data, 0.0)})
        st.download_button("Descargar RESULTS_BASEPLATE.pdf", pdf, "RESULTS_BASEPLATE.pdf")
