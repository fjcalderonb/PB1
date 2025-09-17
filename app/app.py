
import streamlit as st
st.set_page_config(page_title="BasePlate App", layout="wide")
st.title("Base Plate & Anchor Bolts – Prototype I2")
st.markdown(
    """
    **Menu**
    1) Project & Units
    2) Geometry & Materials
    3) Loads & SAP2000 (Single + Batch/Governing I2) — **one upload, two tabs**
    4) Method & Assumptions (with CASE tooltips)
    5) Results – Summary (single case)
    7) Report (PDF)
    """
)
