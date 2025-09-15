
from .models import InputData
from math import pi

def _area_bolt_effective_mm2(d_mm: float) -> float:
    d_core = max(1e-3, d_mm - 1.5)
    return pi*(d_core**2)/4.0

def design_anchors_steel(data: InputData, tension_per_bolt_N: float, shear_per_bolt_N: float):
    fu = data.materials.anchors.fu_MPa
    phi_t = data.materials.phi.anchors_tension
    phi_v = data.materials.phi.anchors_shear

    # Approx: take a representative bolt diameter from sidebar (we don't have per-bolt list here)
    # For now, infer from g1/v1 is not possible; assume d_mm=25.4 unless provided elsewhere
    # We'll pass d_mm via options in app; here just require caller to compute Ase
    d_mm = 25.4
    try:
        # If the app attaches d_mm on data.geometry.v1_mm (hack avoided) — keep constant
        pass
    except Exception:
        pass

    Ase_mm2 = _area_bolt_effective_mm2(d_mm)

    Nsa_nom_N = Ase_mm2 * fu
    Nsa_Rd_N  = phi_t * Nsa_nom_N

    Vsa_nom_N = 0.6 * Nsa_nom_N
    Vsa_Rd_N  = phi_v * Vsa_nom_N

    util_N = tension_per_bolt_N / max(Nsa_Rd_N, 1e-9)
    util_V = shear_per_bolt_N   / max(Vsa_Rd_N, 1e-9)
    util_comb = max(util_N + util_V, util_N, util_V)

    return {
        "Ase_mm2": Ase_mm2,
        "phi*Nsa_kN": Nsa_Rd_N/1e3,
        "phi*Vsa_kN": Vsa_Rd_N/1e3,
        "util_tension": util_N,
        "util_shear": util_V,
        "util_combined": util_comb,
        "controlling": "Steel"
    }
