# PB1 — Base Plate (AISC/ACI) — vNext

This package includes a **clean architecture**, a **robust SAP2000 importer**, discipline checks, and **PDF reporting**.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install -r requirements.txt
streamlit run app/app.py
```

## Tests

```bash
pytest -q
```

## Notes
- Anchors **concrete** modes are simplified placeholders; steel checks are implemented with proper thread area (UNC/ISO).
- Pressure/bearing considers confinement via √(A2/A1) with φ.
- Shear-by-friction default (toggle in sidebar).
```