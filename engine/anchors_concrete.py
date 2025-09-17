
import math

def _area_cone_tension(hef_mm: float, theta_deg: float=35.0) -> float:
    r = hef_mm * math.tan(math.radians(theta_deg))
    return math.pi * r * r

def _area_wedge_shear(hef_mm: float) -> float:
    a = 1.5 * hef_mm
    return a * a

def _phi(failure: str) -> float:
    return {'tension':0.65, 'shear':0.60, 'pullout':0.70}.get(failure, 0.60)

def tension_breakout_draft(fc: float, hef_mm: float, c_edge_mm: float) -> float:
    A = _area_cone_tension(hef_mm)
    psi_edge = min(1.0, max(0.3, c_edge_mm/(1.5*hef_mm)))
    Nn_kN = 0.6*0.85*fc * A / 1000.0
    return _phi('tension') * psi_edge * Nn_kN

def pullout_draft(fc: float, D_mm: float) -> float:
    A_brg = math.pi*(D_mm**2)/4.0
    Nn_kN = 0.5*fc * A_brg / 1000.0
    return _phi('pullout') * Nn_kN

def shear_breakout_draft(fc: float, hef_mm: float, c_edge_mm: float) -> float:
    A = _area_wedge_shear(hef_mm)
    psi_edge = min(1.0, max(0.3, c_edge_mm/(1.5*hef_mm)))
    Vn_kN = 0.6*0.85*fc * A / 1000.0
    return _phi('shear') * psi_edge * Vn_kN

def concrete_checks_draft(fc: float, hef_mm: float, D_mm: float, Nx: float, V: float, c_edge_mm: float):
    phiN_cb = tension_breakout_draft(fc, hef_mm, c_edge_mm)
    phiN_p  = pullout_draft(fc, D_mm)
    phiV_cb = shear_breakout_draft(fc, hef_mm, c_edge_mm)
    return {
        'phiN_cb_kN (draft)': round(phiN_cb,3),
        'phiN_pullout_kN (draft)': round(phiN_p,3),
        'phiV_cb_kN (draft)': round(phiV_cb,3),
        'note': 'Conservative placeholders. Full ACI/EN in I3.'
    }
