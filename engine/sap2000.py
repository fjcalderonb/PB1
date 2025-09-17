
import io
import pandas as pd
import numpy as np

LABEL_CANDIDATES = {'Joint','OutputCase','CaseType','StepType','F1','F2','F3','M1','M2','M3'}
UNITS_TOKENS = {'KN','K N','KN-M','K N-M','KIPS','KIP','N','N-M','K N·M'}

def _read_raw(file_obj):
    name = getattr(file_obj, 'name', '')
    if isinstance(file_obj, (bytes, bytearray)):
        data = io.BytesIO(file_obj)
    else:
        data = file_obj
    if name.lower().endswith(('.xls','.xlsx')):
        raw = pd.read_excel(data, header=None, dtype=str)
    else:
        raw = pd.read_csv(data, header=None, dtype=str)
    return raw

def _find_header_row(df: pd.DataFrame):
    for idx in range(min(50, len(df))):
        row_vals = [str(x).strip() for x in df.iloc[idx].tolist()]
        labels = set(row_vals)
        hits = len(labels.intersection(LABEL_CANDIDATES))
        if ('Joint' in row_vals) and (('F1' in row_vals) or ('F2' in row_vals)) and hits>=3:
            return idx
    return None

def _is_units_row(vals):
    vals_up = [str(v).upper().replace(' ','') for v in vals]
    return any(any(tok.replace(' ','') in v for tok in UNITS_TOKENS) for v in vals_up)

def read_sap_table(file_obj):
    raw = _read_raw(file_obj)
    if raw is None or raw.empty:
        return pd.DataFrame()
    hdr_idx = _find_header_row(raw)
    if hdr_idx is None:
        try:
            file_obj.seek(0)
        except Exception:
            pass
        try:
            df2 = pd.read_excel(file_obj)
        except Exception:
            try:
                df2 = pd.read_csv(file_obj)
            except Exception:
                return pd.DataFrame()
        return df2
    headers = [str(x).strip() for x in raw.iloc[hdr_idx].tolist()]
    start = hdr_idx + 1
    if start < len(raw):
        next_vals = [str(x).strip() for x in raw.iloc[start].tolist()]
        if _is_units_row(next_vals):
            start += 1
    data = raw.iloc[start:].copy()
    data.columns = headers[:len(data.columns)]
    data = data.dropna(how='all')
    rename_map = {}
    for c in list(data.columns):
        cl = str(c).strip()
        if cl.lower() in ['loadcase','load case','case','output case','outputcase']:
            rename_map[c] = 'OutputCase'
        elif cl.lower() == 'joint':
            rename_map[c] = 'Joint'
    data = data.rename(columns=rename_map)
    for c in list(data.columns):
        cu = str(c).upper()
        if cu.startswith('F') or cu.startswith('M'):
            data[c] = pd.to_numeric(data[c], errors='coerce')
    if 'Joint' not in data.columns: data['Joint'] = np.nan
    if 'OutputCase' not in data.columns: data['OutputCase'] = ''
    return data.reset_index(drop=True)
