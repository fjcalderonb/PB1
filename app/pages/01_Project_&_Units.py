import streamlit as st
from engine.utils import save_project_json, load_project_json

if 'cfg' not in st.session_state: st.session_state['cfg']={}
st.title('01 · Project & Units')

cl, cr = st.columns([2,1])
with cl:
    st.session_state['cfg']['project'] = st.text_input('Project', st.session_state['cfg'].get('project','Baseplate I3'))
    st.session_state['cfg']['code'] = st.selectbox('Design Code', ['AISC/ACI (US)'], index=0)
    st.session_state['cfg']['units'] = st.selectbox('Units', ['SI (kN, mm, MPa)'], index=0)
    st.session_state['cfg']['seismic_on'] = st.checkbox('Seismic ON (apply Ω₀ to anchor demands)', value=False)
    st.session_state['cfg']['omega0'] = st.number_input('Ω₀ (seismic overstrength)', value=2.5, step=0.1)
with cr:
    st.download_button('💾 Save project (.json)', data=save_project_json(st.session_state), file_name='project_i3.json', mime='application/json')
    up = st.file_uploader('⬆️ Load project (.json)', type=['json'])
    if up:
        data = load_project_json(up.read())
        st.session_state.update(data)
        st.success('Project loaded into session.')