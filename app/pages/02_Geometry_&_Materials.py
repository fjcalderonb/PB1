
import streamlit as st
if 'geom' not in st.session_state: st.session_state['geom'] = {}
if 'mat' not in st.session_state: st.session_state['mat'] = {}
if 'anchors' not in st.session_state: st.session_state['anchors'] = {}

st.title("02 · Geometry & Materials")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Column (W-shape)")
    st.session_state['geom']['d']  = st.number_input("Depth d (mm)", value=300.0, step=10.0)
    st.session_state['geom']['bf'] = st.number_input("Flange width bf (mm)", value=200.0, step=5.0)
    st.session_state['geom']['tf'] = st.number_input("Flange thickness tf (mm)", value=15.0, step=1.0)
    st.session_state['geom']['tw'] = st.number_input("Web thickness tw (mm)", value=9.0, step=1.0)
with col2:
    st.subheader("Base plate")
    st.session_state['geom']['B'] = st.number_input("B (mm) – along x", value=400.0, step=10.0, min_value=0.0)
    st.session_state['geom']['L'] = st.number_input("L (mm) – along y", value=500.0, step=10.0, min_value=0.0)
    st.session_state['geom']['t'] = st.number_input("Plate thickness t (mm) (0 = compute)", value=0.0, step=1.0, min_value=0.0)
with col3:
    st.subheader("Materials")
    st.session_state['mat']['fc'] = st.number_input("Concrete f'c (MPa)", value=25.0, step=1.0)
    st.session_state['mat']['fy_plate'] = st.number_input("Plate fy (MPa)", value=250.0, step=10.0)
    st.session_state['mat']['FEXX'] = st.number_input("Fillet weld F_EXX (MPa) – E70XX ≈ 483 MPa", value=483.0, step=10.0)

with st.expander("Stiffeners (optional)"):
    st.session_state['geom']['use_stiff'] = st.checkbox("Use stiffeners", value=False)
    st.session_state['geom']['h_stiff'] = st.number_input("Stiffener height (mm)", value=120.0, step=5.0)
    st.session_state['geom']['t_stiff'] = st.number_input("Stiffener thickness (mm)", value=10.0, step=1.0)

st.subheader("Anchors & Concrete parameters")
ca1, ca2, ca3, ca4 = st.columns(4)
with ca1:
    st.session_state['anchors']['D_mm'] = st.number_input("Ø Anchor (mm)", value=24.0, step=2.0)
with ca2:
    st.session_state['anchors']['hef_mm'] = st.number_input("hef (mm)", value=300.0, step=10.0)
with ca3:
    st.session_state['anchors']['c_edge_mm'] = st.number_input("Edge distance c (mm)", value=100.0, step=5.0)
with ca4:
    st.session_state['anchors']['n_rows'] = st.number_input("Bolt rows", min_value=1, max_value=4, value=2)

cb1, cb2, cb3 = st.columns(3)
with cb1:
    st.session_state['anchors']['bolts_per_row'] = st.number_input("Bolts per row", min_value=1, max_value=12, value=2)
with cb2:
    grade = st.selectbox("Bolt grade", [
        'F1554 Gr.36','F1554 Gr.55','F1554 Gr.105','A307','A193 B7','A449','ISO 8.8','ISO 10.9'
    ], index=1)
    st.session_state['anchors']['grade'] = grade
with cb3:
    st.session_state['anchors']['en1090'] = st.checkbox("EN1090 thread (Ase = A_t)", value=True)

if st.session_state['geom']['B']<=0 or st.session_state['geom']['L']<=0:
    st.warning("Set plate dimensions B>0 and L>0 to enable plate design and batch governing.")

st.success("Geometry, materials and anchors saved (hef, c_edge, grade/diameter shared by steel & concrete).")
