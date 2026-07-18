import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


UNIT_TRANSLATIONS = {
    "oz": "oz",
    "shot": "shot",
    "shots": "shots",
    "tsp": "cdita",
    "tblsp": "cda",
    "dash": "dash",
    "dashes": "dash",
    "part": "parte",
    "parts": "partes",
    "cup": "taza",
    "cups": "tazas",
    "cl": "cl",
    "ml": "ml",
    "slice": "rodaja",
    "bottle": "botella",
    "splash": "splash",
    "whole": "unidad",
    "drop": "gotas",
    "drops": "gotas",
    "scoops": "cucharadas",
    "scoop": "cucharadas",
    "cube": "cubos",
    "cubes": "cubos",
    "pinch": "pizca",
    "twist": "twist",
    "l": "L",
    "gal": "gal",
    "qt": "qt",
    "pint": "pinta",
}


PHRASE_TRANSLATIONS = [
    ("cocktail shaker", "coctelera"),
    ("shot glass", "vaso de shot"),
    ("highball glass", "vaso highball"),
    ("chilled glass", "vaso frio"),
    ("cold glass", "vaso frio"),
    ("cocktail glass", "copa de coctel"),
    ("mixing glass", "vaso mezclador"),
    ("ice cubes", "cubos de hielo"),
    ("crushed ice", "hielo triturado"),
    ("club soda", "club soda"),
    ("top with", "completa con"),
    ("fill with", "llena con"),
    ("strain into", "cuela en"),
    ("strain", "cuela"),
    ("shake", "agita"),
    ("stir", "revuelve"),
    ("pour", "vierte"),
    ("add", "agrega"),
    ("serve", "sirve"),
    ("garnish", "decora"),
    ("muddle", "macera"),
    ("combine", "mezcla"),
    ("blend", "licua"),
    ("mix", "mezcla"),
    ("blender", "licuadora"),
    ("freeze", "congela"),
    ("until smooth", "hasta que quede suave"),
    ("sparkling wine", "vino espumante"),
    ("warmed mug", "taza caliente"),
    ("flute", "flauta"),
    ("ice", "hielo"),
    ("fill", "llena"),
    ("glass", "vaso"),
]


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def translate_step(text):
    result = (text or "").strip()
    if not result:
        return result
    if re.search(r"[áéíóúñ]", result.lower()):
        return result
    translated = result
    for source, target in PHRASE_TRANSLATIONS:
        translated = re.sub(rf"\b{re.escape(source)}\b", target, translated, flags=re.IGNORECASE)
    translated = translated.replace(" ,", ",").replace(" .", ".")
    translated = translated[0].upper() + translated[1:] if translated else translated
    return translated


def normalize_requirement(requirement):
    amount = (requirement.get("amount") or "").strip()
    unit = (requirement.get("unit") or "").strip()
    original = amount
    if unit:
        translated_unit = UNIT_TRANSLATIONS.get(unit.lower(), unit)
        requirement["amount"] = amount
        requirement["unit"] = translated_unit
        return

    low = amount.lower()
    if low in {"top", "top up with", "fill with"}:
        requirement["amount"] = "a completar"
        requirement["unit"] = ""
        return
    if low in {"to taste", "al gusto"}:
        requirement["amount"] = "a gusto"
        requirement["unit"] = ""
        return
    if low in {"garnish with"}:
        requirement["amount"] = "para decorar"
        requirement["unit"] = ""
        return
    if low in {"crushed", "frozen", "chopped"}:
        requirement["amount"] = low
        requirement["unit"] = ""
        return
    if low == "cubes":
        requirement["amount"] = "a gusto"
        requirement["unit"] = "cubos"
        return
    if low.startswith("juice of "):
        requirement["amount"] = low.replace("juice of ", "").strip()
        requirement["unit"] = "unidad"
        return
    if low.startswith("twist of"):
        requirement["amount"] = "1"
        requirement["unit"] = "twist"
        return
    if re.match(r"^[0-9/.\- ]+\s+twist of$", low):
        requirement["amount"] = low.replace("twist of", "").strip()
        requirement["unit"] = "twist"
        return
    if low in {"dash", "dash."}:
        requirement["amount"] = "1"
        requirement["unit"] = "dash"
        return
    if low in {"pinch", "pinch."}:
        requirement["amount"] = "1"
        requirement["unit"] = "pizca"
        return
    if low in {"wedges", "wedge"}:
        requirement["amount"] = "1"
        requirement["unit"] = "rodaja"
        return
    if low in {"full glass", "fill to top with", "top up"}:
        requirement["amount"] = "a completar"
        requirement["unit"] = ""
        return

    cleaned = re.sub(r"\s+(white|bacardi|superfine|cold|frozen|fresh)$", "", original, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+(red|green ginger|green|light or dark|light|dark|instant|muscatel|whole|plain|black|hot|iced|chilled|finely chopped dark|blended)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^([0-9/.\- ]+)\s+fresh$", r"\1", cleaned, flags=re.IGNORECASE)
    match = re.match(r"^([0-9/.\- ]+)\s+([A-Za-z]+)$", cleaned)
    if match:
        parsed_amount = match.group(1).strip()
        parsed_unit = UNIT_TRANSLATIONS.get(match.group(2).lower(), match.group(2))
        requirement["amount"] = parsed_amount
        requirement["unit"] = parsed_unit
        return

    requirement["amount"] = original
    requirement["unit"] = unit


def main():
    store = load_store()
    translated_steps = 0
    normalized_units = 0
    units_catalog = set(store.setdefault("settings", {}).get("units_catalog", []))

    for cocktail in store["cocktails"]:
        instructions = (cocktail.get("instructions") or "").strip()
        if instructions:
            translated = translate_step(instructions)
            if translated != instructions:
                cocktail["instructions"] = translated
                translated_steps += 1
        for step in cocktail.get("steps", []):
            original = step.get("instruction", "")
            translated = translate_step(original)
            if translated != original:
                step["instruction"] = translated
                translated_steps += 1
        for requirement in cocktail.get("requirements", []):
            before = (requirement.get("amount", ""), requirement.get("unit", ""))
            normalize_requirement(requirement)
            after = (requirement.get("amount", ""), requirement.get("unit", ""))
            if before != after:
                normalized_units += 1
            if requirement.get("unit"):
                units_catalog.add(requirement["unit"])

    store["settings"]["units_catalog"] = sorted(units_catalog, key=str.lower)
    save_store(store)
    print(f"pasos traducidos: {translated_steps}")
    print(f"cantidades/unidades normalizadas: {normalized_units}")


if __name__ == "__main__":
    main()
