
import pandas as pd
from pathlib import Path

def read_sap_joint_reactions(file) -> pd.DataFrame:
    """Read SAP2000 export (TABLE: Joint Reactions). Ignore StepType/CaseType.
    Returns columns: Joint, OutputCase, F1, F2, F3, M1, M2, M3 (floats for forces/moments).
    """
    def _load(_file):
        if hasattr(_file, 'read') and not isinstance(_file, (str, bytes, Path)):
            name = getattr(_file, 'name', 'uploaded')
            if str(name).lower().endswith('.csv'):
                return pd.read_csv(_file)
            return pd.read_excel(_file, sheet_name=0, header=1, engine='openpyxl')
        path = Path(_file)
        if path.suffix.lower() == '.csv':
            return pd.read_csv(path)
        return pd.read_excel(path, sheet_name=0, header=1, engine='openpyxl')

    df = _load(file)
    # Drop the units/types row
    mask_units = (
        df['Joint'].astype(str).str.contains('Text', na=False) |
        df['F1'].astype(str).str.contains('KN', na=False)
    )
    df = df.loc[~mask_units].copy()

    # Keep only needed columns
    keep = ['Joint','OutputCase','F1','F2','F3','M1','M2','M3']
    df = df[[c for c in keep if c in df.columns]].copy()

    # Types
    df['Joint'] = pd.to_numeric(df['Joint'], errors='coerce').astype('Int64')
    for c in ['F1','F2','F3','M1','M2','M3']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.dropna(subset=['Joint','OutputCase']).reset_index(drop=True)
    return df
