import math

GRADES = {
  'F1554 Gr.36': {'fy': 248, 'fu': 400},
  'F1554 Gr.55': {'fy': 380, 'fu': 620},
  'F1554 Gr.105': {'fy': 724, 'fu': 896},
  'A307': {'fy': 207, 'fu': 414},
  'A193 B7': {'fy': 724, 'fu': 860},
  'A449': {'fy': 620, 'fu': 965},
  'ISO 8.8': {'fy': 640, 'fu': 800},
  'ISO 10.9': {'fy': 900, 'fu': 1040},
  'A325': {'fy': 660, 'fu': 830},
  'A490': {'fy': 940, 'fu': 1040}
}
AREA_THREAD = {16:157, 20:245, 22:303, 24:353, 27:459, 30:561, 33:694, 36:817, 39:956}

def thread_area(D_mm: float) -> float:
    Ag = math.pi*(D_mm**2)/4.0
    return AREA_THREAD.get(int(D_mm), 0.6*Ag)

def steel_tension_capacity(grade: str, D_mm: float):
    fu = GRADES.get(grade, GRADES['F1554 Gr.55'])['fu']
    A_t = thread_area(D_mm); phi = 0.75
    return phi * fu * A_t / 1000.0

def steel_shear_capacity(grade: str, D_mm: float):
    fu = GRADES.get(grade, GRADES['F1554 Gr.55'])['fu']
    A_t = thread_area(D_mm); phi = 0.65
    return phi * 0.6 * fu * A_t / 1000.0