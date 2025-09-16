
from domain.models import InputData

def design_anchors_concrete(data: InputData, tension_per_bolt_N: float, shear_per_bolt_N: float):
    # Placeholder finite capacities
    fc = data.materials.concrete.fc_MPa
    hef = data.anchorage.hef_mm/1000.0
    n = max(1, data.anchorage.n_rows*data.anchorage.n_cols)
    kN = 1e-3
    Ncb_Rd = 0.65 * 24.0*(fc**0.5)*(hef**1.5)*1e6
    Vcb_Rd = 0.65 * 18.0*(fc**0.5)*(hef**1.5)*1e6
    util_t = (tension_per_bolt_N*n) / max(Ncb_Rd, 1e-9)
    util_v = (shear_per_bolt_N*n) / max(Vcb_Rd, 1e-9)
    return {"phi*Ncb_kN": Ncb_Rd*kN, "phi*Vcb_kN": Vcb_Rd*kN, "util_tension_conc": util_t, "util_shear_conc": util_v, "note": "Simplified placeholder"}
