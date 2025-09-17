
import math
from typing import Dict

def compute_contact_pressures(N_kN: float, Mx_kNm: float, My_kNm: float,
                              B_mm: float, L_mm: float) -> Dict[str,float]:
    # Guard invalid geometry to avoid ZeroDivisionError
    if B_mm is None or L_mm is None or B_mm <= 0 or L_mm <= 0:
        return {
            'A_mm2': 0.0,
            'Ix_mm4': 0.0,
            'Iy_mm4': 0.0,
            'sigma_mean_kNmm2': 0.0,
            'sigma_x_kNmm2': 0.0,
            'sigma_y_kNmm2': 0.0,
            'sigma_max_kNmm2': 0.0,
            'sigma_min_kNmm2': 0.0,
            '_warning': 'Invalid plate dimensions (B or L <= 0).'
        }
    A = B_mm*L_mm
    Ix = (B_mm*L_mm**3)/12.0
    Iy = (L_mm*B_mm**3)/12.0
    Mx = (Mx_kNm or 0.0)*1e6
    My = (My_kNm or 0.0)*1e6
    sigma0 = (N_kN or 0.0)*1e3 / A
    sigma_x = Mx * (L_mm/2) / Ix / 1e3
    sigma_y = My * (B_mm/2) / Iy / 1e3
    sigma_max = sigma0 + abs(sigma_x) + abs(sigma_y)
    sigma_min = sigma0 - abs(sigma_x) - abs(sigma_y)
    return {
        'A_mm2': A,
        'Ix_mm4': Ix,
        'Iy_mm4': Iy,
        'sigma_mean_kNmm2': sigma0,
        'sigma_x_kNmm2': sigma_x,
        'sigma_y_kNmm2': sigma_y,
        'sigma_max_kNmm2': sigma_max,
        'sigma_min_kNmm2': sigma_min
    }

def plate_local_method(press: Dict[str,float], bf: float, tf: float, tw: float,
                       B: float, L: float, fy_plate: float,
                       use_stiff: bool, h_stiff: float, t_stiff: float):
    # If invalid geometry, return zeros (caller already warned)
    if B <= 0 or L <= 0:
        return 0.0, [{'strip':'flange (B)','m_eff_mm':0,'q_kNmm2':0,'t_req_mm':0}, {'strip':'web (L)','m_eff_mm':0,'q_kNmm2':0,'t_req_mm':0}]
    m1_each = max(0.0, (B - bf)/2.0)
    m2_each = max(0.0, (L - (0.8*bf)) / 2.0)
    q = max(press.get('sigma_max_kNmm2',0.0), 0.0)
    phi = 0.9
    rfac = 0.7 if use_stiff else 1.0
    def t_req_from_cantilever(m, q, fy):
        if m <= 0 or q <= 0:
            return 0.0
        Mu = q * m**2 / 2.0
        t = math.sqrt( (6e3*Mu) / (phi*fy) )
        return t
    t1 = t_req_from_cantilever(rfac*m1_each, q, fy_plate)
    t2 = t_req_from_cantilever(rfac*m2_each, q, fy_plate)
    t_req = max(t1, t2)
    strips = [
        {'strip':'flange (B)', 'm_eff_mm': rfac*m1_each, 'q_kNmm2': q, 't_req_mm': t1},
        {'strip':'web (L)',    'm_eff_mm': rfac*m2_each, 'q_kNmm2': q, 't_req_mm': t2},
    ]
    return t_req, strips
