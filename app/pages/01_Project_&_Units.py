
import streamlit as st
if 'cfg' not in st.session_state: st.session_state['cfg'] = {}
st.title("01 · Project & Units")
st.session_state['cfg']['project'] = st.text_input("Project", value=st.session_state['cfg'].get('project','Baseplate I2'))
st.session_state['cfg']['code'] = st.selectbox("Design Code", ["AISC/ACI (US)", "EN 1992-4 (EU)"], index=0)
st.session_state['cfg']['units'] = st.selectbox("Units", ["SI (kN, mm, MPa)", "US (kip, in, ksi)"], index=0)
st.success("Saved in session: project, code and units.")
