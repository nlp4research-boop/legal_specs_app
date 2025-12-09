Legal Specs App (FastAPI + SQLite) – V3

important directories:
  app/data   :  Markdown 
  app/specs  : JSON of specs.

run:
  1) cd legal_specs_app_v3
  2) python -m venv .venv 
  3) pip install -r requirements.txt
  4) uvicorn app.main:app --reload
  5) افتح http://127.0.0.1:8000/
