import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


RENAMES = {
    "Baileys irish cream": "Baileys crema irlandesa",
    "Godiva liqueur": "Licor Godiva",
    "Midori melon liqueur": "Licor de melon Midori",
    "maraschino liqueur": "Licor de maraschino",
    "demerara Sugar": "Azucar demerara",
    "Orgeat syrup": "Jarabe de horchata",
    "Sirup of roses": "Jarabe de rosas",
    "Peach Vodka": "Vodka de durazno",
    "Raspberry vodka": "Vodka de frambuesa",
    "Cranberry vodka": "Vodka de arandano",
    "Lime vodka": "Vodka de lima",
    "Blood Orange": "Naranja sanguina",
    "Apricot Nectar": "Nectar de damasco",
    "Peach nectar": "Nectar de durazno",
    "Blackcurrant cordial": "Cordial de grosella negra",
    "Elderflower cordial": "Cordial de flor de sauco",
    "Carbonated soft drink": "Bebida gaseosa",
    "Fruit punch": "Ponche de frutas",
    "Sour mix": "Mezcla sour",
    "Sweet and Sour": "Mezcla agridulce",
    "Half-and-half": "Mitad crema mitad leche",
    "Vanilla ice-cream": "Helado de vainilla",
    "Iced tea": "Te helado",
    "Red wine": "Vino tinto",
    "White Wine": "Vino blanco",
    "Wine": "Vino",
    "Rosemary": "Romero",
    "Thyme": "Tomillo",
    "Black pepper": "Pimienta negra",
    "Pepper": "Pimienta",
    "Salt": "Sal",
    "Brown sugar": "Azucar rubia",
    "Powdered sugar": "Azucar flor",
}


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def find_ingredient(store, name):
    return next((item for item in store["ingredients"] if item["name"].strip().lower() == name.strip().lower()), None)


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


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
    print("normalizaciones ronda 4:")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()
