import math
def contact_pressures(N_kN: float, Mx_kNm: float, My_kNm: float, B_mm: float, L_mm: float):
    if B_mm<=0 or L_mm<=0: return {'A':0,'sigma_max':0,'sigma_min':0,'Mx':0,'My':0}
    A = B_mm*L_mm
    Ix = (B_mm*L_mm**3)/12.0
    Iy = (L_mm*B_mm**3)/12.0
    MxN = (Mx_kNm or 0.0)*1e6
    MyN = (My_kNm or 0.0)*1e6
    sigma0 = (N_kN or 0.0)*1e3 / A
    sx = abs(MxN*(L_mm/2)/Ix)/1e3 if Ix>0 else 0.0
    sy = abs(MyN*(B_mm/2)/Iy)/1e3 if Iy>0 else 0.0
    smax = sigma0 + sx + sy
    smin = sigma0 - sx - sy
    return {'A':A,'sigma_max':smax,'sigma_min':smin,'Ix':Ix,'Iy':Iy}

def plate_t_local(press, bf, tf, tw, B, L, fy_plate, use_stiff, h_stiff, t_stiff, t_min_mm=10.0):
    q = max(press.get('sigma_max',0.0),0.0)  # kN/mm2
    rfac = 0.7 if use_stiff else 1.0
    m1 = max(0.0, (B - bf)/2.0) * rfac
    m2 = max(0.0, (L - (0.8*bf))/2.0) * rfac
    phi = 0.9
    def t_req(m):
        if q<=0 or m<=0: return 0.0
        Mu = q*m**2/2.0  # kN·mm/mm
        return math.sqrt( (6e3*Mu)/(phi*fy_plate) )
    t1 = t_req(m1); t2 = t_req(m2)
    t_req_max = max(t1,t2,t_min_mm)
    return t_req_max, [{'strip':'flange (B)','m_mm':m1,'q':q,'t_req':t1}, {'strip':'web (L)','m_mm':m2,'q':q,'t_req':t2}]

def plate_t_full_section(N_kN, Mx_kNm, My_kNm, B, L, fy_plate, bearing_fc_MPa, t_min_mm=10.0):
    if B<=0 or L<=0: return t_min_mm, {'a_mm':0,'q_max':0}
    A = B*L
    qmean = (N_kN*1e3)/A if A>0 else 0
    q_max = min(qmean*3.0, bearing_fc_MPa/1000.0)  # simplificado
    phi = 0.9
    if q_max<=0: return max(t_min_mm,10.0), {'a_mm':0,'q_max':q_max}
    m = 0.3*min(B,L)  # brazo efectivo simple
    Mu = q_max*m**2/2.0
    t = ((6e3*Mu)/(phi*fy_plate))**0.5
    t = max(t, t_min_mm)
    return t, {'a_mm':m,'q_max':q_max}


# import math
# from typing import Dict

# def compute_contact_pressures(N_kN: float, Mx_kNm: float, My_kNm: float,
#                               B_mm: float, L_mm: float) -> Dict[str,float]:
#     # Guard invalid geometry to avoid ZeroDivisionError
#     if B_mm is None or L_mm is None or B_mm <= 0 or L_mm <= 0:
#         return {
#             'A_mm2': 0.0,
#             'Ix_mm4': 0.0,
#             'Iy_mm4': 0.0,
#             'sigma_mean_kNmm2': 0.0,
#             'sigma_x_kNmm2': 0.0,
#             'sigma_y_kNmm2': 0.0,
#             'sigma_max_kNmm2': 0.0,
#             'sigma_min_kNmm2': 0.0,
#             '_warning': 'Invalid plate dimensions (B or L <= 0).'
#         }
#     A = B_mm*L_mm
#     Ix = (B_mm*L_mm**3)/12.0
#     Iy = (L_mm*B_mm**3)/12.0
#     Mx = (Mx_kNm or 0.0)*1e6
#     My = (My_kNm or 0.0)*1e6
#     sigma0 = (N_kN or 0.0)*1e3 / A
#     sigma_x = Mx * (L_mm/2) / Ix / 1e3
#     sigma_y = My * (B_mm/2) / Iy / 1e3
#     sigma_max = sigma0 + abs(sigma_x) + abs(sigma_y)
#     sigma_min = sigma0 - abs(sigma_x) - abs(sigma_y)
#     return {
#         'A_mm2': A,
#         'Ix_mm4': Ix,
#         'Iy_mm4': Iy,
#         'sigma_mean_kNmm2': sigma0,
#         'sigma_x_kNmm2': sigma_x,
#         'sigma_y_kNmm2': sigma_y,
#         'sigma_max_kNmm2': sigma_max,
#         'sigma_min_kNmm2': sigma_min
#     }

# def plate_local_method(press: Dict[str,float], bf: float, tf: float, tw: float,
#                        B: float, L: float, fy_plate: float,
#                        use_stiff: bool, h_stiff: float, t_stiff: float):
#     # If invalid geometry, return zeros (caller already warned)
#     if B <= 0 or L <= 0:
#         return 0.0, [{'strip':'flange (B)','m_eff_mm':0,'q_kNmm2':0,'t_req_mm':0}, {'strip':'web (L)','m_eff_mm':0,'q_kNmm2':0,'t_req_mm':0}]
#     m1_each = max(0.0, (B - bf)/2.0)
#     m2_each = max(0.0, (L - (0.8*bf)) / 2.0)
#     q = max(press.get('sigma_max_kNmm2',0.0), 0.0)
#     phi = 0.9
#     rfac = 0.7 if use_stiff else 1.0
#     def t_req_from_cantilever(m, q, fy):
#         if m <= 0 or q <= 0:
#             return 0.0
#         Mu = q * m**2 / 2.0
#         t = math.sqrt( (6e3*Mu) / (phi*fy) )
#         return t
#     t1 = t_req_from_cantilever(rfac*m1_each, q, fy_plate)
#     t2 = t_req_from_cantilever(rfac*m2_each, q, fy_plate)
#     t_req = max(t1, t2)
#     strips = [
#         {'strip':'flange (B)', 'm_eff_mm': rfac*m1_each, 'q_kNmm2': q, 't_req_mm': t1},
#         {'strip':'web (L)',    'm_eff_mm': rfac*m2_each, 'q_kNmm2': q, 't_req_mm': t2},
#     ]
#     return t_req, strips
