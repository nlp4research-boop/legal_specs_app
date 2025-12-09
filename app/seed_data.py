from pathlib import Path
import re
import json
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Category, Node, ContentVersion

CATEGORY_DEFS = [
    ("DEEDS", "عقود الصكوك", "Deeds Contracts", "DEEDS.md"),
    ("FIN", "عقود التمويل والتمويل الإسلامي", "Finance / Islamic Finance Contracts", "FIN.md"),
    ("INV", "عقود الاستثمار", "Investment Contracts", "INV.md"),
    ("LEASE", "عقود العقارات والإيجار", "Real Estate & Lease Contracts", "LEASE.md"),
    ("EMP", "عقود التوظيف والعمل", "Employment Contracts", "EMP.md"),
    ("GOVP", "عقود المشتريات الحكومية", "Government Procurement Contracts", "GOVP.md"),
    ("COMM", "العقود التجارية والعامة", "Commercial & General Business Contracts", "COMM.md"),
]


def parse_specs_from_markdown(text: str):
    in_block = False
    codes = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if not in_block:
            continue
        m = re.search(r"(spec\.[A-Za-z0-9_\.]+)", line)
        if m:
            codes.append(m.group(1).strip())

    seen = set()
    unique = []
    for c in codes:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def import_json_specs(db: Session, base_dir: Path):
    specs_dir = base_dir / "specs"
    if not specs_dir.exists():
        return

    for path in specs_dir.glob("*.json"):
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        spec_id = spec.get("spec_id")
        contract_type = spec.get("contract_type")
        clause_type = spec.get("clause_type")

        if not spec_id or not contract_type:
            continue

        slug = str(contract_type).upper()

        cat = db.query(Category).filter_by(slug=slug).first()
        if not cat:
            cat = Category(slug=slug, name_ar=slug, name_en=slug)
            db.add(cat)
            db.flush()

        spec_code = spec_id
        version_num = 1

        if ".v" in spec_id:
            base_id, ver = spec_id.rsplit(".v", 1)
            spec_code = base_id
            if ver.isdigit():
                version_num = int(ver)
        else:
            parts = spec_id.split(".")
            last = parts[-1]
            if last.startswith("v") and last[1:].isdigit():
                version_num = int(last[1:])
                spec_code = ".".join(parts[:-1])

        node = db.query(Node).filter_by(spec_id=spec_id).first()
        if not node:
            node = db.query(Node).filter_by(spec_code=spec_code).first()

        if not node:
            title = clause_type.replace("_", " ") if clause_type else spec_code
            node = Node(
                category_id=cat.id,
                spec_code=spec_code,
                spec_id=spec_id,
                title=title,
                path=spec_code,
            )
            db.add(node)
            db.flush()
        else:
            if not node.category_id:
                node.category_id = cat.id
            if not node.spec_id:
                node.spec_id = spec_id

        existing_version = (
            db.query(ContentVersion)
            .filter_by(node_id=node.id, version=version_num)
            .first()
        )
        if existing_version:
            continue

        cv = ContentVersion(
            node_id=node.id,
            version=version_num,
            created_by="json_import",
            content_json=json.dumps(spec, ensure_ascii=False, indent=2),
        )
        db.add(cv)

    db.commit()


def seed_initial_data():
    db: Session = SessionLocal()
    try:
        base_dir = Path(__file__).resolve().parent
        data_dir = base_dir / "data"

        if db.query(Category).count() == 0 and db.query(Node).count() == 0:
            for slug, name_ar, name_en, filename in CATEGORY_DEFS:
                cat = Category(slug=slug, name_ar=name_ar, name_en=name_en)
                db.add(cat)
                db.flush()

                md_path = data_dir / filename
                if md_path.exists():
                    specs = parse_specs_from_markdown(md_path.read_text(encoding="utf-8"))
                    for spec_code in specs:
                        existing = db.query(Node).filter_by(spec_code=spec_code).first()
                        if existing:
                            continue
                        parts = spec_code.split(".")
                        title_part = parts[-1] if parts else spec_code
                        title = title_part.replace("_", " ")
                        node = Node(
                            category_id=cat.id,
                            spec_code=spec_code,
                            spec_id=None,
                            title=title,
                            path=spec_code,
                        )
                        db.add(node)

            db.commit()

        import_json_specs(db, base_dir)
    finally:
        db.close()


if __name__ == "__main__":
    seed_initial_data()
