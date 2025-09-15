from .models import InputData
from math import pi

def _ase_unc_in2(d_in: float, tpi: float) -> float:
    """A_se,N (in^2) per ASME B1.1: A = π/4 * (d - 0.9743/n)^2"""
    return (pi/4.0) * (d_in - 0.9743/float(tpi))**2

def ase_from_thread(d_mm: float, tpi: float | None = None, pitch_mm: float | None = None) -> float:
    """
    Devuelve A_se,N en mm^2. Para AMERICAN (UNC) usa TPI; para métrico usa paso (pitch).
    """
    if tpi:  # UNC
        d_in = d_mm / 25.4
        a_in2 = _ase_unc_in2(d_in, tpi)
        return a_in2 * (25.4**2)
    if pitch_mm:  # ISO (aprox): A ≈ π/4 * (d - 0.9382*p)^2  (aproximación)
        d_core = max(1e-3, d_mm - 0.9382 * pitch_mm)
        return (pi/4.0) * d_core**2
    # fallback conservador (igual a tu versión previa pero explícito)
    d_core = max(1e-3, d_mm - 1.5)
    return (pi/4.0) * d_core**2

def design_anchors_steel(
    data: InputData,
    tension_per_bolt_N: float,
    shear_per_bolt_N: float,
    d_bolt_mm: float = 25.4,
    tpi: float | None = 13,         # UNC 1", 13 TPI por defecto (ajústalo en la UI si usas otra rosca)
    pitch_mm: float | None = None
):
    fu = data.materials.anchors.fu_MPa      # ACI 318-19 §17.6.1.2 usa fu y A_se,N
    phi_t = data.materials.phi.anchors_tension
    phi_v = data.materials.phi.anchors_shear

    Ase_mm2 = ase_from_thread(d_bolt_mm, tpi=tpi, pitch_mm=pitch_mm)
    Nsa_nom_N = Ase_mm2 * fu * 1e6 / 1e6  # (mm2 * MPa) -> N
    Nsa_Rd_N  = phi_t * Nsa_nom_N

    # Resistencia a cortante del acero: ACI permite usar modelos de acero con φ (referencia de proyecto).
    # Usamos la práctica de Vsa_nom ≈ 0.6 * Nsa_nom (referencia de diseño de anclajes dúctiles).
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
        "controlling": "Steel (ACI 318-19 §17.6.1.2)"
    }
