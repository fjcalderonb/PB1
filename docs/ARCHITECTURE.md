# PB1 — Proposed Architecture (vNext)

**Goals**: clean, testable, UI-agnostic core, and ready for PR.

- `domain/` — pure data models & units
- `engines/` — calculation kernels (pressure, anchors, plate)
- `services/` — orchestration (worst-case, mapping)
- `io/` — adapters (SAP2000 import, PDF reports)
- `app/` — Streamlit UI (thin layer)
- `tests/` — pytest unit tests (SAP import, anchors steel, pressure)

**Key defaults**:
- Code: AMERICAN (ACI/AISC)
- SI units
- Shear path: friction by default (anchors do **not** resist shear unless toggled)

**Next steps**:
- Implement full ACI 318-19 Chapter 17 anchor concrete modes
- Plate Method 2 integration of q(x) and Roark zones
- Optional: CLI/BATCH mode & persistence of scenarios