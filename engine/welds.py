
import math

def fillet_weld_strength(F_EXX_MPa: float):
    Rn_per_mm = 0.6*F_EXX_MPa*0.707/1000.0
    phi = 0.75
    return phi, Rn_per_mm

def suggest_weld_size(Vx: float, Vy: float, Mx: float, My: float, d: float, bf: float,
                       phi: float, Rn_per_mm: float) -> float:
    V = (Vx**2 + Vy**2)**0.5
    Lw = 2.0*(d + bf)
    v_per_mm = V / max(Lw,1.0)
    v_per_mm *= 1.2
    w_req = v_per_mm / max(phi*Rn_per_mm, 1e-6)
    return math.ceil(w_req)
