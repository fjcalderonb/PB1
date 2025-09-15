import pandas as pd

def compute_equiv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Si Condition == 1 usar mapping A, si no usar B (ver tu macro)
    cond = df.get("Condition", pd.Series([1]*len(df)))
    # Ejemplo: replico lógica de columnas M,N,O,P,Q -> T97:X97 (simplificado)
    # 2ª iteración: calc exacto como en tu libro (Mequiv, Vequiv según d1,d2,n1,n2)
    df["Mequiv"] = df["Mx"]
    df["Vequiv"] = (df["Vx"]**2 + df["Vy"]**2) ** 0.5
    return df

def pick_worst(df: pd.DataFrame, discipline: str) -> pd.Series:
    # Criterios básicos; 2ª iteración: usar ratios reales de cada verificación
    if discipline.lower() == "concreto":
        # mayor q_max estimado → mayor N y M
        s = (abs(df["N"]) + abs(df["Mequiv"])).idxmax()
    elif discipline.lower() == "pernos":
        s = (abs(df["Mequiv"])).idxmax()
    elif discipline.lower() == "placa":
        s = (abs(df["Mequiv"])).idxmax()
    else:
        s = df.index[0]
    return df.loc[s]
