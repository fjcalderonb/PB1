import io
import pandas as pd
from .utils import classify_case

# --- helpers internos ---
def _strip_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df

def _drop_unnamed(df: pd.DataFrame) -> pd.DataFrame:
    keep = []
    for c in df.columns:
        if str(c).lower().startswith('unnamed'):
            # si toda la col es NaN o vacío, la descartamos
            if df[c].isna().all() or (df[c].astype(str).str.strip() == '').all():
                continue
        keep.append(c)
    return df[keep]

def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    norm = {str(c).lower().replace(' ','').replace('_',''): c for c in df.columns}
    for cand in candidates:
        key = cand.lower().replace(' ','').replace('_','')
        if key in norm:
            return norm[key]
    return None

def _header_units_data_split(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta patrón SAP2000 Joint Reactions:
      fila i   -> títulos (contiene 'Joint' y 'OutputCase' / 'Case' / 'LoadCase')
      fila i+1 -> unidades
      fila i+2.. -> datos
    """
    max_scan = min(10, len(df_raw))
    header_row = None
    for i in range(max_scan):
        row_vals = df_raw.iloc[i].astype(str).str.strip().tolist()
        has_joint = any(v.upper() == 'JOINT' for v in row_vals)
        has_case  = any(v.upper() in ('OUTPUTCASE','CASE','LOADCASE','LOAD CASE','COMBINATION','COMBO') for v in row_vals)
        if has_joint and has_case:
            header_row = i
            break
    if header_row is None:
        # no se detectó patrón: devolvemos tal cual (ya se manejará más abajo)
        return None

    # títulos y unidades
    titles = df_raw.iloc[header_row].astype(str).str.strip().tolist()
    # datos: todo lo que venga después de la fila de unidades
    data_df = df_raw.iloc[header_row+2:].reset_index(drop=True).copy()

    # Asignar encabezados
    data_df.columns = titles
    data_df = _strip_cols(data_df)
    data_df = _drop_unnamed(data_df)
    return data_df

def read_sap_table(file_obj):
    """
    Lector robusto de SAP2000 'Joint Reactions':
    - Soporta XLS/XLSX/CSV con 3 filas: títulos, unidades, datos.
    - Limpia columnas 'Unnamed', convierte F1,F2,F3,M1,M2,M3 a numérico.
    - Crea 'OutputCase' si no existe y clasifica ULS/SLS en 'ULS_SLS'.
    """
    # Cargar bytes en memoria (Streamlit file_uploader)
    name = getattr(file_obj, 'name', 'uploaded').lower()
    buf  = io.BytesIO(file_obj.read()) if hasattr(file_obj, 'read') else io.BytesIO(file_obj)

    # 1) Intento: leer siempre sin header para poder detectar patrón títulos/unidades
    try:
        if name.endswith(('.xls','.xlsx')):
            df_raw = pd.read_excel(buf, header=None, sheet_name=0)
        else:
            buf.seek(0)
            df_raw = pd.read_csv(buf, header=None)
    except Exception:
        # fallback: intentar con header por defecto
        buf.seek(0)
        if name.endswith(('.xls','.xlsx')):
            df_raw = pd.read_excel(buf, sheet_name=0)
        else:
            df_raw = pd.read_csv(buf)

    # 2) Detectar patrón SAP (títulos/unidades/datos)
    df = _header_units_data_split(df_raw)
    if df is None:
        # No se encontró patrón (p.ej. CSV ya “plano” con header en la 1ª fila)
        # Reintentar leyendo con header en la primera fila
        buf.seek(0)
        try:
            if name.endswith(('.xls','.xlsx')):
                df = pd.read_excel(buf, sheet_name=0)
            else:
                df = pd.read_csv(buf)
        except Exception:
            # Como último recurso, toma primera fila como cabecera y descarta la de unidades si la encuentra
            df = df_raw.copy()
            df.columns = df.iloc[0]
            df = df.iloc[2:].reset_index(drop=True)

    df = _strip_cols(df)
    df = _drop_unnamed(df)

    # 3) Normalizar columna OutputCase (o equivalente)
    out_col = _find_col(df, ['OutputCase','Output Case','Case','LoadCase','Load Case','Combination','Combo'])
    if out_col is None:
        df['OutputCase'] = ''
        out_col = 'OutputCase'

    # 4) Clasificación ULS/SLS
    df['ULS_SLS'] = df[out_col].astype(str).map(classify_case)

    # 5) Renombrar/convertir numéricos conocidos
    rename = {}
    for k in ('F1','F2','F3','M1','M2','M3'):
        if k not in df.columns:
            maybe = _find_col(df, [k])
            if maybe:
                rename[maybe] = k
    if rename:
        df = df.rename(columns=rename)

    for col in ('F1','F2','F3','M1','M2','M3'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6) Limpieza de filas vacías (por si sobran separadores)
    if out_col in df.columns:
        mask_all_nan = df.drop(columns=[out_col]).isna().all(axis=1)
        df = df.loc[~(mask_all_nan & (df[out_col].astype(str).str.strip()==''))].reset_index(drop=True)

    return df


# #V3 FUNCIONA
# # engine/io_sap.py
# import io
# import re
# import pandas as pd
# from .utils import classify_case

# ALIASES = ['Load Case/Combo Name', 'Case/Combo Name', 'Load Case', 'Load Case Name', 'Case']

# def read_sap_table(file_obj):
#     name = (getattr(file_obj, 'name', '') or '').lower()

#     # BytesIO seguro (no “consume” el uploader)
#     if isinstance(file_obj, (bytes, bytearray)):
#         data = io.BytesIO(file_obj)
#     elif hasattr(file_obj, "read"):
#         b = file_obj.read()
#         try:
#             file_obj.seek(0)
#         except Exception:
#             pass
#         data = io.BytesIO(b)
#     else:
#         data = file_obj

#     # 1) Lectura
#     try:
#         if name.endswith(('.xls', '.xlsx')):
#             df = pd.read_excel(data)
#         else:
#             if hasattr(data, 'seek'):
#                 data.seek(0)
#             df = pd.read_csv(data, engine='python', sep=None, encoding_errors='ignore')
#     except Exception:
#         # Reintento sin header (cuando hay metadatos arriba)
#         if hasattr(data, 'seek'):
#             data.seek(0)
#         df = pd.read_excel(data, header=None)

#     # 2) Asegurar DataFrame
#     if isinstance(df, pd.Series):
#         df = df.to_frame().T
#     elif not isinstance(df, pd.DataFrame):
#         if hasattr(data, 'seek'):
#             data.seek(0)
#         df = pd.read_excel(data, header=None)

#     # 3) Reparar encabezado si falta 'OutputCase' o alias
#     if not any(c in df.columns for c in ['OutputCase', *ALIASES]):
#         max_scan = min(50, len(df))
#         for i in range(max_scan):
#             row = df.iloc[i]
#             if not isinstance(row, pd.Series):
#                 continue
#             row = row.astype(str).str.strip()
#             vals = set(row.values)
#             if ('Joint' in vals) and (('OutputCase' in vals) or any(a in vals for a in ALIASES)):
#                 df = df.iloc[i+1:].copy()
#                 df.columns = row
#                 df = df.reset_index(drop=True)
#                 break

#     # 4) Alias → 'OutputCase'
#     for alias in ALIASES:
#         if alias in df.columns and 'OutputCase' not in df.columns:
#             df = df.rename(columns={alias: 'OutputCase'})
#             break

#     # 5) Clasificación ULS/SLS (default Serie del largo del df)
#     col = df.get('OutputCase', pd.Series([''] * len(df), index=df.index, name='OutputCase'))
#     df['ULS_SLS'] = col.astype(str).map(classify_case)

#     # --- SANITIZE → Arrow-friendly (evita ArrowTypeError en st.dataframe) ---
#     NUMERIC_COLS = [c for c in ['F1','F2','F3','M1','M2','M3'] if c in df.columns]
#     for c in NUMERIC_COLS:
#         df[c] = pd.to_numeric(df[c], errors='coerce')

#     # Quitar filas de unidades/encabezado repetido: todas las fuerzas/momentos NaN
#     if NUMERIC_COLS:
#         df = df[~df[NUMERIC_COLS].isna().all(axis=1)].reset_index(drop=True)

#     # Columnas no numéricas → string plano (evita mezcla object)
#     for c in df.columns:
#         if c not in NUMERIC_COLS:
#             # Evitar convertir floats válidos de otras columnas numéricas que no detectamos
#             # (por seguridad, solo las 'no NUMERIC_COLS' se fuerzan a str)
#             df[c] = df[c].astype(str)

#     return df

# # V2 FUNCIONA
# # engine/io_sap.py
# import io
# import re
# import pandas as pd
# from .utils import classify_case

# ALIASES = ['Load Case/Combo Name', 'Case/Combo Name', 'Load Case', 'Load Case Name', 'Case']

# def read_sap_table(file_obj):
#     name = (getattr(file_obj, 'name', '') or '').lower()

#     # --- Convertimos a BytesIO sin “consumir” el uploader ---
#     if isinstance(file_obj, (bytes, bytearray)):
#         data = io.BytesIO(file_obj)
#     elif hasattr(file_obj, "read"):
#         b = file_obj.read()
#         try:
#             file_obj.seek(0)
#         except Exception:
#             pass
#         data = io.BytesIO(b)
#     else:
#         # ya es BytesIO o path-like
#         data = file_obj

#     # --- Lectura (primer intento) ---
#     try:
#         if name.endswith(('.xls', '.xlsx')):
#             df = pd.read_excel(data)
#         else:
#             if hasattr(data, 'seek'):
#                 data.seek(0)
#             df = pd.read_csv(data, engine='python', sep=None, encoding_errors='ignore')
#     except Exception:
#         # Reintento crudo sin header
#         if hasattr(data, 'seek'):
#             data.seek(0)
#         df = pd.read_excel(data, header=None)

#     # --- Asegurar que sea DataFrame ---
#     if isinstance(df, pd.Series):
#         df = df.to_frame().T
#     elif not isinstance(df, pd.DataFrame):
#         if hasattr(data, 'seek'):
#             data.seek(0)
#         df = pd.read_excel(data, header=None)

#     # --- Reparar encabezado si es necesario ---
#     if not any(c in df.columns for c in ['OutputCase', *ALIASES]):
#         # Intentamos encontrar la fila de encabezado en las primeras 50
#         max_scan = min(50, len(df))
#         for i in range(max_scan):
#             row = df.iloc[i]
#             if not isinstance(row, pd.Series):   # ← evita el AttributeError
#                 continue
#             row = row.astype(str).str.strip()
#             vals = set(row.values)
#             if ('Joint' in vals) and (('OutputCase' in vals) or any(a in vals for a in ALIASES)):
#                 df = df.iloc[i+1:].copy()
#                 df.columns = row
#                 df = df.reset_index(drop=True)
#                 break
#         # si no encontró, seguimos con lo que hay (no rompemos)

#     # --- Normalizar alias → 'OutputCase' ---
#     for alias in ALIASES:
#         if alias in df.columns and 'OutputCase' not in df.columns:
#             df = df.rename(columns={alias: 'OutputCase'})
#             break

#     # --- Clasificar ULS/SLS (default = Serie vacía del mismo largo) ---
#     col = df.get('OutputCase', pd.Series([''] * len(df), index=df.index, name='OutputCase'))
#     df['ULS_SLS'] = col.astype(str).map(classify_case)

#     return df




# V1 FALLA
# import io
# import pandas as pd
# from .utils import classify_case

# def read_sap_table(file_obj):
#     name = getattr(file_obj, 'name', '')
#     data = io.BytesIO(file_obj.read()) if hasattr(file_obj, 'read') else file_obj
#     try:
#         if str(name).lower().endswith(('.xls','.xlsx')): df = pd.read_excel(data)
#         else: df = pd.read_csv(data)
#     except Exception:
#         data.seek(0); df = pd.read_excel(data, header=None); df.columns = df.iloc[0]; df=df[1:]
#     df['ULS_SLS'] = df.get('OutputCase','').astype(str).map(classify_case)
#     return df