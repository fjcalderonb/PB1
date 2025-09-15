
from .models import InputData

def plate_checks(data: InputData, q_max_Pa: float):
    fy = data.materials.plate.fy_MPa
    sigma_vm = 0.6 * fy
    ratio = sigma_vm / fy
    return {"sigma_VM_MPa": sigma_vm, "ratio": ratio, "criterion": data.method.plate_method}
