
import pandas as pd
from .models import InputData
from .pressure import pressure_distribution
from .anchors import design_anchors
from .plate import plate_checks


def evaluate_row(data_template: InputData, row: dict, mu_fric: float, resist_shear: bool):
    """Evaluate one combination row. row must include N_kN, Vx_kN, Vy_kN, Mx_kNm, My_kNm.
    Returns a dict with meta, loads, and discipline metrics.
    """
    data = data_template.model_copy(deep=True)
    data.loads.N_kN  = float(row.get('N_kN', 0.0))
    data.loads.Vx_kN = float(row.get('Vx_kN', 0.0))
    data.loads.Vy_kN = float(row.get('Vy_kN', 0.0))
    data.loads.Mx_kNm= float(row.get('Mx_kNm', 0.0))
    data.loads.My_kNm= float(row.get('My_kNm', 0.0))

    press = pressure_distribution(data)
    sigma_max = press.get('sigma_max_MPa', 0.0)

    # Shear by friction (if not resist_shear)
    V_req = abs(data.loads.Vx_kN)  # next iteration: Vequiv
    N_comp = max(0.0, data.loads.N_kN)
    C_f = 0.0 if resist_shear else (mu_fric * N_comp)

    if resist_shear:
        V_to_bolts = V_req
        Cf_util = 0.0
    else:
        if V_req <= C_f:
            V_to_bolts = 0.0
            Cf_util = V_req/max(C_f, 1e-9)
        else:
            V_to_bolts = V_req - C_f
            Cf_util = 1.0

    # Simple distribution to bolts (placeholder)
    n_bolts = max(1, data.anchors.lines[0].n_bolts)
    tension_per_bolt_N = max(0.0, data.loads.N_kN*1e3) / n_bolts
    shear_per_bolt_N   = (V_to_bolts*1e3) / n_bolts

    anch = design_anchors(data, tension_per_bolt_N, shear_per_bolt_N)
    plate = plate_checks(data, q_max_Pa=sigma_max*1e6)

    return {
        'meta': {
            'Joint': row.get('Joint'),
            'OutputCase': row.get('OutputCase'),
        },
        'loads': {
            'N_kN': data.loads.N_kN, 'Vx_kN': data.loads.Vx_kN, 'Vy_kN': data.loads.Vy_kN,
            'Mx_kNm': data.loads.Mx_kNm, 'My_kNm': data.loads.My_kNm,
        },
        'concrete': {'sigma_max_MPa': sigma_max, 'score': sigma_max},
        'anchors':  {'util_combined': anch.get('util_combined', 0.0), 'util_tension': anch.get('util_tension',0.0), 'util_shear': anch.get('util_shear',0.0)},
        'plate':    {'ratio': plate.get('ratio', 0.0)},
        'friction': {'mu': mu_fric, 'Nc_kN': N_comp, 'Cf_kN': C_f, 'V_to_bolts_kN': V_to_bolts, 'util': Cf_util},
    }


def worst_by_discipline(df_std: pd.DataFrame, data_template: InputData, mu_fric: float, resist_shear: bool):
    results = []
    for _, r in df_std.iterrows():
        results.append(evaluate_row(data_template, r.to_dict(), mu_fric, resist_shear))

    if not results:
        return {'concrete': None, 'anchors': None, 'plate': None, 'all_results': []}

    def pick(key, subkey, maximize=True):
        best = None
        best_val = -1e30 if maximize else 1e30
        for res in results:
            val = res[key][subkey]
            if (maximize and val > best_val) or ((not maximize) and val < best_val):
                best = res
                best_val = val
        return best

    return {
        'concrete': pick('concrete','score', True),
        'anchors':  pick('anchors','util_combined', True),
        'plate':    pick('plate','ratio', True),
        'all_results': results,
    }
