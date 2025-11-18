# Base Anchors App – Placa base & anclajes (ACI 318-19 / EN 1992-4)

- Importa **Joint Reactions** de SAP2000 (XLSX/XLSM/CSV).
- **Geometría & Materiales**, **CASE ACI 1/2/3** (controlante automático), **fricción** por defecto.
- Chequeos **ACI 318-19 Cap. 17**: acero (Nsa, Vsa), concreto (Ncbg, Np, Nsbg, Vcbg, Vcpg), y **shear key** (17.11).
- **Interacción N–V**: lineal, ^1.5, ^5/3; **Seismic OFF** por defecto (si ON aplica **Ω₀ = 2.5** a demanda).
- **Placa (AISC DG1)**: espesor mínimo por momentos y cortante; **t_min = 10 mm** y **redondeo a 5 mm**.
- **PDF** con plantilla Jinja y resumen de ratios.

## Ejecutar
```bash
pip install -r requirements.txt
streamlit run app/main.py
