import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from server import STORE_PATH, load_store, save_store  # noqa: E402

REVIEW_TAG = "pendiente-revision"

RESEARCH_FILES = [
    "campari.json",
    "vermouth.json",
    "fernet.json",
    "gin_pisco_ramazzotti.json",
]


def slugify(value):
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "item"


def backup_store():
    backup_dir = STORE_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = backup_dir / f"store-{timestamp}-pre-new-cocktails.json"
    shutil.copy2(STORE_PATH, destination)
    return destination


def find_ingredient_id(store, name):
    candidate = name.strip().lower()
    for item in store["ingredients"]:
        if item["name"].strip().lower() == candidate:
            return item["id"]
    return None


def create_ingredient(store, name, category="Licores y aperitivos", alcoholic=True):
    next_ingredient_id = max((item["id"] for item in store["ingredients"]), default=0) + 1
    store["ingredients"].append(
        {
            "id": next_ingredient_id,
            "name": name,
            "category": category,
            "alcoholic": alcoholic,
            "tags": [],
            "image_url": "",
        }
    )
    return next_ingredient_id


NEW_INGREDIENTS_ALLOWED = {"Ramazzotti"}


def resolve_ingredient_id(store, name, created_log):
    existing = find_ingredient_id(store, name)
    if existing is not None:
        return existing
    if name not in NEW_INGREDIENTS_ALLOWED:
        raise ValueError(f"Ingrediente no encontrado y no esta permitido crearlo: {name!r}")
    new_id = create_ingredient(store, name)
    created_log.append((new_id, name))
    return new_id


def build_cocktail(store, item, next_cocktail_id, created_ingredients_log):
    requirements = []
    for index, requirement in enumerate(item["requirements"], start=1):
        option_ids = [resolve_ingredient_id(store, name, created_ingredients_log) for name in requirement["options"]]
        group_key = f"ingredient-{index}-{slugify(requirement['options'][0])}"
        requirements.append(
            {
                "group_key": group_key,
                "amount": requirement.get("amount", ""),
                "unit": requirement.get("unit", ""),
                "optional": bool(requirement.get("optional", False)),
                "options": option_ids,
            }
        )

    steps = [
        {"step_number": idx + 1, "instruction": text}
        for idx, text in enumerate(item["steps"])
    ]
    tags = list(dict.fromkeys([*item["tags"], REVIEW_TAG]))

    return {
        "id": next_cocktail_id,
        "name": item["name"],
        "description": item["description"],
        "image_url": item["image_url"],
        "prep_time_minutes": int(item["prep_time_minutes"]),
        "alcohol_level": item["alcohol_level"],
        "glassware": item["glassware"],
        "instructions": " ".join(item["steps"]),
        "rating": 0,
        "is_favorite": False,
        "is_active": True,
        "tags": tags,
        "steps": steps,
        "requirements": requirements,
        "source": {
            "provider": item.get("source_provider", ""),
            "source_url": item.get("source_url", ""),
        },
    }


def main():
    store = load_store()
    backup_path = backup_store()

    existing_names_lower = {c["name"].strip().lower() for c in store["cocktails"]}
    next_cocktail_id = max((c["id"] for c in store["cocktails"]), default=0) + 1

    all_items = []
    for filename in RESEARCH_FILES:
        path = SCRIPT_DIR / "_research" / filename
        all_items.extend(json.loads(path.read_text(encoding="utf-8")))

    created_ingredients_log = []
    added = []
    skipped = []

    for item in all_items:
        if item["name"].strip().lower() in existing_names_lower:
            skipped.append(item["name"])
            continue
        cocktail = build_cocktail(store, item, next_cocktail_id, created_ingredients_log)
        store["cocktails"].append(cocktail)
        existing_names_lower.add(item["name"].strip().lower())
        added.append((next_cocktail_id, item["name"]))
        next_cocktail_id += 1

    save_store(store)

    print(f"Backup: {backup_path}")
    print(f"Ingredientes nuevos creados: {created_ingredients_log}")
    print(f"Cocteles agregados ({len(added)}):")
    for cid, name in added:
        print(f"  [{cid}] {name}")
    if skipped:
        print(f"Cocteles omitidos por ya existir ({len(skipped)}): {skipped}")


if __name__ == "__main__":
    main()
