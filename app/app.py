
import streamlit as st
import pandas as pd
from domain.models import InputData, Materials, Concrete, PlateSteel, AnchorSteel, Geometry, Loads, Method, ColumnFootprint, Pedestal, AnchorageConfig
from engines.pressure import pressure_distribution
from engines.anchors.steel import design_anchors_steel
from engines.anchors.concrete import design_anchors_concrete
from engines.plate.method2 import check_plate_method2
from adapters.sap2000 import read_joint_reactions
from services.evaluate import worst_by_discipline
from services.mapping import PRESET_A, PRESET_B
from adapters.reports.pdf import build_report

st.set_page_config(page_title="PB1 — Base Plate AISC/ACI", layout="wide")
st.title("PB1 — Base Plate (AISC/ACI)")

with st.sidebar:
    st.header("Materials")
    fc = st.number_input("f'c (MPa)", 10.0, 70.0, 31.0, 0.5)
    fy_plate = st.number_input("fy plate (MPa)", 200.0, 500.0, 235.0, 5.0)
    grade = st.selectbox("Anchor grade (F1554)", ["F1554-36","F1554-55","F1554-105"], index=1)
    if grade == "F1554-36": fu_anchor, fy_anchor = 400.0, 250.0
    elif grade == "F1554-55": fu_anchor, fy_anchor = 620.0, 380.0
    else: fu_anchor, fy_anchor = 860.0, 720.0

    st.header("Plate")
    a = st.number_input("plate a (mm)", 200.0, 3000.0, 1054.0, 1.0)
    b = st.number_input("plate b (mm)", 200.0, 3000.0, 800.0, 1.0)
    tp = st.number_input("thickness tp (mm)", 8.0, 150.0, 76.0, 1.0)

    st.subheader("Column")
    b_col = st.number_input("b_col (mm)", 50.0, 2000.0, 300.0, 1.0)
    h_col = st.number_input("h_col (mm)", 50.0, 2000.0, 300.0, 1.0)

    st.subheader("Pedestal")
    use_ped = st.checkbox("Use pedestal?", value=False)
    Bp = st.number_input("Bp (mm)", 0.0, 10000.0, 0.0, 1.0)
    Lp = st.number_input("Lp (mm)", 0.0, 10000.0, 0.0, 1.0)
    a2a1_manual = st.number_input("A2/A1 override", 0.0, 20.0, 0.0, 0.1)

    st.header("Anchorage")
    n_rows = st.number_input("# rows", 1, 10, 2)
    n_cols = st.number_input("# cols", 1, 10, 2)
    s_x = st.number_input("s_x (mm)", 50.0, 2000.0, 200.0, 1.0)
    s_y = st.number_input("s_y (mm)", 50.0, 2000.0, 200.0, 1.0)
    hef = st.number_input("hef (mm)", 50.0, 2500.0, 300.0, 1.0)
    conc_thk = st.number_input("concrete thickness (mm)", 50.0, 5000.0, 500.0, 1.0)
    cracked = st.checkbox("Cracked?", value=True)
    anchor_type = st.selectbox("Anchor type", ["headed","hooked"], index=0)
    st.caption("Edge distances (mm) to plate edges")
    c_xl = st.number_input("c_x_left", 0.0, 1000.0, 100.0, 1.0)
    c_xr = st.number_input("c_x_right", 0.0, 1000.0, 100.0, 1.0)
    c_yt = st.number_input("c_y_top", 0.0, 1000.0, 100.0, 1.0)
    c_yb = st.number_input("c_y_bottom", 0.0, 1000.0, 100.0, 1.0)

    st.header("Shear path")
    resist_shear = st.checkbox("Anchors resist shear", value=False)
    mu_fric = st.number_input("Friction μ", 0.0, 1.0, 0.30, 0.01)

    st.header("Quick loads")
    N = st.number_input("N (kN) (+ compression / - tension)", -8000.0, 8000.0, 200.0, 1.0)
    Mx = st.number_input("Mx (kN·m)", -8000.0, 8000.0, 50.0, 0.1)
    Vx = st.number_input("Vx (kN)", -5000.0, 5000.0, 20.0, 0.1)

    st.header("Methods")
    case = st.selectbox("Pressure case", ["CASE_1","CASE_2","CASE_3","CASE_4"], index=0)
    plate_method = st.selectbox("Plate method", ["ELASTIC","ROARK","PLASTIC"], index=0)

materials = Materials(concrete=Concrete(fc_MPa=fc), plate=PlateSteel(fy_MPa=fy_plate), anchors=AnchorSteel(grade=grade, fu_MPa=fu_anchor, fy_MPa=fy_anchor))
geom = Geometry(a_mm=a, b_mm=b, tp_mm=tp)
column = ColumnFootprint(b_col_mm=b_col, h_col_mm=h_col)
pedestal = Pedestal(use=use_ped, Bp_mm=Bp, Lp_mm=Lp, a2a1_override=(a2a1_manual if a2a1_manual>0 else None))
anchorage = AnchorageConfig(n_rows=int(n_rows), n_cols=int(n_cols), s_x_mm=s_x, s_y_mm=s_y, hef_mm=hef, conc_thk_mm=conc_thk, cracked=cracked, anchor_type=anchor_type, c_x_left_mm=c_xl, c_x_right_mm=c_xr, c_y_top_mm=c_yt, c_y_bottom_mm=c_yb)
loads = Loads(N_kN=N, Mx_kNm=Mx, Vx_kN=Vx)
method = Method(pressure_case=case, plate_method=plate_method)

data = InputData(materials=materials, geometry=geom, loads=loads, method=method, column=column, pedestal=pedestal, anchorage=anchorage)

TAB1, TAB2, TAB3 = st.tabs(["Designer", "Combinations (SAP2000)", "Reports"])

with TAB1:
    st.subheader("Results (sidebar loads)")
    press = pressure_distribution(data)
    qmax = press.get('sigma_max_MPa', 0.0)
    V_req = abs(loads.Vx_kN); Nc = max(0.0, loads.N_kN)
    Cf = mu_fric * Nc if not resist_shear else 0.0
    V_to_bolts = V_req if resist_shear else max(0.0, V_req - Cf)
    n_bolts = anchorage.n_rows*anchorage.n_cols
    tpb = max(0.0, loads.N_kN*1e3)/max(1,n_bolts)
    spb = (V_to_bolts*1e3)/max(1,n_bolts)
    steel = design_anchors_steel(data, tpb, spb, d_bolt_mm=25.4, tpi=13)
    conc = design_anchors_concrete(data, tpb, spb)
    plate = check_plate_method2(data, qmax)
    c1,c2 = st.columns(2)
    with c1:
        st.write("### Concrete — bearing/pressure"); st.json(press)
        st.write("### Plate (Method 2 – elastic)"); st.json(plate)
    with c2:
        st.write("### Shear path"); st.json({"mu":mu_fric, "Nc_kN":Nc, "Cf_kN":Cf, "V_to_bolts_kN":V_to_bolts})
        st.write("### Anchors (Steel)"); st.json(steel)
        st.write("### Anchors (Concrete – simplified)"); st.json(conc)

with TAB2:
    st.write("### Import SAP2000 — Joint Reactions (XLSX/CSV)")
    sapfile = st.file_uploader("Exported TABLE: Joint Reactions", type=["xlsx","csv"])
    if sapfile:
        try:
            df = read_joint_reactions(sapfile)
            st.success(f"Rows read: {len(df)}"); st.caption(f"Columns detected: {list(df.columns)}")
            st.dataframe(df.head(25), use_container_width=True)
            preset_name = st.radio("Choose preset", ["Preset A","Preset B","Advanced"], horizontal=True)
            mapping = PRESET_A if preset_name.startswith("Preset A") else PRESET_B
            flips = {k: False for k in ["N","Vx","Vy","Mx","My"]}
            if preset_name == "Advanced":
                cols = [c for c in ["F1","F2","F3","M1","M2","M3"] if c in df.columns]
                c1,c2,c3,c4,c5 = st.columns(5)
                mapping["N"]  = c1.selectbox("N ←",  cols, index=cols.index("F3") if "F3" in cols else 0)
                mapping["Vx"] = c2.selectbox("Vx ←", cols, index=0)
                mapping["Vy"] = c3.selectbox("Vy ←", cols, index=1 if len(cols)>1 else 0)
                mapping["Mx"] = c4.selectbox("Mx ←", cols, index=3 if len(cols)>3 else 0)
                mapping["My"] = c5.selectbox("My ←", cols, index=4 if len(cols)>4 else 0)
                d1,d2,d3,d4,d5 = st.columns(5)
                flips["N"]  = d1.checkbox("Flip N"); flips["Vx"] = d2.checkbox("Flip Vx"); flips["Vy"] = d3.checkbox("Flip Vy"); flips["Mx"] = d4.checkbox("Flip Mx"); flips["My"] = d5.checkbox("Flip My")
            else:
                st.caption(f"Using {preset_name}: {mapping}")
            def apply_mapping(dfin: pd.DataFrame, mapping: dict, flips: dict) -> pd.DataFrame:
                out = pd.DataFrame({
                    'Joint': dfin['Joint'] if 'Joint' in dfin.columns else None,
                    'OutputCase': dfin['OutputCase'] if 'OutputCase' in dfin.columns else 'Unknown',
                    'N_kN':  dfin[mapping['N']]  * (-1 if flips.get('N')  else 1),
                    'Vx_kN': dfin[mapping['Vx']] * (-1 if flips.get('Vx') else 1),
                    'Vy_kN': dfin[mapping['Vy']] * (-1 if flips.get('Vy') else 1),
                    'Mx_kNm':dfin[mapping['Mx']] * (-1 if flips.get('Mx') else 1),
                    'My_kNm':dfin[mapping['My']] * (-1 if flips.get('My') else 1),
                })
                mask = out[['N_kN','Vx_kN','Vy_kN','Mx_kNm','My_kNm']].notna().any(axis=1)
                return out.loc[mask].reset_index(drop=True)
            df_std = apply_mapping(df, mapping, flips)
            st.dataframe(df_std.head(25), use_container_width=True)
            from services.evaluate import worst_by_discipline
            with st.spinner("Evaluating worst cases per discipline..."):
                worst = worst_by_discipline(df_std, data, mu_fric, resist_shear, anchorage.n_rows*anchorage.n_cols, 25.4)
            def show_worst(label: str, key: str, wr: dict):
                st.write(f"### {label} — Worst case")
                if not wr:
                    st.warning("No rows to evaluate."); return
                meta = wr['meta']
                st.write(f"Joint {meta['Joint']} — Case: {meta['OutputCase']}")
                st.json({**wr['loads'], **wr.get(key, {})})
                if st.button(f"Push to Designer ({label})", key=f"btn_{key}"):
                    data.loads.N_kN  = wr['loads']['N_kN']; data.loads.Mx_kNm= wr['loads']['Mx_kNm']; data.loads.Vx_kN = wr['loads']['Vx_kN']
                    st.success(f"Loaded {label}: Joint {meta['Joint']} — {meta['OutputCase']}")
            c1,c2,c3 = st.columns(3)
            with c1: show_worst("Concrete", 'concrete', worst['concrete'])
            with c2: show_worst("Anchors", 'anchors', worst['anchors'])
            with c3: show_worst("Plate", 'plate', worst['plate'])
        except Exception as e:
            st.error(f"Import error: {e}")
            try:
                sapfile.seek(0)
                raw = pd.read_excel(sapfile, header=None) if sapfile.name.lower().endswith('xlsx') else pd.read_csv(sapfile, header=None)
                st.write("Raw preview (first 10 rows):"); st.dataframe(raw.head(10), use_container_width=True)
            except Exception:
                pass

with TAB3:
    st.write("### Consolidated PDF report")
    if st.button("Build report (current inputs)"):
        press = pressure_distribution(data)
        qmax = press.get('sigma_max_MPa', 0.0)
        plate = check_plate_method2(data, qmax)
        n_bolts = data.anchorage.n_rows*data.anchorage.n_cols
        V_req = abs(data.loads.Vx_kN); Nc = max(0.0, data.loads.N_kN)
        Cf = mu_fric * Nc if not resist_shear else 0.0
        V_to_bolts = V_req if resist_shear else max(0.0, V_req - Cf)
        tpb = max(0.0, data.loads.N_kN*1e3)/max(1,n_bolts)
        spb = (V_to_bolts*1e3)/max(1,n_bolts)
        steel = design_anchors_steel(data, tpb, spb, d_bolt_mm=25.4, tpi=13)
        conc = design_anchors_concrete(data, tpb, spb)
        sections = [
            ("Inputs", {"fc (MPa)": data.materials.concrete.fc_MPa, "fy_plate (MPa)": data.materials.plate.fy_MPa, "Plate (mm)": f"{data.geometry.a_mm} x {data.geometry.b_mm} x {data.geometry.tp_mm}", "N/Mx/Vx": f"{data.loads.N_kN} / {data.loads.Mx_kNm} / {data.loads.Vx_kN}"}),
            ("Concrete — Bearing/Pressure", press), ("Anchors — Steel", steel), ("Anchors — Concrete (simplified)", conc), ("Base Plate", plate)
        ]
        pdf = build_report("PB1 — Base Plate Report", sections)
        st.download_button("Download PB1_REPORT.pdf", pdf, "PB1_REPORT.pdf")
