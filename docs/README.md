
# Baseplate App (I1)

## Ejecutar
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
streamlit run app/app.py
```

## Notas
- Carga SAP2000: página 03, soporta XLS/XLSX/CSV de "Joint Reactions".
- Ejes: Option 1/2 + flips; conversión automática de M de kN·mm a kN·m si aplica.
- Placa base: contacto elástico + Método Local (DG1).
- Soldadura: filete E70XX (AISC 360-16 J2/J4). 
- Anclajes: acero (φN_s, φV_s) – concreto en I2/I3.
