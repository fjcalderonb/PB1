
from pydantic import BaseModel, Field
from typing import Optional

class Concrete(BaseModel):
    fc_MPa: float = Field(..., gt=0)

class PlateSteel(BaseModel):
    fy_MPa: float = Field(..., gt=0)

class AnchorSteel(BaseModel):
    grade: str = "F1554-55"
    fu_MPa: float = 620.0
    fy_MPa: float = 380.0

class Phi(BaseModel):
    anchors_tension: float = 0.75
    anchors_shear: float = 0.65
    bearing_concrete: float = 0.65

class Materials(BaseModel):
    concrete: Concrete
    plate: PlateSteel
    anchors: AnchorSteel
    phi: Phi = Phi()

class Geometry(BaseModel):
    a_mm: float
    b_mm: float
    tp_mm: float

class Loads(BaseModel):
    N_kN: float
    Mx_kNm: float
    My_kNm: float = 0.0
    Vx_kN: float = 0.0
    Vy_kN: float = 0.0

class ColumnFootprint(BaseModel):
    b_col_mm: float = 300.0
    h_col_mm: float = 300.0

class Pedestal(BaseModel):
    use: bool = False
    Bp_mm: float = 0.0
    Lp_mm: float = 0.0
    a2a1_override: Optional[float] = None

class AnchorageConfig(BaseModel):
    n_rows: int = 2
    n_cols: int = 2
    s_x_mm: float = 200.0
    s_y_mm: float = 200.0
    hef_mm: float = 300.0
    conc_thk_mm: float = 500.0
    cracked: bool = True
    anchor_type: str = "headed"
    c_x_left_mm: float = 100.0
    c_x_right_mm: float = 100.0
    c_y_top_mm: float = 100.0
    c_y_bottom_mm: float = 100.0

class Method(BaseModel):
    pressure_case: str = "CASE_1"
    plate_method: str = "ELASTIC"

class Options(BaseModel):
    lrfd: bool = True

class InputData(BaseModel):
    units: str = "SI"
    materials: Materials
    geometry: Geometry
    loads: Loads
    method: Method
    column: ColumnFootprint = ColumnFootprint()
    pedestal: Pedestal = Pedestal()
    anchorage: AnchorageConfig = AnchorageConfig()
    options: Options = Options()
