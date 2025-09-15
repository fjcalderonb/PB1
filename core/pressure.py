from .models import InputData
from .units import mm_to_m, kN_to_N, kNm_to_Nm, MPa_to_Pa, Pa_to_MPa
from math import copysign

def _bearing_strength_Pa(fc_MPa: float, phi_c: float, A2_A1: float=1.0):
    # f_jd ≈ φ * 0.85 * f'c * sqrt(A2/A1)  (simplificado)
    return phi_c * 0.85 * MPa_to_Pa(fc_MPa) * (A2_A1 ** 0.5)

def pressure_distribution(data: InputData):
    a = mm_to_m(data.geometry.a_mm)
    b = mm_to_m(data.geometry.b_mm)
    N = kN_to_N(abs(data.loads.N_kN))   # trabajo con compresión positiva
    M = kNm_to_Nm(data.loads.Mx_kNm)

    # Evitar división por cero
    if N <= 1e-6:
        return {"case": data.method.pressure_case, "status":"no-compression", "x_m":0, "sigma_max_MPa":0, "sigma_min_MPa":0}

    e = M / N  # excentricidad respecto al centro (m)
    case = data.method.pressure_case

    # Bearing admisible (simplificado) — 2ª iteración: A2/A1 de plinto o hormigón
    fjd = _bearing_strength_Pa(data.materials.concrete.fc_MPa, data.materials.phi.bearing_concrete)

    # --- Región sin tensión: |e| <= a/6 ---
    if abs(e) <= a/6.0:
        # trapezoidal (aquí calculo extremos equivalentes lineales)
        q0 = N / (a*b)                       # promedio
        dq = 6*e / a * q0                    # variación lineal
        qmax = q0 + dq
        qmin = q0 - dq
        # Límite por bearing
        qmax = min(qmax, fjd)
        return {
            "case": case,
            "status":"no-tension",
            "x_m": a,                         # toda la longitud comprimida
            "sigma_max_MPa": Pa_to_MPa(qmax),
            "sigma_min_MPa": Pa_to_MPa(qmin if qmin>0 else 0.0),
            "e_over_a": e/a
        }

    # --- Con tensión: |e| > a/6 ---
    e_eff = abs(e)   # simetría
    # CASE_1: Triangular por equilibrio (sin tope a priori)
    if case == "CASE_1":
        x = max(1e-9, 3*(a/2.0 - e_eff))
        qmax = 2*N / (b*x)
        qmax = min(qmax, fjd)  # tope de bearing
        return {
            "case": case,
            "status":"tension",
            "x_m": x,
            "sigma_max_MPa": Pa_to_MPa(qmax),
            "sigma_min_MPa": 0.0,
            "e_over_a": e/a
        }

    # CASE_2: Rectangular por equilibrio (sin tope a priori)
    if case == "CASE_2":
        x = max(1e-9, a - 2*e_eff)
        q = N / (b*x)
        q = min(q, fjd)
        return {
            "case": case,
            "status":"tension",
            "x_m": x,
            "sigma_max_MPa": Pa_to_MPa(q),
            "sigma_min_MPa": Pa_to_MPa(q),  # uniforme
            "e_over_a": e/a
        }

    # CASE_3: Rectangular con q = fjd
    if case == "CASE_3":
        # Equilibrio de momentos: a/2 - e = x/2  => x = a - 2e
        x_by_m = max(1e-9, a - 2*e_eff)
        # Equilibrio de fuerzas: N = fjd * b * x  => validar utilización
        N_cap = fjd * b * x_by_m
        util = N / max(N_cap, 1e-9)
        return {
            "case": case,
            "status":"tension",
            "x_m": x_by_m,
            "sigma_max_MPa": Pa_to_MPa(fjd),
            "sigma_min_MPa": Pa_to_MPa(fjd),
            "utilization": util,
            "e_over_a": e/a
        }

    # CASE_4: Triangular con qmax = fjd
    if case == "CASE_4":
        # a/2 - e = x/3  => x = 3*(a/2 - e)
        x_by_m = max(1e-9, 3*(a/2.0 - e_eff))
        N_cap = 0.5 * fjd * b * x_by_m
        util = N / max(N_cap, 1e-9)
        return {
            "case": case,
            "status":"tension",
            "x_m": x_by_m,
            "sigma_max_MPa": Pa_to_MPa(fjd),
            "sigma_min_MPa": 0.0,
            "utilization": util,
            "e_over_a": e/a
        }

    # fallback
    return {"case": case, "status":"tension", "x_m":0, "sigma_max_MPa":0, "sigma_min_MPa":0, "e_over_a": e/a}
