import streamlit as st
import pandas as pd
from engine.plot_plan import render_plan_png

if 'anchors' not in st.session_state: st.session_state['anchors']={}
st.title('06 · Anchors Layout (Parametric & CSV)')

B = st.session_state.get('geom',{}).get('B',0.0)
L = st.session_state.get('geom',{}).get('L',0.0)

mode = st.radio('Input mode', ['Parametric','CSV'], index=0, horizontal=True)
bolts = []

if mode=='Parametric':
    c1,c2,c3 = st.columns(3)
    with c1:
        n_rows = st.number_input('Rows (Y)', min_value=1, max_value=6, value=2)
        n_cols = st.number_input('Cols (X)', min_value=1, max_value=6, value=2)
    with c2:
        sx = st.number_input('Spacing X (mm)', value=300.0)
        sy = st.number_input('Spacing Y (mm)', value=400.0)
    with c3:
        ex = st.number_input('Edge distance X (mm)', value=100.0)
        ey = st.number_input('Edge distance Y (mm)', value=100.0)
    hole = st.number_input('Hole diameter in plate (mm)', value=30.0)
    # centered grid
    xs = [-(n_cols-1)/2.0*sx + i*sx for i in range(n_cols)]
    ys = [-(n_rows-1)/2.0*sy + j*sy for j in range(n_rows)]
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            bolts.append({'id':f'B{j*n_cols+i+1}','x':x,'y':y,'hole_d':hole})
else:
    up = st.file_uploader('Upload bolts CSV (bolt_id,x_mm,y_mm,hole_d_mm)', type=['csv'])
    if up:
        df = pd.read_csv(up)
        for _,r in df.iterrows():
            bolts.append({'id':str(r.get('bolt_id','')),'x':float(r.get('x_mm',0)), 'y':float(r.get('y_mm',0)), 'hole_d': float(r.get('hole_d_mm',30))})
    if st.button('Load sample 4-bolt set'):
        df = pd.read_csv('data/samples/bolts_rect_4.csv')
        for _,r in df.iterrows():
            bolts.append({'id':str(r.get('bolt_id','')),'x':float(r.get('x_mm',0)), 'y':float(r.get('y_mm',0)), 'hole_d': float(r.get('hole_d_mm',30))})

if bolts:
    st.session_state['anchors']['bolts']=bolts
    img = render_plan_png(B, L, bolts, st.session_state['geom'].get('d',0.0), st.session_state['geom'].get('bf',0.0))
    st.image(img, caption='Anchor plan (auto-dim to axes & edges)')
    st.session_state['__plan_png__']=img
    st.success(f'{len(bolts)} bolts loaded.')
else:
    st.info('Provide an anchors set. The plan view will render here.')

st.subheader('Anchor & pedestal params')
col = st.columns(4)
with col[0]: st.session_state['anchors']['D_mm'] = st.number_input('Anchor diameter (mm)', value=24.0)
with col[1]: st.session_state['anchors']['hef_mm'] = st.number_input('hef (mm)', value=400.0)
with col[2]: st.session_state['anchors']['c_edge_mm'] = st.number_input('Edge distance c (mm)', value=150.0)
with col[3]: st.session_state['anchors']['grade'] = st.selectbox('Bolt grade', ['F1554 Gr.36','F1554 Gr.55','F1554 Gr.105','A307','A193 B7','A449','ISO 8.8','ISO 10.9','A325','A490'], index=1)

st.session_state['anchors']['shear_key'] = st.checkbox('Use shear key (single, central)', value=False)
if st.session_state['anchors']['shear_key']:
    ck = st.columns(5)
    with ck[0]: st.session_state['anchors']['key_b']  = st.number_input('key b (mm)', value=100.0)
    with ck[1]: st.session_state['anchors']['key_h']  = st.number_input('key h (mm)', value=300.0)
    with ck[2]: st.session_state['anchors']['key_hsl']= st.number_input('key embed (hsl, mm)', value=250.0)
    with ck[3]: st.session_state['anchors']['key_eg'] = st.number_input('grout gap eg (mm)', value=50.0)
    with ck[4]: st.session_state['anchors']['key_tw'] = st.number_input('key tw (mm)', value=16.0)