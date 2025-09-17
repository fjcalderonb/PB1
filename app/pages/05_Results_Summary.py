
import streamlit as st
from engine.baseplate import compute_contact_pressures, plate_local_method
from engine.welds import fillet_weld_strength, suggest_weld_size
from engine.anchors_steel import friction_capacity, anchor_steel_checks_dist, bolt_grade_props
from engine.anchors_concrete import concrete_checks_draft
import pandas as pd

st.title("05 · Results – Summary (single case)")
geom = st.session_state.get('geom',{})
mat = st.session_state.get('mat',{})
loads = st.session_state.get('loads',{})
ass = st.session_state.get('assump',{})
anc = st.session_state.get('anchors',{})
if not geom or not mat or not loads:
    st.warning("Missing inputs in previous pages.")
    st.stop()
N,Vx,Vy,Mx,My = loads['N'],loads['Vx'],loads['Vy'],loads['Mx'],loads['My']
B,L,t = geom['B'],geom['L'],geom['t']
d,bf,tf,tw = geom['d'], geom['bf'], geom['tf'], geom['tw']
fy_plate, FEXX = mat['fy_plate'], mat['FEXX']
use_stiff, h_stiff, t_stiff = geom.get('use_stiff',False), geom.get('h_stiff',0.0), geom.get('t_stiff',0.0)

# Guard geometry
if B<=0 or L<=0:
    st.error("Set plate dimensions B>0 and L>0 in page 02 to compute plate design.")
    st.stop()

press = compute_contact_pressures(N,Mx,My,B,L)
st.subheader("Contact pressures")
st.json({k: float(v) if isinstance(v,(int,float)) else v for k,v in press.items()})

Vmu = friction_capacity(ass.get('mu',0.45), N) if ass.get('use_friction',True) else 0.0
Vx_eff = max(0.0, Vx - Vmu); Vy_eff = max(0.0, Vy - Vmu)
st.write(f"Friction available V_μ = {Vmu:.2f} kN → Vx_eff = {Vx_eff:.2f} kN, Vy_eff = {Vy_eff:.2f} kN")

t_req, strips = plate_local_method(press, bf, tf, tw, B, L, fy_plate, use_stiff, h_stiff, t_stiff)
if t<=0: t_use=t_req; st.success(f"Required plate thickness (DG1): {t_use:.1f} mm")
else: t_use=t; st.info(f"Provided plate thickness: {t_use:.1f} mm (required: {t_req:.1f} mm)")

st.dataframe(pd.DataFrame(strips))

phi_w, Rn_per_mm = fillet_weld_strength(FEXX)
w_req = suggest_weld_size(Vx_eff, Vy_eff, Mx, My, d, bf, phi_w, Rn_per_mm)
st.subheader("Welds (fillet, E70XX)")
st.write(f"φR_n per mm ≈ {phi_w*Rn_per_mm:.3f} kN/mm → suggested size: **{w_req:.1f} mm**")

case_sel = ass.get('case','Auto (1/2/3)')
fu, fy = bolt_grade_props(anc.get('grade','F1554 Gr.55'))
res_x = anchor_steel_checks_dist(N, Vx_eff, anc.get('n_rows',2), anc.get('bolts_per_row',2), case_sel, fu_MPa=fu, D_mm=anc.get('D_mm',24.0))
res_y = anchor_steel_checks_dist(N, Vy_eff, anc.get('n_rows',2), anc.get('bolts_per_row',2), case_sel, fu_MPa=fu, D_mm=anc.get('D_mm',24.0))
st.subheader("Anchors – Steel")
st.write("Direction X:"); st.json(res_x)
st.write("Direction Y:"); st.json(res_y)

res_conc = concrete_checks_draft(fc=mat.get('fc',25.0), hef_mm=anc.get('hef_mm',300.0), D_mm=anc.get('D_mm',24.0),
                                 Nx=max(0.0,-min(0.0,N)), V=max(Vx_eff,Vy_eff), c_edge_mm=anc.get('c_edge_mm',100.0))
st.subheader("Anchors – Concrete (conservative draft)"); st.json(res_conc)

st.session_state['__pdf__'] = {'press': press,'t_req': t_req,'t_use': t_use,'w_req': w_req,'Vmu': Vmu,
    'Vx_eff': Vx_eff,'Vy_eff': Vy_eff,'res_steel_x': res_x,'res_steel_y': res_y,'res_conc': res_conc}
