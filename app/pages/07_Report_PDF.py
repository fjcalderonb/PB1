import streamlit as st
import pandas as pd
from engine.report import build_pdf
from io import BytesIO
import pandas as pd

st.title('07 · Report & Export')

plan_png = st.session_state.get('__plan_png__')
project = {
 'code': st.session_state.get('cfg',{}).get('code','AISC/ACI (US)'),
 'units': st.session_state.get('cfg',{}).get('units','SI'),
 'B': st.session_state.get('geom',{}).get('B',0.0),
 'L': st.session_state.get('geom',{}).get('L',0.0),
 't': st.session_state.get('geom',{}).get('t',0.0) or st.session_state.get('__i3_gov__',{}).get('plate_t_mm',0.0),
 'd': st.session_state.get('geom',{}).get('d',0.0),
 'bf': st.session_state.get('geom',{}).get('bf',0.0),
 'D': st.session_state.get('anchors',{}).get('D_mm',0.0),
 'hef': st.session_state.get('anchors',{}).get('hef_mm',0.0),
 'grade': st.session_state.get('anchors',{}).get('grade','')
}

governing = st.session_state.get('__i3_gov__')
steel_df = (st.session_state.get('__i3_tables__') or {}).get('steel_df')

col = st.columns(2)
with col[0]:
    if steel_df is not None:
        st.download_button('⬇️ Export steel per-bolt (CSV)', data=steel_df.to_csv(index=False).encode('utf-8'),
                           file_name='anchors_steel.csv', mime='text/csv')
with col[1]:
    if steel_df is not None:
        bio = BytesIO()
        with pd.ExcelWriter(bio, engine='openpyxl') as xw:
            steel_df.to_excel(xw, index=False, sheet_name='Anchors_Steel')
        st.download_button('⬇️ Export all (Excel)', data=bio.getvalue(), file_name='results_i3.xlsx',
                           mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if st.button('Generate PDF (Extended)'):
    images={'plan_png': plan_png}
    tables={'governing': governing, 'sheets': {'Anchors – Steel (per bolt)': steel_df} if steel_df is not None else {}}
    pdf = build_pdf(project, images, tables)
    st.download_button('Download BasePlate_I3.pdf', data=pdf, file_name='BasePlate_I3.pdf', mime='application/pdf')

    
# import streamlit as st
# from engine.report.report_pdf import build_pdf
# st.title("07 · Report (PDF)")
# cfg = st.session_state.get('cfg',{})
# geom = st.session_state.get('geom',{})
# mat = st.session_state.get('mat',{})
# loads = st.session_state.get('loads',{})
# ass = st.session_state.get('assump',{})
# dat = st.session_state.get('__pdf__',{})
# i2  = st.session_state.get('__i2__',{})
# if st.button("Generate PDF (I2)"):
#     code = cfg.get('code','AISC/ACI (US)'); units = cfg.get('units','SI (kN, mm, MPa)')
#     B,L,t_use = geom.get('B',0.0), geom.get('L',0.0), dat.get('t_use',0.0)
#     d,bf = geom.get('d',0.0), geom.get('bf',0.0)
#     fc, fy_plate, FEXX = mat.get('fc',25.0), mat.get('fy_plate',250.0), mat.get('FEXX',483.0)
#     N,Mx,My,Vx,Vy = loads.get('N',0.0), loads.get('Mx',0.0), loads.get('My',0.0), loads.get('Vx',0.0), loads.get('Vy',0.0)
#     Vmu = dat.get('Vmu',0.0); press = dat.get('press',{}); t_req, strips = dat.get('t_req',0.0), []
#     w_req = dat.get('w_req',0.0)
#     anchors_section = {}
#     gov = i2.get('governing') if isinstance(i2, dict) else None
#     if gov:
#         anchors_section['I2 Governing (summary only)'] = gov
#     else:
#         anchors_section = { 'steel X': dat.get('res_steel_x',{}), 'steel Y': dat.get('res_steel_y',{}), 'concrete': dat.get('res_conc',{}) }
#     pdf_bytes = build_pdf(code, units, fc, fy_plate, FEXX, B, L, t_use, d, bf, 0, 0,
#                           N, Mx, My, Vx, Vy, Vmu, 1,
#                           press, t_req, strips, w_req, anchors_section)
#     st.download_button("Download BasePlate_I2.pdf", data=pdf_bytes, file_name="BasePlate_I2.pdf", mime="application/pdf")
