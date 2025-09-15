import pandas as pd
from .models import InputData
from .pressure import pressure_distribution
from .anchors_steel import design_anchors_steel        # <— usar módulo steel
from .plate import plate_checks

def find_worst_cases(data_template: InputData, df_std: pd.DataFrame,
                     mu_friction: float, case: str, plate_method: str):
    """
    Devuelve el peor por disciplina con la convención:
    – Fricción primero; lo que no cubra la fricción va a pernos si 'Anchors resist shear' está OFF en la UI.
    (Acá asumimos QUE NO resisten cortante; si en UI está ON, pasa V_to_bolts = Vreq)
    """
    import copy
    best = {
        'Concreto': {'util': -1, 'row': None, 'press': None},
        'Pernos':   {'util': -1, 'row': None, 'anch': None},
        'Placa':    {'util': -1, 'row': None, 'plate': None},
    }
    for _, r in df_std.iterrows():
        d = copy.deepcopy(data_template)
        d.loads.N_kN  = float(r['N_kN'])
        d.loads.Vx_kN = float(r['Vx_kN'])
        d.loads.Vy_kN = float(r.get('Vy_kN', 0.0))
        d.loads.Mx_kNm= float(r['Mx_kNm'])
        d.loads.My_kNm= float(r.get('My_kNm', 0.0))
        d.method.pressure_case = case
        d.method.plate_method  = plate_method

        # — Concreto
        press = pressure_distribution(d)
        util_c = float(press.get('utilization', 0.0))
        if util_c >= best['Concreto']['util']:
            best['Concreto'] = {'util': util_c, 'row': r.to_dict(), 'press': press}

        # — Fricción → pernos (por defecto en tu app: pernos NO resisten cortante)
        Nc_kN = max(0.0, d.loads.N_kN)
        Cf_kN = mu_friction * Nc_kN
        Vreq_kN = abs(d.loads.Vx_kN)
        V_to_bolts_kN = max(0.0, Vreq_kN - Cf_kN)

        n_bolts = max(1, d.anchorage.n_rows * d.anchorage.n_cols)
        tpb_N = max(0.0, -d.loads.N_kN)*1e3 / n_bolts  # tensión solo si N < 0
        spb_N = V_to_bolts_kN*1e3 / n_bolts

        anch = design_anchors_steel(d, tpb_N, spb_N, d_bolt_mm=25.4, tpi=13)
        anch['V_to_bolts_kN'] = V_to_bolts_kN
        anch['Cf_kN'] = Cf_kN
        util_a = float(anch.get('util_combined', 0.0))
        if util_a >= best['Pernos']['util']:
            best['Pernos'] = {'util': util_a, 'row': r.to_dict(), 'anch': anch}

        # — Placa (Método 2 mínimo: placeholder mejorado)
        plate = plate_checks(d, q_max_Pa=press.get('sigma_max_MPa', 0.0)*1e6)
        util_p = float(plate.get('ratio', 0.0))
        if util_p >= best['Placa']['util']:
            best['Placa'] = {'util': util_p, 'row': r.to_dict(), 'plate': plate}

    return best
