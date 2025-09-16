
import pandas as pd
from domain.models import InputData
from engines.pressure import pressure_distribution
from engines.anchors.steel import design_anchors_steel
from engines.anchors.concrete import design_anchors_concrete
from engines.plate.method2 import check_plate_method2

def evaluate_row(data_template: InputData, row: dict, mu_fric: float, resist_shear: bool, bolt_count: int, bolt_d_mm: float):
    data = data_template.model_copy(deep=True)
    data.loads.N_kN = float(row.get('N_kN', 0.0))
    data.loads.Vx_kN = float(row.get('Vx_kN', 0.0))
    data.loads.Vy_kN = float(row.get('Vy_kN', 0.0))
    data.loads.Mx_kNm = float(row.get('Mx_kNm', 0.0))
    data.loads.My_kNm = float(row.get('My_kNm', 0.0))
    press = pressure_distribution(data)
    qmax = press.get('sigma_max_MPa', 0.0)
    V_req = abs(data.loads.Vx_kN); N_comp = max(0.0, data.loads.N_kN)
    C_f = 0.0 if resist_shear else (mu_fric*N_comp)
    V_to_bolts = V_req if resist_shear else max(0.0, V_req - C_f)
    n_bolts = max(1, int(bolt_count))
    tpb_N = max(0.0, data.loads.N_kN*1e3)/n_bolts
    spb_N = (V_to_bolts*1e3)/n_bolts
    steel = design_anchors_steel(data, tpb_N, spb_N, d_bolt_mm=bolt_d_mm, tpi=13)
    conc = design_anchors_concrete(data, tpb_N, spb_N)
    plate = check_plate_method2(data, qmax)
    util_anch = max(steel.get('util_combined',0.0), conc.get('util_tension_conc',0.0), conc.get('util_shear_conc',0.0))
    return {'meta': {'Joint': row.get('Joint'), 'OutputCase': row.get('OutputCase')}, 'loads': {'N_kN': data.loads.N_kN, 'Vx_kN': data.loads.Vx_kN, 'Vy_kN': data.loads.Vy_kN, 'Mx_kNm': data.loads.Mx_kNm, 'My_kNm': data.loads.My_kNm}, 'concrete': {**press}, 'anchors': {'util_combined': util_anch, 'steel': steel, 'concrete': conc}, 'plate': plate, 'friction': {'mu': mu_fric, 'Nc_kN': N_comp, 'Cf_kN': C_f, 'V_to_bolts_kN': V_to_bolts}}

def worst_by_discipline(df_std: pd.DataFrame, data_template: InputData, mu_fric: float, resist_shear: bool, bolt_count: int, bolt_d_mm: float):
    results = [evaluate_row(data_template, r.to_dict(), mu_fric, resist_shear, bolt_count, bolt_d_mm) for _, r in df_std.iterrows()]
    if not results: return {'concrete': None, 'anchors': None, 'plate': None, 'all_results': []}
    def pick(key, subkey, maximize=True):
        best = None; best_val = -1e30 if maximize else 1e30
        for res in results:
            val = res[key].get(subkey, 0.0)
            if (maximize and val > best_val) or ((not maximize) and val < best_val): best, best_val = res, val
        return best
    concrete_best = pick('concrete','utilization', True) or pick('concrete','sigma_max_MPa', True)
    anchors_best = pick('anchors','util_combined', True)
    plate_best = pick('plate','ratio', True)
    return {'concrete': concrete_best, 'anchors': anchors_best, 'plate': plate_best, 'all_results': results}
