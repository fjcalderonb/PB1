import math
def fillet_strength(FEXX_MPa: float=483.0):
    Rn_per_mm = 0.6*FEXX_MPa*0.707/1000.0
    phi = 0.75
    return phi, Rn_per_mm

def required_fillet_size(Vx: float, Vy: float, Mx: float, My: float, d: float, bf: float, phi: float, Rn_per_mm: float):
    V = (Vx**2+Vy**2)**0.5
    Lw = 2.0*(d+bf)
    v = V/max(1.0,Lw)
    v *= 1.2  # factor simplicado
    return math.ceil(v/max(phi*Rn_per_mm,1e-6))