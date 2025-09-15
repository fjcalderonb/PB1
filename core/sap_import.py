# core/sap_import.py
import pandas as pd
from pathlib import Path
import re

def _load_raw(_file) -> pd.DataFrame:
    # Lee sin encabezado; trabajaremos con filas crudas
    if hasattr(_file, 'read') and not isinstance(_file, (str, bytes, Path)):
        name = getattr(_file, 'name', 'uploaded')
        if str(name).lower().endswith('.csv'):
            return pd.read_csv(_file, header=None, dtype=str, engine='python', on_bad_lines='skip')
        return pd.read_excel(_file, header=None, dtype=str, engine='openpyxl')
    path = Path(_file)
    if path.suffix.lower() == '.csv':
        return pd.read_csv(path, header=None, dtype=str, engine='python', on_bad_lines='skip')
    return pd.read_excel(path, header=None, dtype=str, engine='openpyxl')

def _find_header_row(df_raw: pd.DataFrame) -> int | None:
    """
    Encuentra la fila que parece contener los nombres de columnas:
    buscamos al menos 'OutputCase' (o 'Case') y las fuerzas/momentos 'F1..F3','M1..M3'.
    """
    needed_any = {'outputcase','case'}
    needed_forces = {'f1','f2','f3','m1','m2','m3'}
    max_scan = min(20, len(df_raw))
    for i in range(max_scan):
        row_vals = df_raw.iloc[i].astype(str).str.strip()
        lower = set(v.lower() for v in row_vals if v and v != 'nan')
        if (lower & needed_any) and (needed_forces.issubset(lower)):
            return i
    # fallback: si vemos fuerzas completas en una fila
    for i in range(max_scan):
        row_vals = df_raw.iloc[i].astype(str).str.strip()
        lower = set(v.lower() for v in row_vals if v and v != 'nan')
        if {'f1','f2','f3','m1','m2','m3'}.issubset(lower):
            return i
    return None


# Detecta fila de unidades (p.ej. 'Text', 'kN', 'kN-m', 'kN·m', 'kN*m'), sin grupos de captura.
_UNITS_RE = re.compile(r'(?i)\b(?:text|kn|kn[-·*]?m)\b')

def _maybe_units_row(s: pd.Series) -> bool:
    # s: una fila (Series). Convertimos todo a str y verificamos con regex compilado.
    txt = s.astype(str)
    return bool(txt.str.contains(_UNITS_RE, regex=True, na=False).any())


def _choose_col(cols, preferred: tuple[str, ...]) -> str | None:
    # prioriza nombres exactos; si no, busca por coincidencias parciales
    lowmap = {str(c): str(c).strip().lower() for c in cols}
    inv = {v: k for k, v in lowmap.items()}
    for p in preferred:
        if p in inv:  # match exacto (en minúsculas)
            return inv[p]
    # parcial
    for c in cols:
        name = str(c).strip().lower()
        if any(p in name for p in preferred):
            return c
    return None

def read_sap_joint_reactions(file) -> pd.DataFrame:
    """
    Parser robusto para 'TABLE: Joint Reactions' de SAP2000 (XLSX/CSV).
    Devuelve columnas: Joint, OutputCase, F1, F2, F3, M1, M2, M3 (si existen).
    """
    df_raw = _load_raw(file)
    if df_raw.empty:
        return pd.DataFrame(columns=['Joint','OutputCase','F1','F2','F3','M1','M2','M3'])

    # 1) Ubica fila de encabezados
    h = _find_header_row(df_raw)
    if h is None:
        # Como fallback, intenta header=0 por si el archivo ya viene “limpio”
        try:
            if hasattr(file, 'read'):
                file.seek(0)  # reset pointer por si es subida streamlit
            df = _load_raw(file)
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        except Exception:
            raise ValueError("No se pudo detectar fila de encabezados en el archivo SAP.")
    else:
        # 2) Asigna nombres y salta fila de unidades si aplica
        columns = df_raw.iloc[h].tolist()
        df = df_raw.iloc[h+1:].copy()
        if len(df) and _maybe_units_row(df.iloc[0]):
            df = df.iloc[1:].copy()
        df.columns = columns
        df = df.reset_index(drop=True)

    # 3) Normaliza nombres (case-insensitive, espacios)
    df.columns = [str(c).strip() for c in df.columns]

    # 4) Mapea columnas clave con equivalentes
    joint_col = _choose_col(df.columns, ('joint','point','node','label','joint id','point id','name','object'))
    case_col  = _choose_col(df.columns, ('outputcase','case','output case','loadcase','load case'))
    f1_col    = _choose_col(df.columns, ('f1',))
    f2_col    = _choose_col(df.columns, ('f2',))
    f3_col    = _choose_col(df.columns, ('f3',))
    m1_col    = _choose_col(df.columns, ('m1',))
    m2_col    = _choose_col(df.columns, ('m2',))
    m3_col    = _choose_col(df.columns, ('m3',))

    # 5) Construye el DF final con los que existan
    out_cols = {}
    if joint_col: out_cols['Joint'] = joint_col
    if case_col:  out_cols['OutputCase'] = case_col
    for k, src in (('F1',f1_col),('F2',f2_col),('F3',f3_col),('M1',m1_col),('M2',m2_col),('M3',m3_col)):
        if src: out_cols[k] = src

    if not out_cols:
        raise ValueError("No se encontraron columnas reconocibles (Joint/Case/F1..M3). Revisa el export de SAP.")

    df = df[list(out_cols.values())].copy()
    df.columns = list(out_cols.keys())

    # 6) Tipos: Joint como entero “Int64”, fuerzas/momentos a float
    if 'Joint' in df.columns:
        df['Joint'] = pd.to_numeric(df['Joint'], errors='coerce').astype('Int64')
    for c in ['F1','F2','F3','M1','M2','M3']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    # 7) Filtra filas totalmente vacías en fuerzas/momentos
    numeric_cols = [c for c in ['F1','F2','F3','M1','M2','M3'] if c in df.columns]
    if numeric_cols:
        mask = df[numeric_cols].notna().any(axis=1)
        df = df.loc[mask].reset_index(drop=True)

    # 8) Si Case faltó, rellena con placeholder
    if 'OutputCase' not in df.columns:
        df['OutputCase'] = 'Unknown'

    return df
