import json
import shutil
import time
import unicodedata
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"

GARNISH_UNITS = {
    "twist", "rodaja", "slice", "gajo", "sprig", "rama", "ramita", "hoja", "hojas",
    "wheel", "wedge", "peel", "cascara",
}
MAIN_BUBBLY = {
    "soda", "agua con gas", "agua tonica", "cerveza de jengibre", "ginger beer local",
    "ginger ale", "coca-cola", "cola", "champagne", "prosecco", "bebida", "bebida lima-limon", "bebida de limon",
    "bebida de uva",
}
MAIN_SWEETENERS = {
    "jarabe simple", "jarabe de miel", "jarabe de agave", "azucar", "azucar flor",
    "granadina", "syrup especiado", "jarabe de horchata", "mezcla agridulce", "limonada",
}
MUDDLE_HERBS = {"menta", "albahaca", "romero", "lemongrass"}
DIRECT_GARNISH_NAMES = {
    "aceituna", "cereza marrasquino", "cascara de naranja", "cascara de limon",
    "cascara de lima", "espiral de naranja", "espiral de limon", "naranja deshidratada",
    "deshidratado de naranja",
}
STIRRED_NAMES = {
    "manhattan", "boulevardier", "martinez", "rob roy", "bijou", "martini", "dry martini",
    "pichuncho", "negroni", "white negroni", "pisco negroni", "el capitan", "lucien gaudin",
}


def normalize(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def sentence(text):
    clean = " ".join((text or "").split()).strip(" .")
    if not clean:
        return ""
    return clean[0].upper() + clean[1:] + "."


def lower_glass(glass):
    return (glass or "copa de coctel").strip().lower()


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-step-refine-round3-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(STORE_PATH, backup_path)
    return backup_path


def ingredient_entry(requirement, ingredients_by_id):
    option_id = next(iter(requirement.get("options", [])), None)
    ingredient = ingredients_by_id.get(option_id) or {}
    return {
        "name": ingredient.get("name", str(option_id)),
        "category": ingredient.get("category", ""),
        "amount": (requirement.get("amount") or "").strip(),
        "unit": (requirement.get("unit") or "").strip(),
        "optional": requirement.get("optional", False),
    }


def is_garnish(entry):
    name = normalize(entry["name"])
    unit = normalize(entry["unit"])
    category = entry["category"]
    amount = normalize(entry["amount"])

    if name == "hielo":
        return False
    if category == "Garnish":
        return True
    if entry["optional"] and category in {"Hierbas", "Frutas", "Condimentos"}:
        return True
    if unit in GARNISH_UNITS and category in {"Frutas", "Hierbas", "Condimentos", "Garnish"}:
        return True
    if name in DIRECT_GARNISH_NAMES:
        return True
    if amount == "1" and not unit and name in {"aceituna", "cereza marrasquino", "naranja", "limon", "lima"}:
        return True
    return False


def split_entries(cocktail, ingredients_by_id):
    main = []
    garnish = []
    for requirement in cocktail.get("requirements", []):
        if not requirement.get("options"):
            continue
        entry = ingredient_entry(requirement, ingredients_by_id)
        if normalize(entry["name"]) == "hielo":
            continue
        if is_garnish(entry):
            garnish.append(entry)
        else:
            main.append(entry)
    return main, garnish


def join_names(names):
    values = [value for value in names if value]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + f" y {values[-1]}"


def family_of(cocktail, main_entries):
    name = normalize(cocktail.get("name", ""))
    glass = lower_glass(cocktail.get("glassware"))
    names = [normalize(entry["name"]) for entry in main_entries]

    if name in STIRRED_NAMES or "manhattan" in name:
        return "stir"
    if "french 75" in name:
        return "french75"
    if "old fashioned" in name or "old-fashioned" in name:
        return "old_fashioned"
    if "negroni" in name:
        return "stir"
    if "martini" in name:
        return "stir"
    if "mojito" in name:
        return "mojito"
    if "mule" in name:
        return "mule"
    if "spritz" in name:
        return "spritz"
    if "sour" in name:
        return "sour"
    if "fizz" in name or "collins" in name:
        return "fizz"
    if any(term in name for term in ["piscola", "piston", "batanga", "cuba libre", "terremoto", "aperol spritz"]):
        return "build"
    if "colada" in name or "frozen" in normalize(cocktail.get("instructions", "")):
        return "blend"
    if glass.startswith("shot") or any(term in name for term in ["b-52", "b-53", "abc"]):
        return "shot"

    categories = [entry["category"] for entry in main_entries]
    bubbly = any(normalize(entry["name"]) in MAIN_BUBBLY for entry in main_entries)
    citrus = any(normalize(entry["name"]).startswith("jugo de") for entry in main_entries)
    spirits = sum(1 for category in categories if category in {"Destilados", "Licores y aperitivos", "Bitters"})

    sparkling = any(normalize(entry["name"]) in {"champagne", "prosecco"} for entry in main_entries)
    if bubbly and citrus and sparkling:
        return "french75"
    if bubbly and not sparkling:
        return "build"
    if spirits >= 2 and not citrus:
        return "stir"
    return "shake"


def names_by(entries, predicate):
    return [entry["name"] for entry in entries if predicate(entry)]


def build_lines(cocktail, main_entries, garnish_entries):
    family = family_of(cocktail, main_entries)
    glass = lower_glass(cocktail.get("glassware"))

    names = [entry["name"] for entry in main_entries]
    citrus = names_by(main_entries, lambda e: normalize(e["name"]).startswith("jugo de") or normalize(e["name"]) in {"lima", "limon", "naranja", "pomelo"})
    sweeteners = names_by(main_entries, lambda e: normalize(e["name"]) in MAIN_SWEETENERS)
    herbs = names_by(main_entries, lambda e: normalize(e["name"]) in MUDDLE_HERBS)
    bubbly = names_by(main_entries, lambda e: normalize(e["name"]) in MAIN_BUBBLY)
    bitters = names_by(main_entries, lambda e: normalize(e["name"]).startswith("amargo"))
    non_bubbly = [entry["name"] for entry in main_entries if normalize(entry["name"]) not in MAIN_BUBBLY]
    base = [entry["name"] for entry in main_entries if entry["name"] not in citrus + sweeteners + herbs + bubbly]

    if family == "blend":
        lines = [
            sentence(f"Agregar {join_names(names)} a una licuadora"),
            sentence("Agregar hielo a gusto y licuar hasta obtener una mezcla homogenea"),
            sentence(f"Servir en {glass}"),
        ]
    elif family == "mojito":
        muddle = join_names([item for item in [*herbs[:1], *sweeteners[:1], *citrus[:1]] if item]) or join_names(names[:3])
        remaining = [item for item in base if item not in herbs + sweeteners + citrus]
        lines = [
            sentence(f"Agregar {muddle} al vaso y macerar suavemente"),
            sentence(f"Incorporar {join_names(remaining or base)} y hielo a gusto"),
            sentence(f"Completar con {join_names(bubbly) or 'agua con gas'}, mezclar suavemente y servir en {glass}"),
        ]
    elif family == "mule":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names([item for item in non_bubbly if item])}"),
            sentence(f"Completar con {join_names(bubbly) or 'cerveza de jengibre'} y mezclar suavemente"),
        ]
    elif family == "spritz":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names([item for item in non_bubbly if item])}"),
            sentence(f"Completar con {join_names(bubbly)} y mezclar suavemente"),
        ]
    elif family == "french75":
        non_sparkling = [item for item in names if item not in bubbly]
        lines = [
            sentence(f"Agregar {join_names(non_sparkling)} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar en {glass} y completar con {join_names(bubbly) or 'champagne'}"),
        ]
    elif family == "stir":
        lines = [
            sentence(f"Agregar {join_names(names)} a un vaso mezclador"),
            sentence("Agregar hielo a gusto y revolver hasta enfriar bien"),
            sentence(f"Colar y servir en {glass} bien frio"),
        ]
    elif family == "old_fashioned":
        aromatic = join_names(sweeteners + bitters) or "los ingredientes aromaticos"
        spirit = join_names([item for item in base if item not in bitters]) or join_names(base) or join_names(names)
        lines = [
            sentence(f"Agregar {aromatic} al vaso y mezclar hasta integrar"),
            sentence(f"Incorporar {spirit} y hielo a gusto"),
            sentence(f"Revolver suavemente y servir en {glass}"),
        ]
    elif family == "sour":
        lines = [
            sentence(f"Agregar {join_names(names)} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar y servir en {glass}"),
        ]
    elif family == "fizz":
        lines = [
            sentence(f"Agregar {join_names([item for item in non_bubbly if item])} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar en {glass} y completar con {join_names(bubbly) or 'soda'}"),
        ]
    elif family == "build":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names([item for item in non_bubbly if item])}"),
            sentence(f"Completar con {join_names(bubbly) or 'el mixer correspondiente'} y mezclar suavemente"),
        ]
    elif family == "shot":
        lines = [
            sentence(f"Agregar {join_names(names)} al vaso o al recipiente de mezcla"),
            sentence("Enfriar si corresponde"),
            sentence(f"Servir en {glass}"),
        ]
    else:
        lines = [
            sentence(f"Agregar {join_names(names)} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar y servir en {glass}"),
        ]

    garnish_names = [entry["name"] for entry in garnish_entries]
    if garnish_names:
        lines.append(sentence(f"Decorar con {join_names(garnish_names)}"))
    return [line for line in lines if line]


def refine_steps():
    store = load_store()
    backup = backup_store()
    ingredients_by_id = {ingredient["id"]: ingredient for ingredient in store.get("ingredients", [])}
    steps_updated = 0

    for cocktail in store.get("cocktails", []):
        main_entries, garnish_entries = split_entries(cocktail, ingredients_by_id)
        new_lines = build_lines(cocktail, main_entries, garnish_entries)
        old_text = "\n".join(step.get("instruction", "") for step in cocktail.get("steps", []))
        new_text = "\n".join(new_lines)
        if new_text and new_text != old_text:
            cocktail["steps"] = [
                {"step_number": index, "instruction": line}
                for index, line in enumerate(new_lines, start=1)
            ]
            cocktail["instructions"] = new_text
            steps_updated += 1

    save_store(store)
    print(json.dumps({
        "backup": str(backup),
        "steps_updated": steps_updated,
        "total_cocktails": len(store.get("cocktails", [])),
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    refine_steps()
