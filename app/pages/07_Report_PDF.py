
import streamlit as st
from engine.report.report_pdf import build_pdf
st.title("07 · Report (PDF)")
cfg = st.session_state.get('cfg',{})
geom = st.session_state.get('geom',{})
mat = st.session_state.get('mat',{})
loads = st.session_state.get('loads',{})
ass = st.session_state.get('assump',{})
dat = st.session_state.get('__pdf__',{})
i2  = st.session_state.get('__i2__',{})
if st.button("Generate PDF (I2)"):
    code = cfg.get('code','AISC/ACI (US)'); units = cfg.get('units','SI (kN, mm, MPa)')
    B,L,t_use = geom.get('B',0.0), geom.get('L',0.0), dat.get('t_use',0.0)
    d,bf = geom.get('d',0.0), geom.get('bf',0.0)
    fc, fy_plate, FEXX = mat.get('fc',25.0), mat.get('fy_plate',250.0), mat.get('FEXX',483.0)
    N,Mx,My,Vx,Vy = loads.get('N',0.0), loads.get('Mx',0.0), loads.get('My',0.0), loads.get('Vx',0.0), loads.get('Vy',0.0)
    Vmu = dat.get('Vmu',0.0); press = dat.get('press',{}); t_req, strips = dat.get('t_req',0.0), []
    w_req = dat.get('w_req',0.0)
    anchors_section = {}
    gov = i2.get('governing') if isinstance(i2, dict) else None
    if gov:
        anchors_section['I2 Governing (summary only)'] = gov
    else:
        anchors_section = { 'steel X': dat.get('res_steel_x',{}), 'steel Y': dat.get('res_steel_y',{}), 'concrete': dat.get('res_conc',{}) }
    pdf_bytes = build_pdf(code, units, fc, fy_plate, FEXX, B, L, t_use, d, bf, 0, 0,
                          N, Mx, My, Vx, Vy, Vmu, 1,
                          press, t_req, strips, w_req, anchors_section)
    st.download_button("Download BasePlate_I2.pdf", data=pdf_bytes, file_name="BasePlate_I2.pdf", mime="application/pdf")
