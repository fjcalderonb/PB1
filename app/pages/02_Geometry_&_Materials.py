import streamlit as st
import pandas as pd

if 'geom' not in st.session_state: st.session_state['geom']={}
if 'mat' not in st.session_state: st.session_state['mat']={}

st.title('02 · Geometry & Materials')

left, right = st.columns(2)
with left:
    st.subheader('Plate & Column')
    st.session_state['geom']['B'] = st.number_input('Plate B (mm)', value=400.0, step=10.0, min_value=0.0)
    st.session_state['geom']['L'] = st.number_input('Plate L (mm)', value=500.0, step=10.0, min_value=0.0)
    st.session_state['geom']['t'] = st.number_input('Plate thickness t (mm) (0 = compute)', value=0.0, step=1.0, min_value=0.0)
    st.session_state['geom']['t_min'] = st.number_input('t_min (mm)', value=10.0, step=1.0, min_value=0.0)
    st.session_state['geom']['round_5'] = st.checkbox('Round to multiples of 5 mm', value=True)
    st.session_state['geom']['d']  = st.number_input('Column depth d (mm)', value=300.0, step=5.0)
    st.session_state['geom']['bf'] = st.number_input('Column flange bf (mm)', value=200.0, step=5.0)
    st.session_state['geom']['tf'] = st.number_input('Column flange tf (mm)', value=15.0, step=1.0)
    st.session_state['geom']['tw'] = st.number_input('Column web tw (mm)', value=9.0, step=1.0)
with right:
    st.subheader('Materials')
    st.session_state['mat']['fc'] = st.number_input("Concrete f'c (MPa)", value=28.0, step=1.0)
    st.session_state['mat']['fy_plate'] = st.number_input('Plate fy (MPa)', value=250.0, step=10.0)
    st.session_state['mat']['FEXX'] = st.number_input('Weld F_EXX (MPa) – E70XX≈483', value=483.0, step=5.0)
    st.session_state['mat']['cracked'] = st.checkbox('Cracked concrete (default)', value=True)

st.divider()
st.subheader('W-shapes quick selector (auto-fill & editable)')
opt = st.radio('Source', ['Subset (W8–W36)','Upload CSV'], horizontal=True)

if opt.startswith('Subset'):
    df = pd.read_csv('data/shapes/aisc_w_subset.csv')
    sel = st.selectbox('Shape', df['shape'].tolist(), index=1)
    row = df[df['shape']==sel].iloc[0]
    if st.button('Load to inputs'):
        st.session_state['geom']['d'] = float(row['d_mm'])
        st.session_state['geom']['bf']= float(row['bf_mm'])
        st.session_state['geom']['tf']= float(row['tf_mm'])
        st.session_state['geom']['tw']= float(row['tw_mm'])
        st.success(f'Loaded {sel} into column fields (editable).')
else:
    up = st.file_uploader('Upload shapes CSV (shape,d_mm,bf_mm,tf_mm,tw_mm)', type=['csv'])
    if up:
        try:
            df = pd.read_csv(up); st.dataframe(df.head())
        except Exception as e:
            st.error(f'CSV error: {e}')