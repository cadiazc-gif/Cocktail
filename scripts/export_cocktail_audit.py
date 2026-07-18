import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
EXPORT_DIR = BASE_DIR / "exports"


def normalize(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def ensure_export_dir():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def join_names(values):
    items = [item for item in values if item]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" y {items[-1]}"


def current_steps_text(cocktail):
    steps = [step.get("instruction", "").strip() for step in cocktail.get("steps", []) if step.get("instruction")]
    if steps:
        return "\n".join(f"{index}) {instruction}" for index, instruction in enumerate(steps, start=1))
    instructions = (cocktail.get("instructions") or "").strip()
    return instructions


def requirement_label(requirement):
    names = [option["name"] if isinstance(option, dict) else str(option) for option in requirement.get("options", [])]
    amount = (requirement.get("amount") or "").strip()
    unit = (requirement.get("unit") or "").strip()
    prefix = " ".join(part for part in [amount, unit] if part).strip()
    text = join_names(names)
    return f"{prefix} {text}".strip()


def ingredient_names_for_step(cocktail, ingredients_by_id):
    labels = []
    for requirement in cocktail.get("requirements", []):
        names = []
        for option in requirement.get("options", []):
            if isinstance(option, dict):
                names.append(option.get("name", ""))
            elif isinstance(option, int):
                ingredient = ingredients_by_id.get(option)
                names.append((ingredient or {}).get("name", str(option)))
            else:
                names.append(str(option))
        if names:
            labels.append(names[0])
    return labels


def clean_text(text):
    replacements = {
        "ingrediente es": "ingredientes",
        "el ingrediente es": "los ingredientes",
        "contents": "la mezcla",
        "layered": "servir en capas",
        "muddle": "macerar",
        "strain": "colar",
        "shake": "agitar",
        "stir": "mezclar",
        "float ": "dejar flotar ",
        "pour ": "verter ",
        "serve": "servir",
        "rim ": "escarchar ",
        "glass": "copa",
        "with ice": "con hielo",
        "into ": "en ",
    }
    value = text.strip()
    for source, target in replacements.items():
        value = re.sub(source, target, value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip(" .")
    if value:
        value = value[0].upper() + value[1:]
    return value


def infer_method(cocktail, raw_text):
    text = normalize(raw_text)
    if any(keyword in text for keyword in ["licua", "blender", "licuadora", "frozen"]):
        return "blend"
    if any(keyword in text for keyword in ["macer", "muddle"]):
        return "muddle"
    if any(keyword in text for keyword in ["revuelve", "revolver", "stir", "mezclador"]):
        return "stir"
    if any(keyword in text for keyword in ["build", "completa con", "top", "llenar el vaso"]):
        return "build"
    return "shake"


def proposed_steps(cocktail, ingredients_by_id):
    raw_steps = [clean_text(step.get("instruction", "")) for step in cocktail.get("steps", []) if step.get("instruction")]
    raw_text = " ".join(raw_steps) or clean_text(cocktail.get("instructions", ""))
    ingredients = ingredient_names_for_step(cocktail, ingredients_by_id)
    glassware = cocktail.get("glassware") or "copa de coctel"
    method = infer_method(cocktail, raw_text)

    if method == "blend":
        lines = [
            f"Agregar {join_names(ingredients)} a una licuadora.",
            "Agregar hielo a gusto y licuar hasta integrar bien.",
            f"Servir en {glassware.lower()}.",
        ]
    elif method == "muddle":
        lines = [
            f"Agregar {join_names(ingredients[:3])} al vaso o coctelera y macerar suavemente.",
            "Agregar el resto de los ingredientes e incorporar hielo a gusto.",
            f"Mezclar o agitar segun corresponda y servir en {glassware.lower()}.",
        ]
    elif method == "stir":
        lines = [
            f"Agregar {join_names(ingredients)} a un vaso mezclador.",
            "Agregar hielo a gusto y revolver hasta enfriar bien.",
            f"Colar y servir en {glassware.lower()}.",
        ]
    elif method == "build":
        lines = [
            f"Agregar {join_names(ingredients[:2] or ingredients)} al vaso.",
            "Agregar hielo a gusto y completar con el resto de los ingredientes.",
            f"Mezclar suavemente y servir en {glassware.lower()}.",
        ]
    else:
        lines = [
            f"Agregar {join_names(ingredients)} a una coctelera.",
            "Agregar hielo a gusto y agitar.",
            f"Colar y servir en {glassware.lower()}.",
        ]

    cleaned = []
    for index, line in enumerate(lines, start=1):
        line = clean_text(line)
        cleaned.append(f"{index}) {line}")
    return "\n".join(cleaned)


def tag_analysis(cocktails):
    tags = [tag for cocktail in cocktails for tag in cocktail.get("tags", [])]
    counts = Counter(tags)
    normalized_counts = Counter(normalize(tag) for tag in tags)

    drop_exact = {
        "thecocktaildb", "ordinary drink", "other / unknown", "coffee / tea",
        "soft drink", "homemade liqueur", "punch / party drink", "shake",
        "cocktail", "coffee mug", "irish coffee cup", "pitcher", "jar",
        "mason jar", "punch bowl", "beer mug", "beer pilsner", "copper mug",
        "brandy snifter", "coffee mug", "coffee cup", "cocktail glass",
    }
    vessel_words = {"glass", "mug", "cup", "bowl", "pitcher", "jar", "snifter", "pilsner"}

    drop_candidates = []
    keep_candidates = []
    for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].lower())):
        tag_norm = normalize(tag)
        words = set(tag_norm.replace("/", " ").split())
        if tag_norm in drop_exact:
            drop_candidates.append({"tag": tag, "count": count, "reason": "ruido / vaso / fuente / clasificacion importada"})
        elif "thecocktaildb" in tag_norm:
            drop_candidates.append({"tag": tag, "count": count, "reason": "fuente importada"})
        elif words & vessel_words:
            drop_candidates.append({"tag": tag, "count": count, "reason": "tipo de vaso o servicio, no tag conceptual"})
        else:
            keep_candidates.append({"tag": tag, "count": count})

    proposed_survivors = sorted({
        normalize(tag["tag"])
        for tag in keep_candidates
        if tag["count"] >= 2 or normalize(tag["tag"]) in {
            "chileno", "chileno-autor", "moderno", "top-bars", "bar-top-chile",
            "clasico", "aperitivo", "citrico", "frutal", "cremoso", "refrescante",
            "amargo", "gin", "pisco", "tequila", "mezcal", "mule", "negroni",
            "martini", "sour", "tiki", "verano", "invierno", "navidad",
        }
    })

    return {
        "total_tags_distintos": len(counts),
        "tags_conteo": [{"tag": tag, "count": count} for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))],
        "tags_normalizados_conteo": [{"tag_normalizado": tag, "count": count} for tag, count in sorted(normalized_counts.items(), key=lambda item: (-item[1], item[0]))],
        "propuesta_eliminar": drop_candidates,
        "propuesta_mantener": keep_candidates[:120],
        "propuesta_tags_supervivientes_normalizados": proposed_survivors,
    }


def export_catalog_csv(cocktails):
    path = EXPORT_DIR / "cocktails_catalog.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["nombre", "tags", "paso_a_paso"])
        for cocktail in sorted(cocktails, key=lambda item: item["name"].lower()):
            writer.writerow([
                cocktail["name"],
                ", ".join(cocktail.get("tags", [])),
                current_steps_text(cocktail),
            ])
    return path


def export_step_proposals_csv(cocktails, ingredients_by_id):
    path = EXPORT_DIR / "cocktail_steps_proposal.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["nombre", "tags", "paso_actual", "propuesta_paso_a_paso"])
        for cocktail in sorted(cocktails, key=lambda item: item["name"].lower()):
            writer.writerow([
                cocktail["name"],
                ", ".join(cocktail.get("tags", [])),
                current_steps_text(cocktail),
                proposed_steps(cocktail, ingredients_by_id),
            ])
    return path


def export_tag_analysis_json(cocktails):
    path = EXPORT_DIR / "cocktail_tags_analysis_proposal.json"
    path.write_text(json.dumps(tag_analysis(cocktails), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_tag_analysis_csv(cocktails):
    analysis = tag_analysis(cocktails)
    path = EXPORT_DIR / "cocktail_tags_drop_keep_proposal.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["tipo", "tag", "conteo", "motivo"])
        for item in analysis["propuesta_eliminar"]:
            writer.writerow(["eliminar", item["tag"], item["count"], item["reason"]])
        for item in analysis["propuesta_mantener"]:
            writer.writerow(["mantener", item["tag"], item["count"], "tag util"])
    return path


def main():
    ensure_export_dir()
    store = load_store()
    cocktails = store["cocktails"]
    ingredients_by_id = {ingredient["id"]: ingredient for ingredient in store.get("ingredients", [])}
    files = {
        "catalogo_csv": str(export_catalog_csv(cocktails)),
        "pasos_propuesta_csv": str(export_step_proposals_csv(cocktails, ingredients_by_id)),
        "tags_propuesta_json": str(export_tag_analysis_json(cocktails)),
        "tags_propuesta_csv": str(export_tag_analysis_csv(cocktails)),
        "total_cocktails": len(cocktails),
    }
    print(json.dumps(files, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
