from .models import InputData
from .units import MPa_to_Pa

def plate_checks(data: InputData, q_max_Pa: float):
    """
    Método 2 mínimo (elástico): compara Mmax ~ q*b*z con M_rd = f_y * W_el
    Simplificado para eje x (Mx) con presión uniforme/rectangular (mejoraremos con integración real).
    """
    fy = data.materials.plate.fy_MPa * 1e6    # Pa
    b = data.geometry.b_mm / 1000.0
    a = data.geometry.a_mm / 1000.0
    tp = data.geometry.tp_mm / 1000.0

    # Momento flector en “canto” al alma (aprox). z ≈ a/4 si bloque rectangular centrado (placeholder)
    z = max(1e-6, a/4.0)
    M_req = q_max_Pa * b * z**2   # N·m (muy conservador; siguiente PR integra q(x))

    # Resistencia sección elástica (f_y * W_el), W_el ≈ b*tp^2/6
    Wel = b * tp**2 / 6.0
    M_rd = fy * Wel

    ratio = M_req / max(M_rd, 1e-9)
    return {"sigma_VM_MPa": fy/1e6, "M_req_kNm": M_req/1e3, "M_rd_kNm": M_rd/1e3,
            "ratio": ratio, "criterion": data.method.plate_method}
