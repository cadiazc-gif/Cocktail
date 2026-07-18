import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


MERGES = [
    ("Jagermeister", "Jägermeister"),
    ("Vermouth", "Vermut"),
    ("Dry Vermouth", "Vermut seco"),
    ("Sweet Vermouth", "Vermut dulce"),
    ("Rosso Vermouth", "Vermut rojo"),
]


RENAMES = {
    "Absinthe": "Absenta",
    "Anisette": "Aniseta",
    "Apple brandy": "Brandy de manzana",
    "Apricot brandy": "Brandy de damasco",
    "Blackberry brandy": "Brandy de mora",
    "Cherry brandy": "Brandy de cereza",
    "Coffee brandy": "Brandy de cafe",
    "Peach brandy": "Brandy de durazno",
    "Banana liqueur": "Licor de banana",
    "Cherry liqueur": "Licor de cereza",
    "Chocolate liqueur": "Licor de chocolate",
    "Coconut Liqueur": "Licor de coco",
    "Coffee liqueur": "Licor de cafe",
    "Kiwi liqueur": "Licor de kiwi",
    "Melon Liqueur": "Licor de melon",
    "Raspberry Liqueur": "Licor de frambuesa",
    "Blue Curacao": "Curacao azul",
    "Orange Curacao": "Curacao naranja",
    "Blended whiskey": "Whisky mezclado",
    "Blended Scotch": "Scotch mezclado",
    "Irish whiskey": "Whisky irlandes",
    "Rye Whiskey": "Whisky de centeno",
    "Tennessee whiskey": "Whisky de Tennessee",
    "Whiskey": "Whisky",
    "Black Sambuca": "Sambuca negra",
    "Butterscotch schnapps": "Schnapps de caramelo",
    "Peach schnapps": "Schnapps de durazno",
    "Strawberry schnapps": "Schnapps de frutilla",
    "Irish cream": "Crema irlandesa",
    "Creme de Banane": "Crema de banana",
    "Creme de Cacao": "Crema de cacao",
    "Creme de Cassis": "Crema de cassis",
    "Creme de Mure": "Crema de mora",
    "Green Creme de Menthe": "Crema de menta verde",
    "White Creme de Menthe": "Crema de menta blanca",
}


CREATES = {
    "Vermut": {"category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
    "Vermut seco": {"category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
    "Vermut dulce": {"category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
    "Vermut rojo": {"category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
}


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def find_ingredient(store, name):
    return next((item for item in store["ingredients"] if item["name"].strip().lower() == name.strip().lower()), None)


def ensure_ingredient(store, name):
    existing = find_ingredient(store, name)
    if existing:
        return existing
    base = CREATES[name]
    ingredient = {
        "id": next_id(store["ingredients"]),
        "name": name,
        "category": base["category"],
        "alcoholic": base["alcoholic"],
        "tags": list(base["tags"]),
        "image_url": base["image_url"],
    }
    store["ingredients"].append(ingredient)
    return ingredient


def merge_ingredient_ids(store, source_id, target_id):
    for cocktail in store["cocktails"]:
        for requirement in cocktail.get("requirements", []):
            requirement["options"] = sorted(dict.fromkeys(target_id if option == source_id else option for option in requirement.get("options", [])))

    if str(source_id) in store.get("inventory", {}):
        source_inventory = store["inventory"].pop(str(source_id))
        target_inventory = store["inventory"].get(str(target_id), {"in_stock": False, "low_stock": False, "quantity_label": ""})
        store["inventory"][str(target_id)] = {
            "in_stock": bool(target_inventory.get("in_stock")) or bool(source_inventory.get("in_stock")),
            "low_stock": bool(target_inventory.get("low_stock")) or bool(source_inventory.get("low_stock")),
            "quantity_label": target_inventory.get("quantity_label") or source_inventory.get("quantity_label", ""),
        }

    merged_shopping = {}
    for item in store.get("shopping", []):
        ingredient_id = target_id if item["ingredient_id"] == source_id else item["ingredient_id"]
        bucket = merged_shopping.setdefault(ingredient_id, {"ingredient_id": ingredient_id, "note": "", "done": True})
        if item.get("note") and not bucket["note"]:
            bucket["note"] = item.get("note", "")
        bucket["done"] = bucket["done"] and bool(item.get("done", False))
    store["shopping"] = list(merged_shopping.values())

    source = next(item for item in store["ingredients"] if item["id"] == source_id)
    target = next(item for item in store["ingredients"] if item["id"] == target_id)
    target["tags"] = sorted(dict.fromkeys([*(target.get("tags") or []), *(source.get("tags") or [])]))
    if not target.get("image_url"):
        target["image_url"] = source.get("image_url", "")
    store["ingredients"] = [item for item in store["ingredients"] if item["id"] != source_id]


def main():
    store = load_store()
    summary = []

    for source_name, target_name in MERGES:
        source = find_ingredient(store, source_name)
        if not source:
            continue
        target = ensure_ingredient(store, target_name)
        merge_ingredient_ids(store, source["id"], target["id"])
        summary.append(f"{source_name} -> {target_name}")

    for source_name, target_name in RENAMES.items():
        source = find_ingredient(store, source_name)
        if not source:
            continue
        collision = find_ingredient(store, target_name)
        if collision and collision["id"] != source["id"]:
            merge_ingredient_ids(store, source["id"], collision["id"])
        else:
            source["name"] = target_name
        summary.append(f"{source_name} => {target_name}")

    save_store(store)
    print("normalizaciones ronda 3:")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()
