import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


RENAMES = {
    "Beer": "Cerveza",
    "Tea": "Te",
    "Fruit": "Fruta",
    "Blackberries": "Moras",
    "Cherries": "Cerezas",
    "Cherry": "Cereza",
    "Apple": "Manzana",
    "Banana": "Platano",
    "Kiwi": "Kiwi",
    "Mango": "Mango",
    "Papaya": "Papaya",
    "Cucumber": "Pepino",
    "Lavender": "Lavanda",
    "Cinnamon": "Canela",
    "Cloves": "Clavos de olor",
    "Nutmeg": "Nuez moscada",
    "Cardamom": "Cardamomo",
    "Coriander": "Cilantro",
    "Cumin seed": "Semilla de comino",
    "Celery salt": "Sal de apio",
    "Cayenne pepper": "Pimienta cayena",
    "Red Chili Flakes": "Aji en hojuelas",
    "Soy Sauce": "Salsa de soya",
    "Worcestershire Sauce": "Salsa Worcestershire",
    "Vanilla": "Vainilla",
    "Vanilla extract": "Extracto de vainilla",
    "Olive": "Aceituna",
    "Olive Brine": "Salmuera de aceituna",
    "Hot Sauce": "Salsa picante",
    "Cocoa powder": "Cacao en polvo",
    "Butter": "Mantequilla",
    "Coffee": "Cafe",
    "Espresso": "Cafe espresso",
    "Maraschino cherry": "Cereza marrasquino",
    "Strawberries": "Frutillas",
    "Yoghurt": "Yogur",
    "Rose": "Rosa",
    "Lemon-lime soda": "Bebida lima-limon",
    "Bebida gaseosa": "Bebida",
    "Bourbon": "Whiskey Bourbon",
    "Scotch": "Whisky escoces",
    "Islay single malt Scotch": "Scotch single malt",
    "Cider": "Sidra",
    "Lager": "Cerveza lager",
    "Port": "Oporto",
    "Ruby Port": "Oporto rubi",
    "Sherry": "Jerez",
    "Sherbet": "Helado",
    "Firewater": "Aguardiente",
    "Grain alcohol": "Alcohol de grano",
    "Hot Damn": "Fireball",
}


DELETE_INGREDIENTS = ["Caca"]


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def find_ingredient(store, name):
    return next((item for item in store["ingredients"] if item["name"].strip().lower() == name.strip().lower()), None)


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


def delete_ingredient(store, ingredient_id):
    affected = 0
    for cocktail in store["cocktails"]:
        new_requirements = []
        changed = False
        for requirement in cocktail.get("requirements", []):
            options = [option for option in requirement.get("options", []) if option != ingredient_id]
            if len(options) != len(requirement.get("options", [])):
                changed = True
            if options:
                requirement["options"] = options
                new_requirements.append(requirement)
        if changed:
            affected += 1
        cocktail["requirements"] = new_requirements
    store["ingredients"] = [item for item in store["ingredients"] if item["id"] != ingredient_id]
    store.get("inventory", {}).pop(str(ingredient_id), None)
    store["shopping"] = [item for item in store.get("shopping", []) if item["ingredient_id"] != ingredient_id]
    return affected


def add_sarsaparilla_replacement(store):
    sarsaparilla = find_ingredient(store, "Sarsaparilla")
    root_beer = find_ingredient(store, "Cerveza de raiz")
    if not sarsaparilla or not root_beer:
        return 0
    affected = 0
    for cocktail in store["cocktails"]:
        for requirement in cocktail.get("requirements", []):
            options = requirement.get("options", [])
            if sarsaparilla["id"] in options and root_beer["id"] not in options:
                requirement["options"] = sorted(dict.fromkeys([*options, root_beer["id"]]))
                affected += 1
    return affected


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

    replaced = add_sarsaparilla_replacement(store)
    if replaced:
        summary.append(f"Sarsaparilla con reemplazo Cerveza de raiz en {replaced} cocteles")

    for name in DELETE_INGREDIENTS:
        ingredient = find_ingredient(store, name)
        if ingredient:
            affected = delete_ingredient(store, ingredient["id"])
            summary.append(f"{name} eliminado de {affected} cocteles")

    save_store(store)
    print("normalizaciones ronda 5:")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()
