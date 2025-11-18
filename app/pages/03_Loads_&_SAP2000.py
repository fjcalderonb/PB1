import streamlit as st
import pandas as pd
from engine.io_sap import read_sap_table

if 'sap' not in st.session_state: st.session_state['sap']={}
st.title('03 · Loads & SAP2000')

up = st.file_uploader("Upload SAP2000 'Joint Reactions' (XLS/XLSX/CSV)", type=['xls','xlsx','csv'])
if up:
    df = read_sap_table(up); st.session_state['sap']['df'] = df

if 'df' not in st.session_state.get('sap',{}):
    st.info('Upload a SAP2000 reactions file to continue.'); st.stop()

df = st.session_state['sap']['df']
st.dataframe(df.head(30), width='stretch')

st.subheader('Case classification')
st.write('Detected ULS/SLS from OutputCase name; you can override below if needed.')
if 'ULS_SLS' in df.columns:
    st.dataframe(df[['OutputCase','ULS_SLS']].drop_duplicates().reset_index(drop=True))
st.session_state['sap']['override'] = st.selectbox('Use cases classified as', ['ULS (recommended)','SLS','All'], index=0)

# pick joint & case
joint_col = st.selectbox('Joint column', [c for c in df.columns if 'Joint' in str(c)], index=0)
case_col  = st.selectbox('OutputCase column', [c for c in df.columns if 'OutputCase' in str(c)], index=0)

joints = sorted(df[joint_col].astype(str).unique())
cases  = sorted(df[case_col].astype(str).unique())
J = st.selectbox('Joint', joints, index=0)
C = st.selectbox('OutputCase', cases, index=0)
rows = df[(df[joint_col].astype(str)==str(J)) & (df[case_col].astype(str)==str(C))]

num = rows[['F1','F2','F3','M1','M2']].apply(pd.to_numeric, errors='coerce').dropna()
if num.empty:
    st.warning('No numeric F*/M* columns found after selection.')
else:
    agg = st.radio('If multiple rows:', ['Average','Max |value|'], index=1, horizontal=True)
    v = num.mean() if agg=='Average' else num.abs().max()
    # Preset A: N←F3, Vx←F1, Vy←F2, Mx←M2, My←M1.
    N,Vx,Vy,Mx,My = v['F3'], v['F1'], v['F2'], v['M2'], v['M1']
    st.session_state['loads']={'N':float(N),'Vx':float(Vx),'Vy':float(Vy),'Mx':float(Mx),'My':float(My),'case':str(C),'joint':str(J)}
    st.success(f"Loaded → N={N:.3f} kN, Vx={Vx:.3f} kN, Vy={Vy:.3f} kN, Mx={Mx:.3f} kN·m, My={My:.3f} kN·m")

    
# import streamlit as st
# import pandas as pd
# from engine import sap2000
# from engine.utils.axes import apply_preset, flip_signs
# from engine.baseplate import compute_contact_pressures, plate_local_method
# from engine.welds import fillet_weld_strength, suggest_weld_size
# from engine.anchors_steel import friction_capacity, anchor_steel_checks_dist, bolt_grade_props
# from engine.anchors_concrete import concrete_checks_draft

# if 'loads' not in st.session_state:
#     st.session_state['loads'] = {'N':500.0,'Vx':60.0,'Vy':120.0,'Mx':50.0,'My':80.0}

# st.title("03 · Loads & SAP2000 (Single + Batch/Governing I2)")

# sap_file = st.file_uploader("Upload SAP2000 'Joint Reactions' (XLS/XLSX/CSV) — one upload for both tabs", type=["xls","xlsx","csv"], key='sap_once')
# if sap_file is not None:
#     df = sap2000.read_sap_table(sap_file)
#     if isinstance(df, pd.DataFrame) and len(df)>0:
#         st.session_state['sap_df'] = df
#         st.dataframe(df.head(15), use_container_width=True)
#     else:
#         st.error("Could not parse this file. Check headers and data.")

# if 'sap_df' not in st.session_state:
#     st.info("Upload a SAP2000 reactions file to enable the tabs below.")
#     st.stop()

# # Tabs
# single_tab, batch_tab = st.tabs(["Single case", "Batch & Governing (I2)"])

# df = st.session_state['sap_df']

# with single_tab:
#     joint_col = 'Joint' if 'Joint' in df.columns else st.selectbox("Joint column", df.columns, key='jc_single')
#     case_col  = 'OutputCase' if 'OutputCase' in df.columns else st.selectbox("OutputCase column", df.columns, key='oc_single')
#     try:
#         joints = sorted(pd.to_numeric(df[joint_col], errors='coerce').dropna().astype(int).astype(str).unique())
#     except Exception:
#         joints = sorted(df[joint_col].astype(str).unique())
#     cases  = sorted(df[case_col].astype(str).unique())
#     c1, c2 = st.columns(2)
#     with c1:
#         J = st.selectbox("Joint", joints, key='J_single')
#     with c2:
#         C = st.selectbox("OutputCase", cases, key='C_single')
#     df_pick = df[(df[joint_col].astype(str)==str(J)) & (df[case_col].astype(str)==str(C))]
#     st.caption(f"Selected rows: {len(df_pick)}")

#     colsF = [c for c in df_pick.columns if str(c).upper().startswith('F')]
#     colsM = [c for c in df_pick.columns if str(c).upper().startswith('M')]
#     if not colsF or not colsM:
#         st.error("Could not find F*/M* columns in this sheet. Check your export.")
#     else:
#         st.subheader("Axis Mapper – Presets & Signs")
#         preset = st.radio("Preset", ["Preset A (default)", "Preset B (swap 1↔2)"], index=0, horizontal=True, key='preset_single',
#                           help="Preset A: N←F3, Vx←F1, Vy←F2, Mx←M2, My←M1. Preset B: swap 1↔2 (useful when local axes are rotated).")
#         flips = st.multiselect("Flip signs (optional)", ["N","Vx","Vy","Mx","My"], default=[], key='flips_single')

#         agg = st.radio("If multiple rows:", ["Average","Max |value|"], index=1, horizontal=True, key='agg_single')

#         cN = 'F3' if 'F3' in df_pick.columns else colsF[0]
#         cF1 = 'F1' if 'F1' in df_pick.columns else colsF[0]
#         cF2 = 'F2' if 'F2' in df_pick.columns else (colsF[1] if len(colsF)>1 else colsF[0])
#         cM1 = 'M1' if 'M1' in df_pick.columns else colsM[0]
#         cM2 = 'M2' if 'M2' in df_pick.columns else (colsM[1] if len(colsM)>1 else colsM[0])

#         pick = df_pick[[cN,cF1,cF2,cM1,cM2]].apply(pd.to_numeric, errors='coerce').dropna()
#         if len(pick)==0:
#             st.warning("No numeric data after selection.")
#         else:
#             row = pick.mean() if agg=="Average" else pick.abs().max()
#             F3 = row[cN] if cN in row.index else 0.0
#             F1 = row[cF1] if cF1 in row.index else 0.0
#             F2 = row[cF2] if cF2 in row.index else 0.0
#             M1 = row[cM1] if cM1 in row.index else 0.0
#             M2 = row[cM2] if cM2 in row.index else 0.0

#             N,Vx,Vy,Mx,My = apply_preset(preset, F1,F2,F3,M1,M2)
#             if abs(Mx)>1e4: Mx/=1000.0
#             if abs(My)>1e4: My/=1000.0
#             N,Vx,Vy,Mx,My = flip_signs(N,Vx,Vy,Mx,My, flips)

#             st.session_state['loads'] = {'N':float(N),'Vx':float(Vx),'Vy':float(Vy),'Mx':float(Mx),'My':float(My)}
#             st.success(f"Loaded → N={N:.3f} kN, Vx={Vx:.3f} kN, Vy={Vy:.3f} kN, Mx={Mx:.3f} kN·m, My={My:.3f} kN·m")

# with batch_tab:
#     preset = st.radio("Preset", ["Preset A (default)", "Preset B (swap 1↔2)"], index=0, horizontal=True, key='preset_batch')
#     flips = st.multiselect("Flip signs", ["N","Vx","Vy","Mx","My"], default=[], key='flips_batch')

#     geom = st.session_state.get('geom',{})
#     B = float(geom.get('B',0.0)); L = float(geom.get('L',0.0))
#     if B<=0 or L<=0:
#         st.error("Set plate dimensions B>0 and L>0 in page 02 before running the batch governing.")
#         st.stop()

#     raw = df
#     recs = []
#     for _, r in raw.iterrows():
#         F3 = pd.to_numeric(r.get('F3', None), errors='coerce')
#         F1 = pd.to_numeric(r.get('F1', None), errors='coerce')
#         F2 = pd.to_numeric(r.get('F2', None), errors='coerce')
#         M1 = pd.to_numeric(r.get('M1', None), errors='coerce')
#         M2 = pd.to_numeric(r.get('M2', None), errors='coerce')
#         if pd.isna(F1) and pd.isna(F2) and pd.isna(F3):
#             continue
#         N,Vx,Vy,Mx,My = apply_preset(preset, F1 or 0.0, F2 or 0.0, F3 or 0.0, M1 or 0.0, M2 or 0.0)
#         if abs(Mx)>1e4: Mx/=1000.0
#         if abs(My)>1e4: My/=1000.0
#         N,Vx,Vy,Mx,My = flip_signs(N,Vx,Vy,Mx,My, flips)
#         recs.append({'Joint': str(r.get('Joint','')), 'OutputCase': str(r.get('OutputCase','')),
#                      'N': float(N), 'Vx': float(Vx), 'Vy': float(Vy), 'Mx': float(Mx), 'My': float(My)})

#     if not recs:
#         st.error("No numeric reactions after mapping.")
#     else:
#         loads_df = pd.DataFrame(recs)
#         st.dataframe(loads_df.head(20), use_container_width=True)

#         mat  = st.session_state.get('mat',{})
#         anc  = st.session_state.get('anchors',{})
#         ass  = st.session_state.get('assump',{})
#         d,bf,tf,tw = st.session_state['geom'].get('d',0.0), st.session_state['geom'].get('bf',0.0), st.session_state['geom'].get('tf',0.0), st.session_state['geom'].get('tw',0.0)
#         fy_plate, FEXX = mat.get('fy_plate',250.0), mat.get('FEXX',483.0)
#         use_stiff, h_stiff, t_stiff = st.session_state['geom'].get('use_stiff',False), st.session_state['geom'].get('h_stiff',0.0), st.session_state['geom'].get('t_stiff',0.0)
#         mu = ass.get('mu',0.45) if ass.get('use_friction',True) else 0.0
#         n_rows, bpr = int(anc.get('n_rows',2)), int(anc.get('bolts_per_row',2))
#         D_mm = anc.get('D_mm',24.0)
#         hef = anc.get('hef_mm',300.0)
#         c_edge = anc.get('c_edge_mm',100.0)
#         grade = anc.get('grade','F1554 Gr.55')
#         fu, fy = bolt_grade_props(grade)

#         def eval_case(row):
#             N,Vx,Vy,Mx,My = row['N'],row['Vx'],row['Vy'],row['Mx'],row['My']
#             press = compute_contact_pressures(N,Mx,My,B,L)
#             t_req, _ = plate_local_method(press, bf, tf, tw, B, L, fy_plate, use_stiff, h_stiff, t_stiff)
#             Vmu = mu*N if N>0 else 0.0
#             Vx_eff = max(0.0, Vx - Vmu)
#             Vy_eff = max(0.0, Vy - Vmu)
#             phi_w, Rn_per_mm = fillet_weld_strength(FEXX)
#             w_req = suggest_weld_size(Vx_eff, Vy_eff, Mx, My, d, bf, phi_w, Rn_per_mm)
#             rx = anchor_steel_checks_dist(N, Vx_eff, n_rows, bpr, 'Auto (1/2/3)', fu_MPa=fu, D_mm=D_mm)
#             ry = anchor_steel_checks_dist(N, Vy_eff, n_rows, bpr, 'Auto (1/2/3)', fu_MPa=fu, D_mm=D_mm)
#             util_steel = max(rx['util_max'], ry['util_max'])
#             conc = concrete_checks_draft(fc=mat.get('fc',25.0), hef_mm=hef, D_mm=D_mm, Nx=max(0.0,-min(0.0,N)), V=max(Vx_eff,Vy_eff), c_edge_mm=c_edge)
#             return {'Joint': row['Joint'], 'OutputCase': row['OutputCase'], 't_req_mm': t_req, 'weld_req_mm': w_req,
#                     'util_steel': util_steel, 'phiN_cb_kN(draft)': conc.get('phiN_cb_kN (draft)'), 'phiV_cb_kN(draft)': conc.get('phiV_cb_kN (draft)')}

#         res = pd.DataFrame([eval_case(r) for _, r in loads_df.iterrows()])
#         st.subheader("Governing by mechanism")
#         gov = {'plate_t': res.loc[res['t_req_mm'].idxmax()].to_dict(),
#                'weld_size': res.loc[res['weld_req_mm'].idxmax()].to_dict(),
#                'anchors_steel': res.loc[res['util_steel'].idxmax()].to_dict()}
#         st.json(gov)
#         st.session_state['__i2__'] = {'batch_table': res.to_dict(orient='records'), 'governing': gov}

# st.caption("This page uses a **single upload** and two tabs to work with the same SAP file.")
