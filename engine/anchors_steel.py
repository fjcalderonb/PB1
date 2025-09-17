
import math

GRADE_MAP = {
    'F1554 Gr.36': {'fy': 248, 'fu': 400},
    'F1554 Gr.55': {'fy': 380, 'fu': 620},
    'F1554 Gr.105': {'fy': 724, 'fu': 896},
    'A307': {'fy': 207, 'fu': 414},
    'A193 B7': {'fy': 724, 'fu': 860},
    'A449': {'fy': 620, 'fu': 965},
    'ISO 8.8': {'fy': 640, 'fu': 800},
    'ISO 10.9': {'fy': 900, 'fu': 1040},
}

AREA_THREAD = {16:157, 20:245, 22:303, 24:353, 27:459, 30:561, 33:694, 36:817, 39:956}

def bolt_grade_props(grade_label: str):
    d = GRADE_MAP.get(grade_label, GRADE_MAP['F1554 Gr.55'])
    return d['fu'], d['fy']

def area_thread_mm2(D_mm: float) -> float:
    Ag = math.pi*(D_mm**2)/4.0
    return AREA_THREAD.get(int(D_mm), 0.6*Ag)

def friction_capacity(mu: float, N_kN: float) -> float:
    return max(0.0, mu * max(N_kN, 0.0))

def anchor_steel_checks_dist(N_kN: float, V_kN: float, n_rows: int, bolts_per_row: int, case_sel: str,
                             fu_MPa: float=400.0, D_mm: float=24.0):
    A_t = area_thread_mm2(D_mm)
    phi_t = 0.75
    phi_v = 0.65
    Nsa = phi_t * fu_MPa * A_t / 1000.0
    Vsa = phi_v * 0.6 * fu_MPa * A_t / 1000.0

    total_bolts = max(1, n_rows*bolts_per_row)
    N_per_bolt = max(0.0, -min(0.0, N_kN)) / total_bolts

    cases = [1,2,3] if case_sel.startswith('Auto') else [int(case_sel.split()[-1])]
    util_max = 0.0
    info = {}
    for c in cases:
        V_rows = [0.0]*n_rows
        if c == 1:
            for i in range(n_rows): V_rows[i] = V_kN / n_rows
        elif c == 2:
            V_rows[-1] = V_kN
        elif c == 3:
            V_rows[0] = V_kN
        util_case = 0.0
        gov_row = None
        gov_v_per_bolt = 0.0
        for i, Vrow in enumerate(V_rows):
            V_per_bolt = Vrow / max(1, bolts_per_row)
            util = (N_per_bolt/max(Nsa,1e-6)) + (V_per_bolt/max(Vsa,1e-6))
            if util > util_case:
                util_case = util
                gov_row = i
                gov_v_per_bolt = V_per_bolt
        info[f'CASE {c}'] = {'util_case': util_case, 'governing_row': gov_row, 'V_row_kN': V_rows, 'V_per_bolt_governing_kN': gov_v_per_bolt}
        util_max = max(util_max, util_case)

    return {'util_max': util_max, 'envelope': info, 'N_per_bolt_kN': N_per_bolt, 'phiNsa_kN': Nsa, 'phiVsa_kN': Vsa, 'D_mm': D_mm, 'fu_MPa': fu_MPa}
