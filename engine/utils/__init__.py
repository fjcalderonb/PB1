import json
import pandas as pd

# --- Case classification (ULS/SLS) ---
ULS_TOKENS = ['ULS','ULT','ULTIMATE','LRFD','FACT','STR','EQU']
SLS_TOKENS = ['SLS','SERV','SERVICE','ASD','SVC']

def classify_case(name: str) -> str:
    s = (name or '').upper()
    if any(t in s for t in ULS_TOKENS): return 'ULS'
    if any(t in s for t in SLS_TOKENS): return 'SLS'
    return 'UNKNOWN'

# --- Rounding & seismic ---
def round_to_5(x: float) -> float:
    return 5.0 * round((x or 0.0)/5.0)

def apply_seismic_omega(demand_kN: float, seismic_on: bool, omega0: float=2.5) -> float:
    return float(demand_kN * (omega0 if seismic_on else 1.0))

# --- Save/Load project (JSON) ---
def save_project_json(state: dict) -> bytes:
    clean = {}
    for k,v in state.items():
        try:
            json.dumps(v)
            clean[k]=v
        except Exception:
            pass
    return json.dumps(clean, indent=2).encode('utf-8')

def load_project_json(file_bytes: bytes) -> dict:
    try:
        return json.loads(file_bytes.decode('utf-8'))
    except Exception:
        return {}
    

# --- EXISTENTES: classify_case, round_to_5, apply_seismic_omega, save/load (déjalas como las tienes) ---

def to_arrow_compatible(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una copia 'safe' para Streamlit/Arrow:
      - Columnas object con mezcla bytes/float -> str
      - Columnas 'Unnamed' vacías -> drop
    No altera 'df' original (útil si luego calculas con numéricos).
    """
    dfx = df.copy()
    drop_cols = []
    for c in dfx.columns:
        if str(c).lower().startswith('unnamed'):
            if dfx[c].isna().all() or (dfx[c].astype(str).str.strip()=='').all():
                drop_cols.append(c)
                continue
        if dfx[c].dtype == 'object':
            # Si hay mezcla de tipos raros, fuerzo a str
            try:
                _ = dfx[c].values.astype('S')  # prueba bytes
                # si no lanza, convierto a str para evitar ArrowTypeError
                dfx[c] = dfx[c].astype(str)
            except Exception:
                # Si hay floats mezclados con strings, convierto todo a str
                dfx[c] = dfx[c].astype(str)
    if drop_cols:
        dfx = dfx.drop(columns=drop_cols)
    return dfx
