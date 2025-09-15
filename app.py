
import streamlit as st
import pandas as pd
from core.models import (InputData, Materials, Concrete, PlateSteel, AnchorSteel, PhiFactors,
                         Geometry, Anchors, AnchorLine, Loads, Method, Options)
from core.pressure import pressure_distribution
from core.anchors import design_anchors
from core.plate import plate_checks
from core.sap_import import read_sap_joint_reactions
from core.evaluator import worst_by_discipline
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
    a = st.number_input("a (mm)", 200.0, 3000.0, 1054.0, 1.0)
    b = st.number_input("b (mm)", 200.0, 3000.0, 800.0, 1.0)
    tp = st.number_input("tp (mm)", 8.0, 150.0, 76.0, 1.0)

    st.header("Anchors (line 1)")
    diam_in = st.selectbox("Diameter (in)", ["1/2","5/8","3/4","7/8","1","1-1/8","1-1/4"])
    DIAM_TO_MM = {"1/2":12.7,"5/8":15.875,"3/4":19.05,"7/8":22.225,"1":25.4,"1-1/8":28.575,"1-1/4":31.75}
    d_mm = DIAM_TO_MM[diam_in]
    n_bolts = st.number_input("# of bolts (line 1)", 2, 16, 4, 1)
    g1 = st.number_input("g1 (mm, edge→bolt)", 20.0, 400.0, 114.0, 1.0)
    v1 = st.number_input("v1 (mm, side margin)", 20.0, 600.0, 241.5, 0.5)
    resist_shear = st.checkbox("Anchors resist shear", value=False)
    mu_fric = st.number_input("Friction μ (plate–grout/concrete)", 0.0, 1.0, 0.30, 0.01)

    st.header("Quick loads (for manual check)")
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
geom = Geometry(a_mm=a, b_mm=b, tp_mm=tp, g1_mm=g1, v1_mm=v1)
anchors = Anchors(lines=[AnchorLine(index=1, n_bolts=int(n_bolts), edge_dist_mm=g1, bolt_d_mm=d_mm)],
                  resist_shear=resist_shear)
loads = Loads(N_kN=N, Mx_kNm=Mx, Vx_kN=Vx)
method = Method(pressure_case=case, plate_method=plate_method)
data = InputData(materials=materials, geometry=geom, anchors=anchors, loads=loads, method=method)


# Tabs
tab_main, tab_sap, tab_pdf = st.tabs(["Design/Checks", "Combinations (SAP2000)", "Reports"])

with tab_main:
    st.subheader("Results (from manual sidebar loads)")
    press = pressure_distribution(data)

    # Friction vs. bolts for Vx
    V_req = abs(loads.Vx_kN)
    Nc = max(0.0, loads.N_kN)
    Cf = mu_fric * Nc if not resist_shear else 0.0
    V_to_bolts = max(0.0, V_req - Cf) if not resist_shear else V_req

    n_b = max(1, anchors.lines[0].n_bolts)
    tpb = max(0.0, loads.N_kN*1e3)/n_b
    spb = (V_to_bolts*1e3)/n_b

    anch = design_anchors(data, tpb, spb)
    plate = plate_checks(data, q_max_Pa=press.get("sigma_max_MPa",0.0)*1e6)

    c1, c2 = st.columns(2)
    with c1:
        st.write("### Concrete — Bearing/pressure")
        st.json(press)
        st.write("### Plate")
        st.json(plate)
    with c2:
        st.write("### Shear path")
        st.write({"mu": mu_fric, "Nc_kN": Nc, "Cf_kN": Cf, "V_to_bolts_kN": V_to_bolts})
        st.write("### Anchors (Steel)")
        st.json(anch)

with tab_sap:
    st.write("### Import SAP2000 — Joint Reactions (XLSX/CSV)")
    sapfile = st.file_uploader("File exported from SAP2000 (TABLE: Joint Reactions)", type=["xlsx","csv"])

    if sapfile:
        df = read_sap_joint_reactions(sapfile)
        st.caption(f"Rows read: {len(df)} — Joints sample: {sorted(df['Joint'].dropna().astype(int).unique().tolist())[:10]} ...")

        # ===== Axis mapper (presets + advanced) =====
        st.write("#### Axis and sign mapper")
        preset = st.radio("Preset", ["Preset A (default)", "Preset B (swap 1↔2)", "Advanced"], horizontal=True)

        def mapping_from_preset(preset_label: str):
            if preset_label.startswith("Preset A"):
                return {"N":"F3", "Vx":"F1", "Vy":"F2", "Mx":"M2", "My":"M1"}
            if preset_label.startswith("Preset B"):
                # swap 1<->2
                return {"N":"F3", "Vx":"F2", "Vy":"F1", "Mx":"M1", "My":"M2"}
            # Advanced default start from A
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

        # Build standardized DF for ALL joints/rows (ignore CaseType/StepType)
        def apply_mapping(dfin: pd.DataFrame, mapping: dict, flips: dict) -> pd.DataFrame:
            out = pd.DataFrame({
                'Joint': dfin['Joint'],
                'OutputCase': dfin['OutputCase'],
                'N_kN':  dfin[mapping['N']]  * (-1 if flips.get('N') else 1),
                'Vx_kN': dfin[mapping['Vx']] * (-1 if flips.get('Vx') else 1),
                'Vy_kN': dfin[mapping['Vy']] * (-1 if flips.get('Vy') else 1),
                'Mx_kNm': dfin[mapping['Mx']] * (-1 if flips.get('Mx') else 1),
                'My_kNm': dfin[mapping['My']] * (-1 if flips.get('My') else 1),
            })
            # drop rows with all NaNs in mapped forces
            mask = out[['N_kN','Vx_kN','Vy_kN','Mx_kNm','My_kNm']].notna().any(axis=1)
            return out.loc[mask].reset_index(drop=True)

        df_std = apply_mapping(df, mapping, flips)
        st.dataframe(df_std.head(25), use_container_width=True)

        # Evaluate ALL rows and pick worst per discipline
        with st.spinner("Evaluating worst cases per discipline..."):
            worst = worst_by_discipline(df_std, data, mu_fric, resist_shear)

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
        # Recompute shear split
        V_req = abs(loads.Vx_kN); Nc = max(0.0, loads.N_kN)
        Cf = mu_fric * Nc if not anchors.resist_shear else 0.0
        V_to_bolts = max(0.0, V_req - Cf) if not anchors.resist_shear else V_req
        n_b = max(1, anchors.lines[0].n_bolts)
        tpb = max(0.0, loads.N_kN*1e3)/n_b
        spb = (V_to_bolts*1e3)/n_b
        data_dict = {"fric_mu": mu_fric, "Nc_kN": Nc, "Cf_kN": Cf, "V_to_bolts_kN": V_to_bolts, **design_anchors(data, tpb, spb)}
        pdf = pdf_from_dict("Anchors", data_dict)
        st.download_button("Download RESULTS_BOLTS.pdf", pdf, "RESULTS_BOLTS.pdf")
    if st.button("PDF — Plate (current)"):
        pdf = pdf_from_dict("Plate", plate_checks(data, 0.0))
        st.download_button("Download RESULTS_BASEPLATE.pdf", pdf, "RESULTS_BASEPLATE.pdf")
