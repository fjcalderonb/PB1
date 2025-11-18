import streamlit as st
import pandas as pd
from engine.baseplate import contact_pressures, plate_t_local, plate_t_full_section
from engine.steel.welds import fillet_strength, required_fillet_size
from engine.steel.bolts import steel_tension_capacity, steel_shear_capacity
from engine.concrete.aci318_25 import tension_breakout_group, pullout, shear_breakout, pryout_from_tension
from engine.anchors.distribute import tension_distribution, shear_distribution
from engine.utils import round_to_5, apply_seismic_omega

st.title('05 · Results – Summary')
geom = st.session_state.get('geom',{})
mat  = st.session_state.get('mat',{})
loads= st.session_state.get('loads',{})
ass  = st.session_state.get('ass',{})
anc  = st.session_state.get('anchors',{})
cfg  = st.session_state.get('cfg',{})

if not geom or not mat or not loads or not anc:
    st.warning('Missing inputs (geometry/materials/loads/anchors).'); st.stop()

B,L,t = geom.get('B',0.0), geom.get('L',0.0), geom.get('t',0.0)
d,bf,tf,tw = geom.get('d',0.0), geom.get('bf',0.0), geom.get('tf',0.0), geom.get('tw',0.0)
N,Vx,Vy,Mx,My = loads.get('N',0.0), loads.get('Vx',0.0), loads.get('Vy',0.0), loads.get('Mx',0.0), loads.get('My',0.0)

# Seismic Ω0
seis = cfg.get('seismic_on', False); omega0 = cfg.get('omega0',2.5)
Vx_dem = apply_seismic_omega(Vx, seis, omega0)
Vy_dem = apply_seismic_omega(Vy, seis, omega0)
N_dem  = N

# Plate thickness
press = contact_pressures(N_dem, Mx, My, B, L)
if ass.get('plate_method','Local (DG1-like)').startswith('Local'):
    t_req, strips = plate_t_local(press, bf, tf, tw, B, L, mat.get('fy_plate',250.0), False, 0.0, 0.0, geom.get('t_min',10.0))
else:
    t_req, fs = plate_t_full_section(N_dem, Mx, My, B, L, mat.get('fy_plate',250.0), ass.get('bearing_fc',0.7*mat.get('fc',28.0)), geom.get('t_min',10.0))
    strips=[{'strip':'full-section','m_mm':fs.get('a_mm',0),'q':fs.get('q_max',0),'t_req':t_req}]

t_use = max(t_req, t) if t>0 else t_req
if geom.get('round_5',True): t_use = round_to_5(t_use)

st.subheader('Plate thickness')
st.write(f"Required t = {t_req:.1f} mm; Using t = **{t_use:.1f} mm**")
st.dataframe(pd.DataFrame(strips))

# Welds
phi_w, Rn_mm = fillet_strength(mat.get('FEXX',483.0))
w_req = required_fillet_size(Vx_dem, Vy_dem, Mx, My, d, bf, phi_w, Rn_mm)
st.subheader('Welds (fillet, perimetral continua)')
st.write(f"Suggested weld size: **{w_req:.1f} mm**")

# Anchors steel (per bolt)
D_mm = anc.get('D_mm',24.0); grade = anc.get('grade','F1554 Gr.55')
Nsa = steel_tension_capacity(grade, D_mm)
Vsa = steel_shear_capacity(grade, D_mm)

bolts = anc.get('bolts', [])
Ndist = tension_distribution(max(0.0,N_dem), Mx, My, [type('B',(),b) for b in bolts]) if bolts else {}
Vmode = ass.get('shear_mode','ELASTIC')
Vydist= shear_distribution(Vy_dem, [type('B',(),b) for b in bolts], mode=Vmode) if bolts else {}
Vxdist= shear_distribution(Vx_dem, [type('B',(),b) for b in bolts], mode=Vmode) if bolts else {}

rows = []
for b in bolts:
    Nb = Ndist.get(b['id'],0.0)
    Vb = max(abs(Vydist.get(b['id'],0.0)), abs(Vxdist.get(b['id'],0.0)))
    if ass.get('interact','Linear').startswith('Linear'):
        util = (Nb/max(Nsa,1e-9)) + (Vb/max(Vsa,1e-9))
    elif '1.5' in ass.get('interact',''):
        util = (Nb/max(Nsa,1e-9))**1.5 + (Vb/max(Vsa,1e-9))**1.5
    else:
        util = (Nb/max(Nsa,1e-9))**2 + (Vb/max(Vsa,1e-9))**2
    rows.append({'bolt_id':b['id'],'Nb_kN':Nb,'Vb_kN':Vb,'phiNsa_kN':Nsa,'phiVsa_kN':Vsa,'util_steel':util})
steel_df = pd.DataFrame(rows)

st.subheader('Anchors – Steel (per bolt)')
st.dataframe(steel_df)
util_steel_max = steel_df['util_steel'].max() if not steel_df.empty else 0.0

# Concrete (group-level simplified)
fc = mat.get('fc',28.0); hef=anc.get('hef_mm',400.0); c_edge=anc.get('c_edge_mm',150.0)
Ncb = tension_breakout_group(fc, hef, c_edge, max(1,len(bolts)))
Np  = pullout(fc, D_mm)
Vcb = shear_breakout(fc, hef, c_edge)
Vcp = pryout_from_tension(Ncb)

conc_summary = {'phiN_cb_kN': round(Ncb,2), 'phiN_pullout_kN': round(Np,2), 'phiV_cb_kN': round(Vcb,2), 'phiV_cp_kN': round(Vcp,2)}
st.subheader('Anchors – Concrete (ACI 318-25, draft props)')
st.json(conc_summary)

# Governing
gov = {'plate_t_mm': float(t_use), 'weld_mm': float(w_req), 'anchors_steel_util_max': float(util_steel_max)}
st.session_state['__i3_gov__'] = gov
st.session_state['__i3_tables__'] = {'steel_df': steel_df}
st.success('Results computed. Proceed to Report for export and PDF.')

# import streamlit as st
# from engine.baseplate import compute_contact_pressures, plate_local_method
# from engine.welds import fillet_weld_strength, suggest_weld_size
# from engine.anchors_steel import friction_capacity, anchor_steel_checks_dist, bolt_grade_props
# from engine.anchors_concrete import concrete_checks_draft
# import pandas as pd

# st.title("05 · Results – Summary (single case)")
# geom = st.session_state.get('geom',{})
# mat = st.session_state.get('mat',{})
# loads = st.session_state.get('loads',{})
# ass = st.session_state.get('assump',{})
# anc = st.session_state.get('anchors',{})
# if not geom or not mat or not loads:
#     st.warning("Missing inputs in previous pages.")
#     st.stop()
# N,Vx,Vy,Mx,My = loads['N'],loads['Vx'],loads['Vy'],loads['Mx'],loads['My']
# B,L,t = geom['B'],geom['L'],geom['t']
# d,bf,tf,tw = geom['d'], geom['bf'], geom['tf'], geom['tw']
# fy_plate, FEXX = mat['fy_plate'], mat['FEXX']
# use_stiff, h_stiff, t_stiff = geom.get('use_stiff',False), geom.get('h_stiff',0.0), geom.get('t_stiff',0.0)

# # Guard geometry
# if B<=0 or L<=0:
#     st.error("Set plate dimensions B>0 and L>0 in page 02 to compute plate design.")
#     st.stop()

# press = compute_contact_pressures(N,Mx,My,B,L)
# st.subheader("Contact pressures")
# st.json({k: float(v) if isinstance(v,(int,float)) else v for k,v in press.items()})

# Vmu = friction_capacity(ass.get('mu',0.45), N) if ass.get('use_friction',True) else 0.0
# Vx_eff = max(0.0, Vx - Vmu); Vy_eff = max(0.0, Vy - Vmu)
# st.write(f"Friction available V_μ = {Vmu:.2f} kN → Vx_eff = {Vx_eff:.2f} kN, Vy_eff = {Vy_eff:.2f} kN")

# t_req, strips = plate_local_method(press, bf, tf, tw, B, L, fy_plate, use_stiff, h_stiff, t_stiff)
# if t<=0: t_use=t_req; st.success(f"Required plate thickness (DG1): {t_use:.1f} mm")
# else: t_use=t; st.info(f"Provided plate thickness: {t_use:.1f} mm (required: {t_req:.1f} mm)")

# st.dataframe(pd.DataFrame(strips))

# phi_w, Rn_per_mm = fillet_weld_strength(FEXX)
# w_req = suggest_weld_size(Vx_eff, Vy_eff, Mx, My, d, bf, phi_w, Rn_per_mm)
# st.subheader("Welds (fillet, E70XX)")
# st.write(f"φR_n per mm ≈ {phi_w*Rn_per_mm:.3f} kN/mm → suggested size: **{w_req:.1f} mm**")

# case_sel = ass.get('case','Auto (1/2/3)')
# fu, fy = bolt_grade_props(anc.get('grade','F1554 Gr.55'))
# res_x = anchor_steel_checks_dist(N, Vx_eff, anc.get('n_rows',2), anc.get('bolts_per_row',2), case_sel, fu_MPa=fu, D_mm=anc.get('D_mm',24.0))
# res_y = anchor_steel_checks_dist(N, Vy_eff, anc.get('n_rows',2), anc.get('bolts_per_row',2), case_sel, fu_MPa=fu, D_mm=anc.get('D_mm',24.0))
# st.subheader("Anchors – Steel")
# st.write("Direction X:"); st.json(res_x)
# st.write("Direction Y:"); st.json(res_y)

# res_conc = concrete_checks_draft(fc=mat.get('fc',25.0), hef_mm=anc.get('hef_mm',300.0), D_mm=anc.get('D_mm',24.0),
#                                  Nx=max(0.0,-min(0.0,N)), V=max(Vx_eff,Vy_eff), c_edge_mm=anc.get('c_edge_mm',100.0))
# st.subheader("Anchors – Concrete (conservative draft)"); st.json(res_conc)

# st.session_state['__pdf__'] = {'press': press,'t_req': t_req,'t_use': t_use,'w_req': w_req,'Vmu': Vmu,
#     'Vx_eff': Vx_eff,'Vy_eff': Vy_eff,'res_steel_x': res_x,'res_steel_y': res_y,'res_conc': res_conc}
