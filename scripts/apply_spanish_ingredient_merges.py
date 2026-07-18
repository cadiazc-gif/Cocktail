import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


SAFE_MERGES = [
    ("Mint", "Menta"),
    ("Lemon Juice", "Jugo de limon"),
    ("Fresh Lemon Juice", "Jugo de limon"),
    ("Lime juice", "Jugo de lima"),
    ("Fresh Lime Juice", "Jugo de lima"),
    ("Pineapple juice", "Jugo de pinia"),
    ("Sugar syrup", "Jarabe simple"),
    ("Sugar", "Azucar"),
    ("Cream of coconut", "Crema de coco"),
    ("Angostura Bitters", "Amargo de angostura"),
    ("Soda Water", "Agua con gas"),
]


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def find_ingredient(store, name):
    return next((item for item in store["ingredients"] if item["name"].strip().lower() == name.strip().lower()), None)


def merge_ingredient_ids(store, source_id, target_id):
    affected = 0
    for cocktail in store["cocktails"]:
        touched = False
        for requirement in cocktail.get("requirements", []):
            if source_id in requirement.get("options", []):
                touched = True
            requirement["options"] = sorted(dict.fromkeys(target_id if option == source_id else option for option in requirement.get("options", [])))
        if touched:
            affected += 1

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
        bucket = merged_shopping.setdefault(
            ingredient_id,
            {"ingredient_id": ingredient_id, "note": "", "done": True},
        )
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
    return affected


def rename_tonic_to_spanish(store):
    tonic = find_ingredient(store, "Tonic water")
    if tonic:
        tonic["name"] = "Agua tonica"
        tonic["category"] = tonic.get("category") or "Mezcladores"
        tonic["tags"] = sorted(dict.fromkeys([*(tonic.get("tags") or []), "mezclador"]))
    return tonic


def add_club_soda_replacement(store):
    club = find_ingredient(store, "Club soda")
    tonic = find_ingredient(store, "Agua tonica")
    if not club or not tonic:
        return 0
    affected = 0
    for cocktail in store["cocktails"]:
        for requirement in cocktail.get("requirements", []):
            options = requirement.get("options", [])
            if club["id"] in options and tonic["id"] not in options:
                requirement["options"] = sorted(dict.fromkeys([*options, tonic["id"]]))
                affected += 1
    return affected


def main():
    store = load_store()
    summary = []

    for source_name, target_name in SAFE_MERGES:
        source = find_ingredient(store, source_name)
        target = find_ingredient(store, target_name)
        if not source or not target:
            continue
        affected = merge_ingredient_ids(store, source["id"], target["id"])
        summary.append(f"{source_name} -> {target_name}: {affected} cocteles")

    rename_tonic_to_spanish(store)
    club_replacements = add_club_soda_replacement(store)
    save_store(store)

    print("fusiones aplicadas:")
    for line in summary:
        print(line)
    print(f"club soda con reemplazo agua tonica: {club_replacements} cocteles")


if __name__ == "__main__":
    main()
