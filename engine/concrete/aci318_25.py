from typing import Dict
import math

# Placeholders de capacidad (prototipo) con phi centralizados (318-25 mueve ϕ a capítulo general)
PHI = {
    'steel_tension': 0.75,
    'steel_shear': 0.65,
    'tension_breakout': 0.75,
    'pullout': 0.75,
    'shear_breakout': 0.65,
    'pryout': 0.65,
    'shear_lug_bearing': 0.65,
    'shear_lug_breakout': 0.65,
}

def tension_breakout_group(fc_MPa: float, hef_mm: float, c_edge_mm: float, n_bolts_tension: int) -> float:
    A = math.pi*(hef_mm*math.tan(math.radians(35.0)))**2
    psi_edge = min(1.0, max(0.3, c_edge_mm/(1.5*hef_mm)))
    Nn_kN = 0.6*0.85*fc_MPa * A / 1000.0
    return PHI['tension_breakout'] * psi_edge * Nn_kN

def pullout(fc_MPa: float, D_mm: float) -> float:
    A_brg = math.pi*(D_mm**2)/4.0
    Nn_kN = 0.5*fc_MPa*A_brg/1000.0
    return PHI['pullout']*Nn_kN

def shear_breakout(fc_MPa: float, hef_mm: float, c_edge_mm: float) -> float:
    a = 1.5*hef_mm
    A = a*a
    psi = min(1.0, max(0.3, c_edge_mm/(1.5*hef_mm)))
    Vn_kN = 0.6*0.85*fc_MPa*A/1000.0
    return PHI['shear_breakout']*psi*Vn_kN

def pryout_from_tension(Ncb_phi_kN: float, kcp: float=2.0) -> float:
    return PHI['pryout']*(kcp/PHI['tension_breakout'])*Ncb_phi_kN