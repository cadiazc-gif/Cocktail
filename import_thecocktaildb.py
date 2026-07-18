import argparse
import json
import re
import shutil
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

from server import STORE_PATH, default_store, load_store, save_store


API_BASE = "https://www.thecocktaildb.com/api/json/v1/1"
MAX_INGREDIENT_SLOTS = 15


def slugify(value):
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "item"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_all_drinks():
    drinks_by_id = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        url = f"{API_BASE}/search.php?f={letter}"
        payload = fetch_json(url)
        for drink in payload.get("drinks") or []:
            drinks_by_id[drink["idDrink"]] = drink
    return list(drinks_by_id.values())


def split_instructions(raw_text):
    if not raw_text:
        return []
    normalized = raw_text.replace("\r", "\n")
    pieces = []
    for block in normalized.split("\n"):
        stripped = block.strip(" -\t")
        if not stripped:
            continue
        parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", stripped) if part.strip()]
        pieces.extend(parts if parts else [stripped])
    unique_steps = []
    for piece in pieces:
        if not unique_steps or unique_steps[-1] != piece:
            unique_steps.append(piece)
    return [{"step_number": index + 1, "instruction": text} for index, text in enumerate(unique_steps)]


def ensure_ingredient(store, ingredient_name, alcoholic=False):
    existing = next((item for item in store["ingredients"] if item["name"].lower() == ingredient_name.lower()), None)
    if existing:
        return existing["id"]
    next_ingredient_id = max((item["id"] for item in store["ingredients"]), default=0) + 1
    store["ingredients"].append(
        {
            "id": next_ingredient_id,
            "name": ingredient_name,
            "category": "Importado",
            "alcoholic": bool(alcoholic),
        }
    )
    return next_ingredient_id


def parse_requirements(drink, store):
    requirements = []
    ingredient_names = []
    for slot in range(1, MAX_INGREDIENT_SLOTS + 1):
        ingredient_name = (drink.get(f"strIngredient{slot}") or "").strip()
        if not ingredient_name:
            continue
        measure = (drink.get(f"strMeasure{slot}") or "").strip()
        ingredient_names.append(ingredient_name)
        ingredient_id = ensure_ingredient(store, ingredient_name)
        requirements.append(
            {
                "group_key": f"ingredient-{slot}-{slugify(ingredient_name)}",
                "amount": measure,
                "unit": "",
                "optional": False,
                "options": [ingredient_id],
            }
        )
    return requirements, ingredient_names


def parse_tags(drink):
    tags = []
    for candidate in [
        drink.get("strCategory"),
        drink.get("strGlass"),
        drink.get("strAlcoholic"),
        "thecocktaildb",
    ]:
        if not candidate:
            continue
        normalized = candidate.strip()
        if normalized and normalized not in tags:
            tags.append(normalized)
    return tags


def drink_to_cocktail(drink, store, existing_id=None):
    requirements, ingredient_names = parse_requirements(drink, store)
    instructions = (drink.get("strInstructions") or "").strip()
    category = (drink.get("strCategory") or "").strip()
    alcoholic_value = (drink.get("strAlcoholic") or "").strip().lower()
    is_alcoholic = "non alcoholic" not in alcoholic_value
    name = (drink.get("strDrink") or "").strip()
    image_url = (drink.get("strDrinkThumb") or "").strip()

    return {
        "id": existing_id,
        "name": name,
        "description": f"Importado desde TheCocktailDB. Categoria: {category or 'sin categoria'}.",
        "image_url": image_url,
        "prep_time_minutes": 5,
        "difficulty": "media",
        "strength": "sin alcohol" if not is_alcoholic else "media",
        "is_alcoholic": is_alcoholic,
        "instructions": instructions,
        "rating": 0,
        "is_favorite": False,
        "is_active": True,
        "tags": parse_tags(drink),
        "steps": split_instructions(instructions),
        "requirements": requirements,
        "source": {
            "provider": "TheCocktailDB",
            "source_id": drink.get("idDrink"),
            "source_url": f"https://www.thecocktaildb.com/drink/{drink.get('idDrink')}",
            "ingredients_text": ingredient_names,
        },
    }


def backup_store():
    if not STORE_PATH.exists():
        return None
    backup_dir = STORE_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = backup_dir / f"store-{timestamp}.json"
    shutil.copy2(STORE_PATH, destination)
    return destination


def import_catalog(replace_catalog=False):
    store = load_store() if STORE_PATH.exists() else default_store()
    backup_path = backup_store()
    drinks = fetch_all_drinks()

    if replace_catalog:
        store["cocktails"] = []

    existing_by_source_id = {
        (cocktail.get("source") or {}).get("source_id"): cocktail
        for cocktail in store["cocktails"]
        if cocktail.get("source")
    }
    existing_by_name = {cocktail["name"].lower(): cocktail for cocktail in store["cocktails"]}
    next_cocktail_id = max((item["id"] for item in store["cocktails"]), default=0) + 1

    imported = 0
    updated = 0
    for drink in drinks:
        source_id = drink.get("idDrink")
        name = (drink.get("strDrink") or "").strip()
        current = existing_by_source_id.get(source_id) or existing_by_name.get(name.lower())
        if current:
            cocktail = drink_to_cocktail(drink, store, existing_id=current["id"])
            current_index = next(index for index, item in enumerate(store["cocktails"]) if item["id"] == current["id"])
            store["cocktails"][current_index] = cocktail
            updated += 1
        else:
            cocktail = drink_to_cocktail(drink, store, existing_id=next_cocktail_id)
            store["cocktails"].append(cocktail)
            next_cocktail_id += 1
            imported += 1

    save_store(store)
    return {
        "total_fetched": len(drinks),
        "imported": imported,
        "updated": updated,
        "backup_path": str(backup_path) if backup_path else None,
        "store_path": str(STORE_PATH),
    }


def main():
    parser = argparse.ArgumentParser(description="Importa cocteles desde TheCocktailDB a data/store.json")
    parser.add_argument("--replace-catalog", action="store_true", help="Reemplaza el catalogo local antes de importar")
    args = parser.parse_args()
    try:
        result = import_catalog(replace_catalog=args.replace_catalog)
    except Exception as exc:
        print(f"Importacion fallida: {exc}", file=sys.stderr)
        raise
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
