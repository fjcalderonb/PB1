
import pandas as pd
from .models import InputData
from .pressure import pressure_distribution
from .anchors_steel import design_anchors_steel
from .anchors_concrete import design_anchors_concrete_stub


def evaluate_row(data_template: InputData, row: dict, mu_fric: float, resist_shear: bool, bolt_count:int, bolt_d_mm: float):
    data = data_template.model_copy(deep=True)
    data.loads.N_kN  = float(row.get('N_kN', 0.0))
    data.loads.Vx_kN = float(row.get('Vx_kN', 0.0))
    data.loads.Vy_kN = float(row.get('Vy_kN', 0.0))
    data.loads.Mx_kNm= float(row.get('Mx_kNm', 0.0))
    data.loads.My_kNm= float(row.get('My_kNm', 0.0))

    press = pressure_distribution(data)
    sigma_max = press.get('sigma_max_MPa', 0.0)

    # Shear path
    V_req = abs(data.loads.Vx_kN)
    N_comp = max(0.0, data.loads.N_kN)
    C_f = 0.0 if resist_shear else (mu_fric * N_comp)
    if resist_shear:
        V_to_bolts = V_req; Cf_util = 0.0
    else:
        if V_req <= C_f:
            V_to_bolts = 0.0; Cf_util = V_req/max(C_f, 1e-9)
        else:
            V_to_bolts = V_req - C_f; Cf_util = 1.0

    n_bolts = max(1, int(bolt_count))
    tpb_N = max(0.0, data.loads.N_kN*1e3)/n_bolts  # placeholder distribution
    spb_N = (V_to_bolts*1e3)/n_bolts

    steel = design_anchors_steel(data, tpb_N, spb_N)
    conc  = design_anchors_concrete_stub(data, tpb_N, spb_N)

    anchors_util = max(steel.get('util_combined',0.0), conc.get('util_tension_conc',0.0), conc.get('util_shear_conc',0.0))

    return {
        'meta': {'Joint': row.get('Joint'), 'OutputCase': row.get('OutputCase')},
        'loads': {'N_kN': data.loads.N_kN, 'Vx_kN': data.loads.Vx_kN, 'Vy_kN': data.loads.Vy_kN,
                  'Mx_kNm': data.loads.Mx_kNm, 'My_kNm': data.loads.My_kNm},
        'concrete': {'sigma_max_MPa': sigma_max, 'score': sigma_max, 'A2_A1': press.get('A2_A1')},
        'anchors':  {'util_combined': anchors_util, 'steel': steel, 'concrete': conc},
        'plate':    {'ratio': 0.6},  # placeholder; Roark to be added next
        'friction': {'mu': mu_fric, 'Nc_kN': N_comp, 'Cf_kN': C_f, 'V_to_bolts_kN': V_to_bolts, 'util': Cf_util},
    }


def worst_by_discipline(df_std: pd.DataFrame, data_template: InputData, mu_fric: float, resist_shear: bool, bolt_count:int, bolt_d_mm:float):
    results = []
    for _, r in df_std.iterrows():
        results.append(evaluate_row(data_template, r.to_dict(), mu_fric, resist_shear, bolt_count, bolt_d_mm))

    if not results:
        return {'concrete': None, 'anchors': None, 'plate': None, 'all_results': []}

    def pick(key, subkey, maximize=True):
        best = None
        best_val = -1e30 if maximize else 1e30
        for res in results:
            val = res[key][subkey]
            if (maximize and val > best_val) or ((not maximize) and val < best_val):
                best = res; best_val = val
        return best

    return {
        'concrete': pick('concrete','score', True),
        'anchors':  pick('anchors','util_combined', True),
        'plate':    pick('plate','ratio', True),
        'all_results': results,
    }
