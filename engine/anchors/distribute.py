import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Bolt:
    id: str
    x: float
    y: float
    hole_d: float

def tension_distribution(N_kN: float, Mx_kNm: float, My_kNm: float, bolts: List[Bolt]):
    if not bolts: return {}
    A = len(bolts)
    x = np.array([b.x for b in bolts]); y=np.array([b.y for b in bolts])
    # Coeficientes lineales iniciales y recorte a tracción
    c = N_kN / max(A,1)
    n = c + 0.0*x + 0.0*y
    n = np.maximum(0.0, n)
    s = n.sum()
    if s>1e-9 and N_kN>0: n = n * (N_kN/s)
    return {bolts[i].id: float(n[i]) for i in range(A)}

def shear_distribution(V_kN: float, bolts: List[Bolt], mode: str='ELASTIC'):
    if not bolts: return {}
    n = len(bolts)
    if abs(V_kN)<1e-9: return {b.id: 0.0 for b in bolts}
    if mode.upper().startswith('ELASTIC'):
        xs = np.array([b.x for b in bolts]); ys=np.array([b.y for b in bolts])
        w = np.abs(ys)
        if w.sum()<1e-9: w = np.ones(n)
        v = V_kN * (w / w.sum())
        return {bolts[i].id: float(v[i]) for i in range(n)}
    if mode.endswith('1'):
        return {b.id: float(V_kN/n) for b in bolts}
    if mode.endswith('2') or mode.endswith('3'):
        ys = np.array([b.y for b in bolts])
        far = np.argmax(np.abs(ys)) if mode.endswith('2') else np.argmin(np.abs(ys))
        out = {b.id: 0.0 for b in bolts}
        out[bolts[far].id] = float(V_kN)
        return out
    return {b.id: float(V_kN/n) for b in bolts}