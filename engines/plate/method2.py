
from domain.models import InputData

def check_plate_method2(data: InputData, q_max_MPa: float):
    fy = data.materials.plate.fy_MPa*1e6
    b = data.geometry.b_mm/1000.0
    a = data.geometry.a_mm/1000.0
    tp = data.geometry.tp_mm/1000.0
    q = q_max_MPa*1e6
    z = max(1e-6, a/4.0)
    M_req = q*b*(z**2)
    W_el = b*(tp**2)/6.0
    M_rd = fy*W_el
    ratio = M_req/max(M_rd, 1e-9)
    return {"M_req_kNm": M_req/1e3, "M_rd_kNm": M_rd/1e3, "ratio": ratio}
