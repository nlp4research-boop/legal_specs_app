import json
from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Category, Node, ContentVersion
from .auth import get_current_user
from .seed_data import seed_initial_data

app = FastAPI(title="Legal Specs App")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    seed_initial_data()


def get_latest_version(db: Session, node_id: int):
    return (
        db.query(ContentVersion)
        .filter(ContentVersion.node_id == node_id)
        .order_by(ContentVersion.version.desc())
        .first()
    )


def get_version(db: Session, node_id: int, version: int):
    return (
        db.query(ContentVersion)
        .filter(ContentVersion.node_id == node_id, ContentVersion.version == version)
        .first()
    )


def _default_spec(node: Node):
    return {
        "spec_id": node.spec_id or node.spec_code,
        "contract_type": node.category.slug if node.category else "",
        "clause_type": node.spec_code.split(".")[-1] if node.spec_code else "",
        "jurisdiction": "General/KSA",
        "purpose": "",
        "scope": {
            "applies_when": [],
            "does_not_apply_when": [],
        },
        "allowed": {"model_may": []},
        "disallowed": {"model_must_not": []},
        "required_reasoning": {
            "before_answer_think_about": [],
            "potential_risk_signals": [],
        },
        "edge_cases": {"model_must_know": []},
        "safe_completion_rules": {
            "model_should": [],
            "response_template": "",
        },
    }


def _normalize_spec_dict(node: Node, data: dict) -> dict:
    base = _default_spec(node)

    def merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict):
                merge(a[k], v)
            else:
                a[k] = v

    merge(base, data or {})
    return base


def _build_form_data(node: Node, version_obj: ContentVersion | None):
    if version_obj:
        try:
            data = json.loads(version_obj.content_json)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    spec = _normalize_spec_dict(node, data)
    print("=============>", spec)

    def join_lines(lst):
        if not isinstance(lst, list):
            return ""
        return "\n".join(str(x) for x in lst)

    form_data = {
        "spec_id": spec.get("spec_id", ""),
        "contract_type": spec.get("contract_type", ""),
        "clause_type": spec.get("clause_type", ""),
        "jurisdiction": spec.get("jurisdiction", ""),
        "purpose": spec.get("purpose", ""),
        "scope_applies_when": join_lines(spec.get("scope", {}).get("applies_when", [])),
        "scope_does_not_apply_when": join_lines(
            spec.get("scope", {}).get("does_not_apply_when", [])
        ),
        "allowed_model_may": join_lines(spec.get("allowed", {}).get("model_may", [])),
        "disallowed_model_must_not": join_lines(
            spec.get("disallowed", {}).get("model_must_not", [])
        ),
        "reasoning_before": join_lines(
            spec.get("required_reasoning", {}).get("before_answer_think_about", [])
        ),
        "reasoning_risks": join_lines(
            spec.get("required_reasoning", {}).get("potential_risk_signals", [])
        ),
        "edge_cases_must_know": join_lines(
            spec.get("edge_cases", {}).get("model_must_know", [])
        ),
        "safe_completion_rules_should": join_lines(
            spec.get("safe_completion_rules", {}).get("model_should", [])
        ),
        "safe_completion_rules_template": join_lines(
            spec.get("safe_completion_rules", {}).get("response_template", "")
        ),
    }
    print("====>", spec.get("safe_completion_rules", {}).get("response_template", ""))
    return form_data, spec


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "categories": categories},
    )


@app.get("/category/{slug}", response_class=HTMLResponse)
def category_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    nodes = category.nodes
    return templates.TemplateResponse(
        "category.html",
        {"request": request, "category": category, "nodes": nodes},
    )


@app.get("/node/{node_id}", response_class=HTMLResponse)
def node_detail(node_id: int, request: Request, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    latest = get_latest_version(db, node.id)
    form_data, spec = _build_form_data(node, latest)
    return templates.TemplateResponse(
        "node_detail.html",
        {
            "request": request,
            "node": node,
            "latest": latest,
            "form": form_data,
            "spec": spec,
        },
    )


@app.get("/node/{node_id}/version/{version}", response_class=HTMLResponse)
def node_version_view(
    node_id: int,
    version: int,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    ver_obj = get_version(db, node_id, version)
    if not ver_obj:
        raise HTTPException(status_code=404, detail="Version not found")

    form_data, spec = _build_form_data(node, ver_obj)

    return templates.TemplateResponse(
        "node_version.html",
        {
            "request": request,
            "node": node,
            "ver": ver_obj,
            "form": form_data,
            "spec": spec,
        },
    )


@app.get("/node/{node_id}/edit", response_class=HTMLResponse)
def edit_node(
    node_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    latest = get_latest_version(db, node.id)
    form_data, spec = _build_form_data(node, latest)
    return templates.TemplateResponse(
        "node_edit.html",
        {
            "request": request,
            "node": node,
            "form": form_data,
            "user": user,
        },
    )


@app.post("/node/{node_id}/edit")
def save_node(
    node_id: int,
    spec_id: str = Form(...),
    contract_type: str = Form(""),
    clause_type: str = Form(""),
    jurisdiction: str = Form(""),
    purpose: str = Form(""),
    scope_applies_when: str = Form(""),
    scope_does_not_apply_when: str = Form(""),
    allowed_model_may: str = Form(""),
    disallowed_model_must_not: str = Form(""),
    reasoning_before: str = Form(""),
    reasoning_risks: str = Form(""),
    edge_cases_must_know: str = Form(""),
    safe_completion_rules_should: str = Form(""),
    safe_completion_template: str = Form(""),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    def split_lines(text: str):
        return [line.strip() for line in text.splitlines() if line.strip()]

    scr = {}

    spec = {
        "spec_id": spec_id,
        "contract_type": contract_type,
        "clause_type": clause_type,
        "jurisdiction": jurisdiction,
        "purpose": purpose,
        "scope": {
            "applies_when": split_lines(scope_applies_when),
            "does_not_apply_when": split_lines(scope_does_not_apply_when),
        },
        "allowed": {"model_may": split_lines(allowed_model_may)},
        "disallowed": {"model_must_not": split_lines(disallowed_model_must_not)},
        "required_reasoning": {
            "before_answer_think_about": split_lines(reasoning_before),
            "potential_risk_signals": split_lines(reasoning_risks),
        },
        "edge_cases": {"model_must_know": split_lines(edge_cases_must_know)},
        "safe_completion_rules": {
            "model_should": split_lines(safe_completion_rules_should),
            "response_template": split_lines(safe_completion_template),
        },
    }

    node.spec_id = spec_id
    if contract_type:
        cat = db.query(Category).filter(Category.slug == contract_type.upper()).first()
        if cat and node.category_id != cat.id:
            node.category_id = cat.id
    if clause_type and node.spec_code:
        parts = node.spec_code.split(".")
        parts[-1] = clause_type
        node.spec_code = ".".join(parts)

    latest = get_latest_version(db, node.id)
    new_version_number = 1 if not latest else latest.version + 1

    new_version = ContentVersion(
        node_id=node.id,
        version=new_version_number,
        created_by=user,
        content_json=json.dumps(spec, ensure_ascii=False, indent=2),
    )
    db.add(new_version)
    db.commit()

    return RedirectResponse(url=f"/node/{node.id}", status_code=303)


@app.get("/node/{node_id}/history", response_class=HTMLResponse)
def node_history(
    node_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user),
):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    versions = (
        db.query(ContentVersion)
        .filter(ContentVersion.node_id == node_id)
        .order_by(ContentVersion.version.desc())
        .all()
    )
    return templates.TemplateResponse(
        "node_history.html",
        {
            "request": request,
            "node": node,
            "versions": versions,
        },
    )
