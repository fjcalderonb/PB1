
from math import pi
from domain.models import InputData

def _ase_unc_in2(d_in: float, tpi: float) -> float:
    return (pi/4.0) * (d_in - 0.9743/float(tpi))**2

def ase_from_thread(d_mm: float, tpi: float | None = None, pitch_mm: float | None = None) -> float:
    if tpi:
        d_in = d_mm/25.4
        return _ase_unc_in2(d_in, tpi) * (25.4**2)
    if pitch_mm:
        d_core = max(1e-3, d_mm - 0.9382*pitch_mm)
        return (pi/4.0) * d_core**2
    d_core = max(1e-3, d_mm - 1.5)
    return (pi/4.0) * d_core**2

def design_anchors_steel(data: InputData, tension_per_bolt_N: float, shear_per_bolt_N: float, d_bolt_mm: float = 25.4, tpi: float | None = 13, pitch_mm: float | None = None):
    fu = data.materials.anchors.fu_MPa
    phi_t = data.materials.phi.anchors_tension
    phi_v = data.materials.phi.anchors_shear
    Ase_mm2 = ase_from_thread(d_bolt_mm, tpi=tpi, pitch_mm=pitch_mm)
    Nsa_nom = Ase_mm2 * fu
    Nsa_Rd = phi_t * Nsa_nom
    Vsa_Rd = phi_v * 0.6 * Nsa_nom
    util_N = tension_per_bolt_N / max(Nsa_Rd, 1e-9)
    util_V = shear_per_bolt_N / max(Vsa_Rd, 1e-9)
    util = max(util_N + util_V, util_N, util_V)
    return {"Ase_mm2": Ase_mm2, "phi*Nsa_kN": Nsa_Rd/1e3, "phi*Vsa_kN": Vsa_Rd/1e3, "util_tension": util_N, "util_shear": util_V, "util_combined": util, "controlling": "Steel"}
