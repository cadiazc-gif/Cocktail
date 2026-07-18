import json
import shutil
import time
import unicodedata
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"

ALLOWED_TAGS = {
    "agave", "amargo", "aperitivo", "argentino", "bar-top-chile", "brasileno", "cafe", "campari",
    "chileno", "chileno-autor", "citrico", "clasico", "cremoso", "espanol", "espumante",
    "estadounidense", "frances", "frutal", "gin", "highball", "ingles", "invierno", "italiano",
    "jerez", "last-word-family", "martini", "mexicano", "mezcal", "moderno", "mojito", "mule",
    "navidad", "negroni", "old-fashioned", "peruano", "pisco", "rapido", "refrescante",
    "siam-thai", "sobremesa", "sour", "tequila", "tiki", "top-bars", "top-bars-chile",
    "verano", "vino",
}


def normalize(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-enrichment-round2-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(STORE_PATH, backup_path)
    return backup_path


def ingredient_name(ingredient_id, ingredients_by_id):
    return (ingredients_by_id.get(ingredient_id) or {}).get("name", str(ingredient_id))


def ingredient_category(ingredient_id, ingredients_by_id):
    return (ingredients_by_id.get(ingredient_id) or {}).get("category", "")


def is_optional_garnish(requirement, ingredients_by_id):
    cats = {ingredient_category(option_id, ingredients_by_id) for option_id in requirement.get("options", [])}
    return requirement.get("optional") and cats <= {"Garnish", "Hierbas", "Frutas", "Condimentos"}


def main_ingredient_names(cocktail, ingredients_by_id):
    names = []
    for requirement in cocktail.get("requirements", []):
        if is_optional_garnish(requirement, ingredients_by_id):
            continue
        for option_id in requirement.get("options", []):
            name = ingredient_name(option_id, ingredients_by_id)
            if name.lower() != "hielo":
                names.append(name)
                break
    return names


def garnish_names(cocktail, ingredients_by_id):
    names = []
    for requirement in cocktail.get("requirements", []):
        if is_optional_garnish(requirement, ingredients_by_id):
            for option_id in requirement.get("options", []):
                names.append(ingredient_name(option_id, ingredients_by_id))
                break
    return names


def join_names(items):
    values = [item for item in items if item]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return ", ".join(values[:-1]) + f" y {values[-1]}"


def lower_glass(glass):
    return (glass or "copa de coctel").strip().lower()


def infer_family(cocktail, ingredients_by_id):
    name = normalize(cocktail.get("name", ""))
    glass = lower_glass(cocktail.get("glassware"))
    ingredient_names = [normalize(item) for item in main_ingredient_names(cocktail, ingredients_by_id)]
    all_text = " ".join([name, glass, normalize(cocktail.get("instructions", ""))])

    if "colada" in name or "frozen" in all_text:
        return "blend"
    if "mojito" in name:
        return "mojito"
    if "mule" in name:
        return "mule"
    if "spritz" in name:
        return "spritz"
    if "negroni" in name:
        return "negroni"
    if "martini" in name:
        return "martini"
    if "old fashioned" in name:
        return "old_fashioned"
    if "sour" in name:
        return "sour"
    if "fizz" in name or "collins" in name:
        return "fizz"
    if any(term in name for term in ["abc", "b-52", "b-53", "acid"]) or "shot" in glass:
        return "shot"
    if any(term in name for term in ["highball", "cola", "piston", "piscola"]):
        return "build"
    bubbly = {"soda", "agua con gas", "agua tonica", "ginger beer local", "cerveza de jengibre", "champagne", "prosecco", "cola"}
    if any(item in bubbly for item in ingredient_names):
        return "build"
    spirits = sum(1 for item in ingredient_names if ingredient_category(next((i for i in ingredients_by_id if normalize(ingredients_by_id[i]["name"]) == item), -1), ingredients_by_id) in {"Destilados", "Licores y aperitivos", "Bitters"})
    juices = sum(1 for item in ingredient_names if item.startswith("jugo"))
    if spirits >= 2 and juices == 0:
        return "stir"
    return "shake"


def sentence(text):
    clean = " ".join(text.split()).strip(" .")
    if not clean:
        return ""
    return clean[0].upper() + clean[1:] + "."


def build_step_lines(cocktail, ingredients_by_id):
    family = infer_family(cocktail, ingredients_by_id)
    glass = lower_glass(cocktail.get("glassware"))
    ingredients = main_ingredient_names(cocktail, ingredients_by_id)
    garnish = garnish_names(cocktail, ingredients_by_id)

    citrus = [name for name in ingredients if normalize(name).startswith("jugo de")]
    sweeteners = [name for name in ingredients if normalize(name) in {"jarabe simple", "jarabe de miel", "jarabe de agave", "azucar", "granadina", "syrup especiado"}]
    herbs = [name for name in ingredients if normalize(name) in {"menta", "albahaca", "lemongrass", "romero"}]
    bubbly = [name for name in ingredients if normalize(name) in {"soda", "agua con gas", "agua tonica", "ginger beer local", "cerveza de jengibre", "cola", "champagne", "prosecco"}]
    base = [name for name in ingredients if name not in citrus + sweeteners + herbs + bubbly]

    if family == "blend":
        lines = [
            sentence(f"Agregar {join_names(ingredients)} a una licuadora"),
            sentence("Agregar hielo a gusto y licuar hasta obtener una mezcla homogenea"),
            sentence(f"Servir en {glass}"),
        ]
    elif family == "mojito":
        first = join_names([item for item in [*herbs[:1], *sweeteners[:1], *citrus[:1]] if item]) or join_names(ingredients[:3])
        lines = [
            sentence(f"Agregar {first} al vaso y macerar suavemente"),
            sentence(f"Incorporar {join_names([item for item in base + ['Hielo'] if item])}"),
            sentence(f"Completar con {join_names(bubbly) or 'soda'} y servir en {glass}"),
        ]
    elif family == "mule":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names([item for item in base + citrus + sweeteners if item])}"),
            sentence(f"Completar con {join_names(bubbly) or 'ginger beer'} y mezclar suavemente"),
        ]
    elif family == "spritz":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names(base)}"),
            sentence(f"Completar con {join_names(bubbly)} y mezclar suavemente"),
        ]
    elif family == "negroni":
        lines = [
            sentence(f"Agregar {join_names(ingredients)} a un vaso mezclador"),
            sentence("Agregar hielo a gusto y revolver hasta enfriar bien"),
            sentence(f"Colar y servir en {glass}"),
        ]
    elif family == "martini":
        lines = [
            sentence(f"Agregar {join_names(ingredients)} a un vaso mezclador"),
            sentence("Agregar hielo a gusto y revolver hasta enfriar bien"),
            sentence(f"Colar y servir en {glass} fria"),
        ]
    elif family == "old_fashioned":
        aromatic = join_names([item for item in sweeteners + [name for name in ingredients if normalize(name).startswith("amargo")] if item]) or "los ingredientes aromaticos"
        base_join = join_names(base) or join_names(ingredients)
        lines = [
            sentence(f"Agregar {aromatic} al vaso y mezclar"),
            sentence(f"Incorporar {base_join} y hielo a gusto"),
            sentence(f"Revolver suavemente y servir en {glass}"),
        ]
    elif family == "sour":
        first = join_names(base + citrus + sweeteners)
        lines = [
            sentence(f"Agregar {first} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar y servir en {glass}"),
        ]
    elif family == "fizz":
        first = join_names(base + citrus + sweeteners)
        lines = [
            sentence(f"Agregar {first} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar en {glass} y completar con {join_names(bubbly) or 'soda'}"),
        ]
    elif family == "shot":
        lines = [
            sentence(f"Agregar {join_names(ingredients)} a un vaso mezclador o directamente al vaso"),
            sentence("Enfriar con hielo si corresponde"),
            sentence(f"Servir en {glass}"),
        ]
    elif family == "build":
        lines = [
            sentence(f"Llenar {glass} con hielo"),
            sentence(f"Agregar {join_names([item for item in base + citrus + sweeteners if item])}"),
            sentence(f"Completar con {join_names(bubbly) or 'el mixer correspondiente'} y mezclar suavemente"),
        ]
    else:
        lines = [
            sentence(f"Agregar {join_names(ingredients)} a una coctelera"),
            sentence("Agregar hielo a gusto y agitar hasta enfriar bien"),
            sentence(f"Colar y servir en {glass}"),
        ]

    if garnish:
        lines.append(sentence(f"Decorar con {join_names(garnish)} si deseas"))
    return [line for line in lines if line]


def infer_tags(cocktail, ingredients_by_id):
    current = set(cocktail.get("tags", []))
    if current & {"bar-top-chile", "chileno-autor", "top-bars", "siam-thai"}:
        inferred = set(current)
    else:
        inferred = set(current)

    name = normalize(cocktail.get("name", ""))
    description = normalize(cocktail.get("description", ""))
    source = normalize((cocktail.get("source") or {}).get("provider", ""))
    tags_text = " ".join([name, description, source])
    ingredient_names = [normalize(name) for name in main_ingredient_names(cocktail, ingredients_by_id)]

    inferred.add("clasico" if "moderno" not in inferred and "top-bars" not in inferred else "")

    if cocktail.get("prep_time_minutes", 0) <= 4:
        inferred.add("rapido")
    if cocktail.get("alcohol_level") == "Sin alcohol":
        inferred.add("refrescante")
    if cocktail.get("alcohol_level") == "Fuerte":
        inferred.add("amargo" if any(x in ingredient_names for x in {"campari", "amaro nonino", "amargo de angostura"}) else "")

    spirit_map = {
        "pisco": "pisco",
        "gin": "gin",
        "tequila": "tequila",
        "mezcal": "mezcal",
        "campari": "campari",
    }
    for key, tag in spirit_map.items():
        if any(key in item for item in ingredient_names) or key in tags_text:
            inferred.add(tag)

    if any(item.startswith("jugo de") or item in {"lima", "limon", "naranja", "pomelo"} for item in ingredient_names):
        inferred.add("citrico")
    if any(item in {"frutillas", "papaya", "frambuesa", "jugo de pinia", "jugo de maracuya", "durazno"} for item in ingredient_names):
        inferred.add("frutal")
    if any(item in {"crema espesa", "leche", "leche condensada", "clara de huevo", "crema de coco", "leche de coco"} for item in ingredient_names):
        inferred.add("cremoso")
    if any(item in {"campari", "amargo de angostura", "araucano", "suze"} for item in ingredient_names):
        inferred.add("amargo")
    if any(item in {"champagne", "prosecco"} for item in ingredient_names):
        inferred.add("espumante")
    if any(item in {"vino tinto", "vino blanco", "vermut rojo", "vermut dulce", "fino", "manzanilla", "jerez"} for item in ingredient_names):
        inferred.add("vino")
    if any(item in {"cafe", "cafe espresso", "cafe instantaneo"} for item in ingredient_names):
        inferred.add("cafe")

    family = infer_family(cocktail, ingredients_by_id)
    family_tags = {
        "mojito": "mojito",
        "mule": "mule",
        "negroni": "negroni",
        "martini": "martini",
        "old_fashioned": "old-fashioned",
        "sour": "sour",
        "blend": "tiki",
        "spritz": "aperitivo",
    }
    if family in family_tags:
        inferred.add(family_tags[family])

    if any(term in tags_text for term in ["italia", "italiano"]):
        inferred.add("italiano")
    if any(term in tags_text for term in ["mexico", "mexicano"]):
        inferred.add("mexicano")
    if any(term in tags_text for term in ["peru", "peruano"]):
        inferred.add("peruano")
    if any(term in tags_text for term in ["argentina", "argentino"]):
        inferred.add("argentino")
    if any(term in tags_text for term in ["ingles", "england", "savoy"]):
        inferred.add("ingles")
    if any(term in tags_text for term in ["francia", "frances"]):
        inferred.add("frances")
    if any(term in tags_text for term in ["brasil", "brasileno"]):
        inferred.add("brasileno")
    if any(term in tags_text for term in ["estados unidos", "american", "milk & honey", "death & co", "modern classic"]):
        inferred.add("estadounidense")
    if any(term in tags_text for term in ["chile", "chileno"]):
        inferred.add("chileno")

    if any(term in tags_text for term in ["moderno", "top-bars", "milk & honey", "death & co", "joaquin simo", "phil ward", "jorg meyer"]):
        inferred.add("moderno")
    if any(term in tags_text for term in ["top-bars", "bar-top-chile", "siam thai", "bar la providencia", "chipe libre"]):
        inferred.add("top-bars")

    final = sorted(tag for tag in inferred if tag in ALLOWED_TAGS and tag)
    return final


def apply_enrichment():
    store = load_store()
    backup = backup_store()
    ingredients_by_id = {ingredient["id"]: ingredient for ingredient in store.get("ingredients", [])}
    tags_updated = 0
    steps_updated = 0

    for cocktail in store.get("cocktails", []):
        new_tags = infer_tags(cocktail, ingredients_by_id)
        if new_tags != cocktail.get("tags", []):
            cocktail["tags"] = new_tags
            tags_updated += 1

        new_step_lines = build_step_lines(cocktail, ingredients_by_id)
        new_steps = [{"step_number": index, "instruction": line} for index, line in enumerate(new_step_lines, start=1)]
        old_text = "\n".join(step.get("instruction", "") for step in cocktail.get("steps", []))
        new_text = "\n".join(line for line in new_step_lines)
        if new_text and old_text != new_text:
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
    apply_enrichment()
