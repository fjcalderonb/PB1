from .models import InputData
from .units import Pa_to_MPa

def plate_checks(data: InputData, q_max_Pa: float):
    # Strip simplificado a lo largo de la dirección a (para tener un W_el base).
    # 2ª iteración: usar tu M1c,max, V1c,max, Z y regiones Roark.
    fy = data.materials.plate.fy_MPa

    # Placeholder de Von Mises (~0.6*fy)
    sigma_vm = 0.6 * fy
    ratio = sigma_vm / fy

    return {
        "sigma_VM_MPa": sigma_vm,
        "ratio": ratio,
        "criterion": data.method.plate_method
    }
