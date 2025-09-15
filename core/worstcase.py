
import pandas as pd
from .models import InputData
from .pressure import pressure_distribution
from .anchors import design_anchors
from .plate import plate_checks
from .units import kN_to_N


def find_worst_cases(data_template: InputData, df_std: pd.DataFrame, mu_friction: float, case: str, plate_method: str):
    """
    Recorre TODAS las filas (todos los joints/casos) y devuelve el peor por disciplina.
    - data_template: InputData con materiales/geom/anchors ya configurados (se clonará cargas/métodos)
    - df_std: DataFrame mapeado con columnas N_kN, Vx_kN, Vy_kN, Mx_kNm, My_kNm, Joint, OutputCase, StepType
    - mu_friction: coeficiente de fricción en interfaz (si NO resisten cortante los pernos)
    - case: 'CASE_1'..'CASE_4'
    - plate_method: 'ROARK'|'ELASTIC'|'PLASTIC'
    Retorna dict con los peores (Concrete/Pernos/Placa), cada uno con fila y resultados.
    """
    # helpers para clonar
    import copy

    best = {
        'Concreto': {'util': -1, 'row': None, 'press': None},
        'Pernos':   {'util': -1, 'row': None, 'anch': None},
        'Placa':    {'util': -1, 'row': None, 'plate': None},
    }

    for _, r in df_std.iterrows():
        d = copy.deepcopy(data_template)
        # set loads & methods
        d.loads.N_kN = float(r['N_kN'])
        d.loads.Vx_kN = float(r['Vx_kN'])
        d.loads.Vy_kN = float(r.get('Vy_kN', 0.0))
        d.loads.Mx_kNm = float(r['Mx_kNm'])
        d.loads.My_kNm = float(r.get('My_kNm', 0.0))
        d.method.pressure_case = case
        d.method.plate_method = plate_method

        # --- Concrete ---
        press = pressure_distribution(d)
        util_c = float(press.get('utilization', 0.0))
        if util_c >= best['Concreto']['util']:
            best['Concreto'] = {'util': util_c, 'row': r.to_dict(), 'press': press}

        # --- Shear path: friction first (per your rule)
        N_c = max(0.0, d.loads.N_kN)  # compresión positiva (kN)
        Cf_kN = mu_friction * N_c
        V_req_kN = abs(d.loads.Vx_kN)
        V_to_bolts_kN = max(0.0, V_req_kN - Cf_kN)

        # reparto a pernos (uniforme por ahora)
        nbolts = max(1, d.anchors.lines[0].n_bolts)
        anch = design_anchors(d, tension_per_bolt_N= max(0.0, -d.loads.N_kN)*1e3 / nbolts,
                                 shear_per_bolt_N= V_to_bolts_kN*1e3 / nbolts)
        util_a = float(anch.get('util_combined', 0.0))
        if util_a >= best['Pernos']['util']:
            b = {'util': util_a, 'row': r.to_dict(), 'anch': anch}
            b['anch']['V_to_bolts_kN'] = V_to_bolts_kN
            b['anch']['Cf_kN'] = Cf_kN
            best['Pernos'] = b

        # --- Plate ---
        plate = plate_checks(d, q_max_Pa=press.get('sigma_max_MPa',0.0)*1e6)
        util_p = float(plate.get('ratio', 0.0))
        if util_p >= best['Placa']['util']:
            best['Placa'] = {'util': util_p, 'row': r.to_dict(), 'plate': plate}

    return best
