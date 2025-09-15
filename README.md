
# Base Plate — AISC/ACI (Streamlit)

**Iteration 2 (partial, EN UI)**
- LRFD by default.
- Anchor grade selector (F1554-36/55/105) and diameters (in→mm).
- Bearing/pressure Cases 1–4 (AISC DG1) with simplified bearing cap; A2/A1 in next iteration.
- Anchors (steel) operational; concrete (ACI 318-19 Ch.17) next iteration.
- **Combinations (SAP2000)**: importer for `TABLE: Joint Reactions` → evaluates **ALL** joints & combinations and picks the **worst case per discipline** (Concrete, Anchors, Plate). Reports show Joint/OutputCase.
- **Shear**: by default use **friction** (configurable μ); if you tick “Anchors resist shear”, full V goes to anchors.
- PDF reports per discipline.

## Run locally
```bat
py -3.11 -m venv .venv
.\.venv\Scriptsctivate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8590
```

## Upload to GitHub (web UI)
1. Create an empty repository: https://github.com/new
2. Download this project as `.zip` and **extract** it locally.
3. In your repo → **Code → Add file → Upload files**. Drag & drop **all contents** of the folder (do not upload the container folder).
4. Click **Commit changes**.
5. (Optional) Connect Streamlit Cloud and point to `app.py`.

## Upload to GitHub (git CLI)
```bat
cd <project_path>
git init
notepad .gitignore
git add .
git commit -m "feat: EN UI + SAP importer + worst-case per discipline + friction"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```
### Recommended `.gitignore`
```
__pycache__/
*.pyc
.venv/
.vscode/
.streamlit/secrets.toml
*.xlsm
*.xlsx
*.pdf
*.docx
*.pptx
.DS_Store
Thumbs.db
~$*
```
