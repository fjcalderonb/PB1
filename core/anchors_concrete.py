
from .models import InputData

# NOTE: This is a SCAFFOLD. ACI 318-19 Chapter 17 equations for concrete modes
# (N_cb, N_pn, N_sb, V_cb, V_cp, etc.) will be implemented in the next commit.
# Here we return a neutral/high capacity so concrete does not control yet.

def design_anchors_concrete_stub(data: InputData, tension_per_bolt_N: float, shear_per_bolt_N: float):
    return {
        "phi*Ncb_kN": 1e9,   # placeholder very large
        "phi*Npn_kN": 1e9,
        "phi*Nsb_kN": 1e9,
        "phi*Vcb_kN": 1e9,
        "phi*Vcp_kN": 1e9,
        "util_tension_conc": 0.0,
        "util_shear_conc": 0.0,
        "note": "Concrete modes not implemented yet (stub)."
    }
