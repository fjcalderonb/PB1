
# Base Plate — AISC/ACI (Streamlit) — Iteration 2b (EN)

This drop adds **UI and scaffolding** for:
- **Anchorage & Concrete (ACI 318-19 Ch.17)** — inputs for layout, edges, `hef`, thickness, cracked, anchor type. (*Concrete modes are stubbed for now; next commit will implement equations and validation.*)
- **Plate** — column footprint for Roark local checks (zones) + section-wide EL/PL (scaffold).
- **Pedestal (plinth)** — toggle + dimensions; **A2/A1** auto from plate/pedestal footprints (or manual override).
- SAP importer stays as before (ignores CaseType/StepType) with **Axis & sign mapper** (Preset A/B/Advanced) and **worst-case per discipline**.

> **Disclaimer**: Anchors concrete modes are **placeholders** in this drop to keep UI + data flow consistent. The next PR will implement ACI 318-19 concrete capacities and interactions.

## Run locally
```bat
py -3.11 -m venv .venv
.\.venv\Scriptsctivate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8590
```

## Git — update your repo
```bat
git add .
git commit -m "feat(iter2b): EN UI + pedestal & A2/A1 + anchorage inputs + worst-case flow"
git push
```
