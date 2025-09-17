
import streamlit as st
if 'assump' not in st.session_state: st.session_state['assump'] = {}
st.title("04 · Method & Assumptions")
st.session_state['assump']['method'] = st.selectbox("Plate design method", ["Local (DG1)", "Full section (coming)"] , index=0)
st.session_state['assump']['mu'] = st.number_input("Friction μ (grout)", value=0.45, min_value=0.0, max_value=1.0, step=0.05)
st.session_state['assump']['use_friction'] = st.checkbox("Consider friction (reduces V)", value=True)
col = st.columns([1,3])
with col[0]: st.markdown("**Shear CASE (ACI)**")
with col[1]:
    with st.popover("ℹ️ CASE help with sketches"):
        st.markdown("""
        **CASE 1 – Uniform** (all rows share V):
        ```
        ↑ V
        [● ●]  Row 1
        [● ●]  Row 2
        [● ●]  Row 3   ← V/3 each
        ```
        **CASE 2 – Far row** (all V to far row):
        ```
        ↑ V → far row
        [○ ○]  Row 1
        [○ ○]  Row 2
        [● ●]  Row 3   ← all V
        ```
        **CASE 3 – Near row** (all V to near row):
        ```
        ↑ V → near row
        [● ●]  Row 1   ← all V
        [○ ○]  Row 2
        [○ ○]  Row 3
        ```
        """)
if st.session_state.get('cfg',{}).get('code','AISC/ACI (US)').startswith('AISC'):
    st.session_state['assump']['case'] = st.selectbox("Select CASE (ACI)", ["Auto (1/2/3)", "CASE 1", "CASE 2", "CASE 3"], index=0)
else:
    st.session_state['assump']['case'] = 'CASE 3'
st.success("Assumptions saved.")
