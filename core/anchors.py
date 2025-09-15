from .models import InputData
from math import pi

def _area_bolt_effective_mm2(d_mm: float) -> float:
    # Ase ~ área efectiva por rosca (aprox). 2ª iteración: tabla por norma
    # Aquí uso área de núcleo aproximada: π*(d-Δ)^2/4. Tomo Δ≈1.5 mm como placeholder.
    d_core = max(1e-3, d_mm - 1.5)
    return pi*(d_core**2)/4.0

def design_anchors(data: InputData, tension_per_bolt_N: float, shear_per_bolt_N: float):
    # Solo acero en esta iteración
    fu = data.materials.anchors.fu_MPa  # MPa
    phi_t = data.materials.phi.anchors_tension
    phi_v = data.materials.phi.anchors_shear

    # Tomo línea 1 como representativa
    line = data.anchors.lines[0]
    Ase_mm2 = _area_bolt_effective_mm2(line.bolt_d_mm)

    # Tensión acero (ACI 318 Ch.17 ~ Ase * futa)
    Nsa_nom_N = Ase_mm2 * fu * 1e6 / 1e6   # (MPa*mm2 => N)
    Nsa_Rd_N  = phi_t * Nsa_nom_N

    # Cortante acero (ACI 318 Ch.17 usa ~0.6*futa*Ase en cizalla pura)
    Vsa_nom_N = 0.6 * Nsa_nom_N
    Vsa_Rd_N  = phi_v * Vsa_nom_N

    util_N = tension_per_bolt_N / max(Nsa_Rd_N, 1e-9)
    util_V = shear_per_bolt_N   / max(Vsa_Rd_N, 1e-9)

    # Interacción simple (placeholder) — 2ª iteración: interacción ACI y modos de concreto
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
