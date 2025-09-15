
from .models import InputData
from .units import mm_to_m, kN_to_N, kNm_to_Nm, MPa_to_Pa, Pa_to_MPa

def _bearing_strength_Pa(fc_MPa: float, phi_c: float, A2_A1: float=1.0):
    return phi_c * 0.85 * MPa_to_Pa(fc_MPa) * (A2_A1 ** 0.5)

def pressure_distribution(data: InputData):
    a = mm_to_m(data.geometry.a_mm)
    b = mm_to_m(data.geometry.b_mm)
    N = kN_to_N(max(0.0, data.loads.N_kN))  # compression >= 0
    M = kNm_to_Nm(data.loads.Mx_kNm)
    case = data.method.pressure_case

    if N <= 1e-9:
        return {"case":case, "status":"no-compression", "x_m":0.0,
                "sigma_max_MPa":0.0, "sigma_min_MPa":0.0, "e_over_a":0.0}

    e = M / max(N,1e-9)
    fjd = _bearing_strength_Pa(data.materials.concrete.fc_MPa, data.materials.phi.bearing_concrete)

    if abs(e) <= a/6.0:
        q0 = N/(a*b)
        dq = 6*e/a * q0
        qmax = min(q0 + dq, fjd)
        qmin = max(0.0, q0 - dq)
        return {"case":case, "status":"no-tension", "x_m":a,
                "sigma_max_MPa":Pa_to_MPa(qmax), "sigma_min_MPa":Pa_to_MPa(qmin),
                "e_over_a": e/a}

    e_eff = abs(e)
    if case == 'CASE_1':
        x = max(1e-9, 3*(a/2.0 - e_eff))
        qmax = min(2*N/(b*x), fjd)
        return {"case":case, "status":"tension", "x_m":x,
                "sigma_max_MPa":Pa_to_MPa(qmax), "sigma_min_MPa":0.0,
                "e_over_a": e/a}
    if case == 'CASE_2':
        x = max(1e-9, a - 2*e_eff)
        q = min(N/(b*x), fjd)
        return {"case":case, "status":"tension", "x_m":x,
                "sigma_max_MPa":Pa_to_MPa(q), "sigma_min_MPa":Pa_to_MPa(q),
                "e_over_a": e/a}
    if case == 'CASE_3':
        x = max(1e-9, a - 2*e_eff)
        N_cap = fjd * b * x
        util = (N/max(1e-9, N_cap))
        return {"case":case, "status":"tension", "x_m":x,
                "sigma_max_MPa":Pa_to_MPa(fjd), "sigma_min_MPa":Pa_to_MPa(fjd),
                "utilization": util, "e_over_a": e/a}
    if case == 'CASE_4':
        x = max(1e-9, 3*(a/2.0 - e_eff))
        N_cap = 0.5 * fjd * b * x
        util = (N/max(1e-9, N_cap))
        return {"case":case, "status":"tension", "x_m":x,
                "sigma_max_MPa":Pa_to_MPa(fjd), "sigma_min_MPa":0.0,
                "utilization": util, "e_over_a": e/a}

    return {"case":case, "status":"tension", "x_m":0.0,
            "sigma_max_MPa":0.0, "sigma_min_MPa":0.0, "e_over_a": e/a}
