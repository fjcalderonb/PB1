
import streamlit as st
import pandas as pd
from core.models import (InputData, Materials, Concrete, PlateSteel, AnchorSteel, PhiFactors,
                         Geometry, Loads, Method, Options, ColumnFootprint, Pedestal, AnchorageConfig)
from core.pressure import pressure_distribution
from core.anchors_steel import design_anchors_steel
from core.anchors_concrete import design_anchors_concrete_stub
from core.evaluator import worst_by_discipline
from core.sap_import import read_sap_joint_reactions
from reports.pdf import build_pdf
from reports.pdf_sections import pdf_from_dict

st.set_page_config(page_title="Base Plate AISC/ACI", layout="wide")
st.title("Base Plate — AISC / ACI")

with st.sidebar:
    st.header("Materials")
    fc = st.number_input("f'c (MPa)", 10.0, 70.0, 31.0, 0.5)
    fy_plate = st.number_input("fy plate (MPa)", 200.0, 500.0, 235.0, 5.0)
    grade = st.selectbox("Anchor grade (F1554)", ["F1554-36","F1554-55","F1554-105"])
    if grade == "F1554-36": fu_anchor, fy_anchor = 400.0, 250.0
    elif grade == "F1554-55": fu_anchor, fy_anchor = 620.0, 380.0
    else: fu_anchor, fy_anchor = 860.0, 720.0

    st.header("Plate")
    a = st.number_input("plate a (mm)", 200.0, 3000.0, 1054.0, 1.0)
    b = st.number_input("plate b (mm)", 200.0, 3000.0, 800.0, 1.0)
    tp = st.number_input("plate thickness tp (mm)", 8.0, 150.0, 76.0, 1.0)

    st.subheader("Column footprint (mm)")
    b_col = st.number_input("b_col (mm)", 100.0, 2000.0, 300.0, 1.0)
    h_col = st.number_input("h_col (mm)", 100.0, 2000.0, 300.0, 1.0)

    st.subheader("Pedestal / Plinth")
    use_ped = st.checkbox("Use pedestal (plinth)?", value=False)
    Bp = st.number_input("Pedestal width Bp (mm)", 0.0, 10000.0, 0.0, 1.0)
    Lp = st.number_input("Pedestal length Lp (mm)", 0.0, 10000.0, 0.0, 1.0)
    a2a1_manual = st.number_input("A2/A1 override (optional)", 0.0, 20.0, 0.0, 0.1)
    a2a1_override = a2a1_manual if a2a1_manual>0 else None

    st.header("Anchorage & Concrete")
    n_rows = st.number_input("# rows", 1, 10, 2)
    n_cols = st.number_input("# cols", 1, 10, 2)
    s_x = st.number_input("s_x (mm)", 50.0, 2000.0, 200.0, 1.0)
    s_y = st.number_input("s_y (mm)", 50.0, 2000.0, 200.0, 1.0)
    hef = st.number_input("hef (mm)", 50.0, 2000.0, 300.0, 1.0)
    conc_thk = st.number_input("concrete thickness (mm)", 50.0, 5000.0, 500.0, 1.0)
    cracked = st.checkbox("Cracked concrete?", value=True)
    a_type = st.selectbox("Anchor type", ["headed","hooked"])
    st.caption("Edge distances to plate edges (mm)")
    c_xl = st.number_input("c_x_left (mm)", 0.0, 1000.0, 100.0, 1.0)
    c_xr = st.number_input("c_x_right (mm)", 0.0, 1000.0, 100.0, 1.0)
    c_yt = st.number_input("c_y_top (mm)", 0.0, 1000.0, 100.0, 1.0)
    c_yb = st.number_input("c_y_bottom (mm)", 0.0, 1000.0, 100.0, 1.0)

    st.header("Shear path")
    resist_shear = st.checkbox("Anchors resist shear", value=False)
    mu_fric = st.number_input("Friction μ (plate–grout/concrete)", 0.0, 1.0, 0.30, 0.01)

    st.header("Manual quick loads")
    N = st.number_input("N (kN) (compression + / tension -)", -5000.0, 5000.0, 200.0, 1.0)
    Mx = st.number_input("Mx (kN·m)", -5000.0, 5000.0, 50.0, 0.1)
    Vx = st.number_input("Vx (kN)", -2000.0, 2000.0, 20.0, 0.1)

    st.header("Methods")
    case = st.selectbox("Pressure case", ["CASE_1","CASE_2","CASE_3","CASE_4"])
    plate_method = st.selectbox("Plate method", ["ROARK","ELASTIC","PLASTIC"])

materials = Materials(
    concrete=Concrete(fc_MPa=fc),
    plate=PlateSteel(fy_MPa=fy_plate),
    anchors=AnchorSteel(grade=grade, fu_MPa=fu_anchor, fy_MPa=fy_anchor),
    phi=PhiFactors()
)
geom = Geometry(a_mm=a, b_mm=b, tp_mm=tp)
column = ColumnFootprint(b_col_mm=b_col, h_col_mm=h_col)
pedestal = Pedestal(use=use_ped, Bp_mm=Bp, Lp_mm=Lp, a2a1_override=a2a1_override)
anchorage = AnchorageConfig(n_rows=int(n_rows), n_cols=int(n_cols), s_x_mm=s_x, s_y_mm=s_y,
                            hef_mm=hef, conc_thk_mm=conc_thk, cracked=cracked, anchor_type=a_type,
                            c_x_left_mm=c_xl, c_x_right_mm=c_xr, c_y_top_mm=c_yt, c_y_bottom_mm=c_yb)
loads = Loads(N_kN=N, Mx_kNm=Mx, Vx_kN=Vx)
method = Method(pressure_case=case, plate_method=plate_method)
data = InputData(materials=materials, geometry=geom, loads=loads, method=method,
                 column=column, pedestal=pedestal, anchorage=anchorage)


# ---------- Tabs ----------
tab_main, tab_sap, tab_pdf = st.tabs(["Design/Checks", "Combinations (SAP2000)", "Reports"])

with tab_main:
    st.subheader("Results (from manual sidebar loads)")
    press = pressure_distribution(data)

    # Shear split
    V_req = abs(loads.Vx_kN)
    Nc = max(0.0, loads.N_kN)
    Cf = mu_fric * Nc if not resist_shear else 0.0
    V_to_bolts = max(0.0, V_req - Cf) if not resist_shear else V_req

    n_bolts = anchorage.n_rows * anchorage.n_cols
    tpb = max(0.0, loads.N_kN*1e3)/max(1,n_bolts)
    spb = (V_to_bolts*1e3)/max(1,n_bolts)

    steel = design_anchors_steel(data, tpb, spb)
    conc  = design_anchors_concrete_stub(data, tpb, spb)

    c1, c2 = st.columns(2)
    with c1:
        st.write("### Concrete — Bearing/pressure")
        st.json(press)
        st.write("### Anchors (Concrete — stub)")
        st.json(conc)
    with c2:
        st.write("### Shear path")
        st.write({"mu": mu_fric, "Nc_kN": Nc, "Cf_kN": Cf, "V_to_bolts_kN": V_to_bolts})
        st.write("### Anchors (Steel)")
        st.json(steel)

with tab_sap:
    st.write("### Import SAP2000 — Joint Reactions (XLSX/CSV)")
    sapfile = st.file_uploader("File exported from SAP2000 (TABLE: Joint Reactions)", type=["xlsx","csv"])

    if sapfile:
        from core.sap_import import read_sap_joint_reactions
        df = read_sap_joint_reactions(sapfile)
        st.caption(f"Rows read: {len(df)} — Joints sample: {sorted(df['Joint'].dropna().astype(int).unique().tolist())[:10]} ...")

        # Axis mapper
        st.write("#### Axis and sign mapper")
        preset = st.radio("Preset", ["Preset A (default)", "Preset B (swap 1↔2)", "Advanced"], horizontal=True)
        def mapping_from_preset(p):
            if p.startswith("Preset A"): return {"N":"F3", "Vx":"F1", "Vy":"F2", "Mx":"M2", "My":"M1"}
            if p.startswith("Preset B"): return {"N":"F3", "Vx":"F2", "Vy":"F1", "Mx":"M1", "My":"M2"}
            return {"N":"F3", "Vx":"F1", "Vy":"F2", "Mx":"M2", "My":"M1"}
        mapping = mapping_from_preset(preset)
        flips = {k: False for k in ["N","Vx","Vy","Mx","My"]}
        if preset == "Advanced":
            st.info("Advanced: choose any source column and optionally flip its sign.")
            cols = [c for c in ["F1","F2","F3","M1","M2","M3"] if c in df.columns]
            c1,c2,c3,c4,c5 = st.columns(5)
            mapping["N"]  = c1.selectbox("N ←", cols, index=cols.index(mapping["N"]))
            mapping["Vx"] = c2.selectbox("Vx ←", cols, index=cols.index(mapping["Vx"]))
            mapping["Vy"] = c3.selectbox("Vy ←", cols, index=cols.index(mapping["Vy"]))
            mapping["Mx"] = c4.selectbox("Mx ←", cols, index=cols.index(mapping["Mx"]))
            mapping["My"] = c5.selectbox("My ←", cols, index=cols.index(mapping["My"]))
            d1,d2,d3,d4,d5 = st.columns(5)
            flips["N"]  = d1.checkbox("Flip N",  value=False)
            flips["Vx"] = d2.checkbox("Flip Vx", value=False)
            flips["Vy"] = d3.checkbox("Flip Vy", value=False)
            flips["Mx"] = d4.checkbox("Flip Mx", value=False)
            flips["My"] = d5.checkbox("Flip My", value=False)
        else:
            st.caption(f"Using preset: {mapping}")

        def apply_mapping(dfin, mapping, flips):
            out = pd.DataFrame({
                'Joint': dfin['Joint'], 'OutputCase': dfin['OutputCase'],
                'N_kN':  dfin[mapping['N']]  * (-1 if flips.get('N') else 1),
                'Vx_kN': dfin[mapping['Vx']] * (-1 if flips.get('Vx') else 1),
                'Vy_kN': dfin[mapping['Vy']] * (-1 if flips.get('Vy') else 1),
                'Mx_kNm': dfin[mapping['Mx']] * (-1 if flips.get('Mx') else 1),
                'My_kNm': dfin[mapping['My']] * (-1 if flips.get('My') else 1),
            })
            mask = out[['N_kN','Vx_kN','Vy_kN','Mx_kNm','My_kNm']].notna().any(axis=1)
            return out.loc[mask].reset_index(drop=True)

        df_std = apply_mapping(df, mapping, flips)
        st.dataframe(df_std.head(25), use_container_width=True)

        with st.spinner("Evaluating worst cases per discipline..."):
            worst = worst_by_discipline(df_std, data, mu_fric, resist_shear, anchorage.n_rows*anchorage.n_cols, 25.4)

        def show_worst(label: str, key: str, wr: dict):
            st.write(f"### {label} — Worst case")
            if wr is None:
                st.warning("No rows to evaluate.")
                return
            meta = wr['meta']
            st.write(f"Joint {meta['Joint']} | Case: {meta['OutputCase']}")
            st.json({**wr['loads'], **wr[key]})
            if st.button(f"Push to Designer ({label})", key=f"btn_insert_{key}"):
                loads.N_kN  = wr['loads']['N_kN']
                loads.Mx_kNm= wr['loads']['Mx_kNm']
                loads.Vx_kN = wr['loads']['Vx_kN']
                st.success(f"Loaded {label}: Joint {meta['Joint']} — {meta['OutputCase']}")

        c1, c2, c3 = st.columns(3)
        with c1: show_worst("Concrete", 'concrete', worst['concrete'])
        with c2: show_worst("Anchors",  'anchors',  worst['anchors'])
        with c3: show_worst("Plate",    'plate',    worst['plate'])

with tab_pdf:
    st.write("### Discipline reports")
    if st.button("PDF — Concrete (current)"):
        pdf = pdf_from_dict("Concrete", {"Pressures": pressure_distribution(data)})
        st.download_button("Download RESULTS_CONCRETE.pdf", pdf, "RESULTS_CONCRETE.pdf")
    if st.button("PDF — Anchors (steel, current)"):
        V_req = abs(loads.Vx_kN); Nc = max(0.0, loads.N_kN)
        Cf = mu_fric * Nc if not anchorage else (mu_fric * Nc if not resist_shear else 0.0)
        V_to_bolts = max(0.0, V_req - Cf) if not resist_shear else V_req
        n_b = max(1, anchorage.n_rows*anchorage.n_cols)
        tpb = max(0.0, loads.N_kN*1e3)/n_b
        spb = (V_to_bolts*1e3)/n_b
        data_dict = {"fric_mu": mu_fric, "Nc_kN": Nc, "Cf_kN": Cf, "V_to_bolts_kN": V_to_bolts, **design_anchors_steel(data, tpb, spb)}
        pdf = pdf_from_dict("Anchors", data_dict)
        st.download_button("Download RESULTS_BOLTS.pdf", pdf, "RESULTS_BOLTS.pdf")
    if st.button("PDF — Plate (current)"):
        pdf = pdf_from_dict("Plate", {"note":"Roark local to be added next"})
        st.download_button("Download RESULTS_BASEPLATE.pdf", pdf, "RESULTS_BASEPLATE.pdf")
