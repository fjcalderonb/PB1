
import pandas as pd
from pathlib import Path
import re

_UNITS_RE = re.compile(r'(?i)\b(?:text|kn|kn[-·*]?m)\b')

def _load_raw(_file) -> pd.DataFrame:
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
    needed_any = {'outputcase', 'case'}
    needed_forces = {'f1','f2','f3','m1','m2','m3'}
    max_scan = min(30, len(df_raw))
    for i in range(max_scan):
        row_vals = df_raw.iloc[i].astype(str).str.strip()
        lower = set(v.lower() for v in row_vals if v and v != 'nan')
        if (lower & needed_any) and (needed_forces.issubset(lower)):
            return i
    for i in range(max_scan):
        row_vals = df_raw.iloc[i].astype(str).str.strip()
        lower = set(v.lower() for v in row_vals if v and v != 'nan')
        if {'f1','f2','f3','m1','m2','m3'}.issubset(lower):
            return i
    return None

def _maybe_units_row(s: pd.Series) -> bool:
    txt = s.astype(str)
    return bool(txt.str.contains(_UNITS_RE, regex=True, na=False).any())

def _choose_col(cols, preferred: tuple[str, ...]) -> str | None:
    lowmap = {str(c): str(c).strip().lower() for c in cols}
    inv = {v: k for k, v in lowmap.items()}
    for p in preferred:
        if p in inv: return inv[p]
    for c in cols:
        name = str(c).strip().lower()
        if any(p in name for p in preferred): return c
    return None

def read_joint_reactions(file) -> pd.DataFrame:
    df_raw = _load_raw(file)
    if df_raw.empty:
        return pd.DataFrame(columns=['Joint','OutputCase','F1','F2','F3','M1','M2','M3'])
    h = _find_header_row(df_raw)
    if h is None:
        if hasattr(file, 'read'):
            try: file.seek(0)
            except Exception: pass
        df = _load_raw(file)
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
    else:
        columns = df_raw.iloc[h].tolist()
        df = df_raw.iloc[h+1:].copy()
        if len(df) and _maybe_units_row(df.iloc[0]):
            df = df.iloc[1:].copy()
        df.columns = columns
        df = df.reset_index(drop=True)
    df.columns = [str(c).strip() for c in df.columns]
    joint_col = _choose_col(df.columns, ('joint','point','node','label','joint id','point id','name','object'))
    case_col  = _choose_col(df.columns, ('outputcase','case','output case','loadcase','load case'))
    f1_col    = _choose_col(df.columns, ('f1',))
    f2_col    = _choose_col(df.columns, ('f2',))
    f3_col    = _choose_col(df.columns, ('f3',))
    m1_col    = _choose_col(df.columns, ('m1',))
    m2_col    = _choose_col(df.columns, ('m2',))
    m3_col    = _choose_col(df.columns, ('m3',))
    out_cols = {}
    if joint_col: out_cols['Joint'] = joint_col
    if case_col:  out_cols['OutputCase'] = case_col
    for k, src in (('F1',f1_col),('F2',f2_col),('F3',f3_col),('M1',m1_col),('M2',m2_col),('M3',m3_col)):
        if src: out_cols[k] = src
    if not out_cols:
        raise ValueError("Unrecognized columns in SAP export (Joint/Case/F1..M3 not found).")
    df = df[list(out_cols.values())].copy(); df.columns = list(out_cols.keys())
    if 'Joint' in df.columns: df['Joint'] = pd.to_numeric(df['Joint'], errors='coerce').astype('Int64')
    for c in ['F1','F2','F3','M1','M2','M3']:
        if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
    numeric_cols = [c for c in ['F1','F2','F3','M1','M2','M3'] if c in df.columns]
    if numeric_cols:
        mask = df[numeric_cols].notna().any(axis=1)
        df = df.loc[mask].reset_index(drop=True)
    if 'OutputCase' not in df.columns:
        df['OutputCase'] = 'Unknown'
    return df
