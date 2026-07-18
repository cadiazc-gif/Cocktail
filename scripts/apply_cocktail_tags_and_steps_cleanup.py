import json
import shutil
import time
from pathlib import Path

from export_cocktail_audit import normalize, proposed_steps


BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"

ALLOWED_TAGS = {
    "agave",
    "amargo",
    "aperitivo",
    "argentino",
    "bar-top-chile",
    "brasileno",
    "cafe",
    "campari",
    "chileno",
    "chileno-autor",
    "citrico",
    "clasico",
    "cremoso",
    "espanol",
    "espumante",
    "estadounidense",
    "frances",
    "frutal",
    "gin",
    "highball",
    "ingles",
    "invierno",
    "italiano",
    "jerez",
    "last-word-family",
    "martini",
    "mexicano",
    "mezcal",
    "moderno",
    "mojito",
    "mule",
    "navidad",
    "negroni",
    "old-fashioned",
    "peruano",
    "pisco",
    "rapido",
    "refrescante",
    "siam-thai",
    "sobremesa",
    "sour",
    "tequila",
    "tiki",
    "top-bars",
    "top-bars-chile",
    "verano",
    "vino",
}


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-tags-steps-cleanup-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(STORE_PATH, backup_path)
    return backup_path


def normalize_tags(tags):
    normalized_tags = []
    seen = set()
    for tag in tags or []:
        clean = normalize(tag)
        if not clean or clean not in ALLOWED_TAGS or clean in seen:
            continue
        seen.add(clean)
        normalized_tags.append(clean)
    return sorted(normalized_tags)


def numbered_lines_to_steps(text):
    steps = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ")" in line[:4]:
            _, instruction = line.split(")", 1)
        elif "." in line[:4]:
            _, instruction = line.split(".", 1)
        else:
            instruction = line
        steps.append(instruction.strip().rstrip(".") + ".")
    return [{"step_number": index, "instruction": step} for index, step in enumerate(steps, start=1)]


def apply_cleanup():
    store = load_store()
    backup = backup_store()
    ingredients_by_id = {ingredient["id"]: ingredient for ingredient in store.get("ingredients", [])}

    tags_updated = 0
    steps_updated = 0

    for cocktail in store.get("cocktails", []):
        cleaned_tags = normalize_tags(cocktail.get("tags", []))
        if cleaned_tags != cocktail.get("tags", []):
            cocktail["tags"] = cleaned_tags
            tags_updated += 1

        proposal_text = proposed_steps(cocktail, ingredients_by_id)
        new_steps = numbered_lines_to_steps(proposal_text)
        old_steps = cocktail.get("steps", [])
        old_text = "\n".join(step.get("instruction", "") for step in old_steps)
        new_text = "\n".join(step["instruction"] for step in new_steps)
        if old_text != new_text:
            cocktail["steps"] = new_steps
            cocktail["instructions"] = new_text
            steps_updated += 1

    save_store(store)
    print(json.dumps({
        "backup": str(backup),
        "tags_updated": tags_updated,
        "steps_updated": steps_updated,
        "total_cocktails": len(store.get("cocktails", [])),
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    apply_cleanup()
