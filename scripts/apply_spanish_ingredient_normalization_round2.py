import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


MERGES = [
    ("Apple juice", "Jugo de manzana"),
    ("Cherry Juice", "Jugo de cereza"),
    ("Cranberry juice", "Jugo de arandano"),
    ("Fruit juice", "Jugo de frutas"),
    ("Grape juice", "Jugo de uva"),
    ("Grapefruit juice", "Jugo de pomelo"),
    ("Orange juice", "Jugo de naranja"),
    ("Passion fruit juice", "Jugo de maracuya"),
    ("Pomegranate juice", "Jugo de granada"),
    ("Tomato Juice", "Jugo de tomate"),
    ("Agave Syrup", "Jarabe de agave"),
    ("Chocolate syrup", "Jarabe de chocolate"),
    ("Coconut syrup", "Jarabe de coco"),
    ("Ginger Syrup", "Jarabe de jengibre"),
    ("Honey syrup", "Jarabe de miel"),
    ("Maple syrup", "Jarabe de maple"),
    ("Mint syrup", "Jarabe de menta"),
    ("Passion fruit syrup", "Jarabe de maracuya"),
    ("Pineapple Syrup", "Jarabe de pina"),
    ("Raspberry syrup", "Jarabe de frambuesa"),
    ("Rosemary Syrup", "Jarabe de romero"),
    ("Vanilla syrup", "Jarabe de vainilla"),
    ("Coconut milk", "Leche de coco"),
    ("Condensed milk", "Leche condensada"),
    ("Milk", "Leche"),
    ("Water", "Agua"),
    ("Carbonated water", "Agua con gas"),
    ("Orange peel", "Cascara de naranja"),
    ("Lemon peel", "Cascara de limon"),
    ("Lime peel", "Cascara de lima"),
    ("Orange spiral", "Espiral de naranja"),
    ("Lemon", "Limon"),
    ("Lime", "Lima"),
    ("Orange", "Naranja"),
    ("Pineapple", "Pina"),
    ("Honey", "Miel"),
    ("Egg", "Huevo"),
    ("Egg White", "Clara de huevo"),
    ("Egg yolk", "Yema de huevo"),
    ("Cream", "Crema"),
    ("Heavy cream", "Crema espesa"),
    ("Light cream", "Crema ligera"),
    ("Whipped cream", "Crema batida"),
    ("Whipping cream", "Crema para batir"),
    ("Lemonade", "Limonada"),
    ("Limeade", "Limonada"),
    ("Pink lemonade", "Limonada"),
    ("Bitters", "Amargo"),
]


RENAMES = {
    "Orange bitters": "Amargo de naranja",
    "Peach Bitters": "Amargo de durazno",
    "Peychaud bitters": "Amargo Peychaud",
    "Ginger Beer": "Cerveza de jengibre",
    "Root beer": "Cerveza de raiz",
    "Bitter lemon": "Bebida de limon",
    "Grape Soda": "Bebida de uva",
    "Rum": "Ron",
    "Dark rum": "Ron oscuro",
    "Gold rum": "Ron dorado",
    "Light rum": "Ron claro",
    "White rum": "Ron blanco",
    "Añejo rum": "Ron añejo",
    "Spiced rum": "Ron especiado",
    "Malibu rum": "Ron Malibu",
    "151 proof rum": "Ron 151 grados",
    "blackstrap rum": "Ron blackstrap",
}


CREATES = {
    "Jugo de manzana": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de cereza": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de arandano": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de frutas": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de uva": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de pomelo": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de naranja": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de maracuya": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de granada": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jugo de tomate": {"category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
    "Jarabe de agave": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de chocolate": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de coco": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de jengibre": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de miel": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de maple": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de menta": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de maracuya": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de pina": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de frambuesa": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de romero": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Jarabe de vainilla": {"category": "Endulzantes", "alcoholic": False, "tags": ["jarabe"], "image_url": ""},
    "Leche de coco": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Leche condensada": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Leche": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Agua": {"category": "Basicos", "alcoholic": False, "tags": ["basico"], "image_url": ""},
    "Cascara de naranja": {"category": "Otros", "alcoholic": False, "tags": ["decoracion"], "image_url": ""},
    "Cascara de limon": {"category": "Otros", "alcoholic": False, "tags": ["decoracion"], "image_url": ""},
    "Cascara de lima": {"category": "Otros", "alcoholic": False, "tags": ["decoracion"], "image_url": ""},
    "Espiral de naranja": {"category": "Otros", "alcoholic": False, "tags": ["decoracion"], "image_url": ""},
    "Limon": {"category": "Citricos", "alcoholic": False, "tags": ["citricos"], "image_url": ""},
    "Lima": {"category": "Citricos", "alcoholic": False, "tags": ["citricos"], "image_url": ""},
    "Naranja": {"category": "Citricos", "alcoholic": False, "tags": ["citricos"], "image_url": ""},
    "Pina": {"category": "Jugos", "alcoholic": False, "tags": ["fruta"], "image_url": ""},
    "Miel": {"category": "Endulzantes", "alcoholic": False, "tags": ["endulzante"], "image_url": ""},
    "Huevo": {"category": "Basicos", "alcoholic": False, "tags": ["basico"], "image_url": ""},
    "Clara de huevo": {"category": "Basicos", "alcoholic": False, "tags": ["basico"], "image_url": ""},
    "Yema de huevo": {"category": "Basicos", "alcoholic": False, "tags": ["basico"], "image_url": ""},
    "Crema": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Crema espesa": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Crema ligera": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Crema batida": {"category": "Mezcladores", "alcoholic": False, "tags": ["decoracion"], "image_url": ""},
    "Crema para batir": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Limonada": {"category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
    "Amargo": {"category": "Bitters", "alcoholic": True, "tags": ["bitters"], "image_url": ""},
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
    print("normalizaciones aplicadas:")
    for line in summary:
        print(line)


if __name__ == "__main__":
    main()
