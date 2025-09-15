from pydantic import BaseModel
from typing import Optional, List

# --- Materiales ---
class Concrete(BaseModel):
    fc_MPa: float

class PlateSteel(BaseModel):
    fy_MPa: float

class AnchorSteel(BaseModel):
    grade: str
    fu_MPa: float
    fy_MPa: float

class PhiFactors(BaseModel):
    anchors_tension: float = 0.75   # ACI 318 LRFD
    anchors_shear: float   = 0.65   # ACI 318 LRFD
    bearing_concrete: float = 0.65  # ACI 318 LRFD

class Materials(BaseModel):
    concrete: Concrete
    plate: PlateSteel
    anchors: AnchorSteel
    phi: PhiFactors = PhiFactors()

# --- Geometría ---
class Geometry(BaseModel):
    a_mm: float
    b_mm: float
    tp_mm: float
    hc_mm: float = 0.0
    bc_mm: float = 0.0
    g1_mm: float = 0.0
    v1_mm: float = 0.0

class AnchorLine(BaseModel):
    index: int
    n_bolts: int
    edge_dist_mm: float
    bolt_d_mm: float
    bolt_d_in: Optional[float] = None

class Anchors(BaseModel):
    lines: List[AnchorLine]
    resist_shear: bool = False  # si Vx/Vy se transfieren por pernos

# --- Cargas y método ---
class Loads(BaseModel):
    N_kN: float
    Mx_kNm: float
    My_kNm: float = 0.0
    Vx_kN: float = 0.0
    Vy_kN: float = 0.0

class Method(BaseModel):
    pressure_case: str  # 'CASE_1','CASE_2','CASE_3','CASE_4'
    plate_method: str   # 'ROARK','ELASTIC','PLASTIC'

class Options(BaseModel):
    lrfd: bool = True

class InputData(BaseModel):
    units: str = "SI"
    materials: Materials
    geometry: Geometry
    anchors: Anchors
    loads: Loads
    method: Method
    options: Options = Options()
