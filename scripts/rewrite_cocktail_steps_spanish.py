import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


PHRASES = [
    ("do ahead:", "Preparacion anticipada:"),
    ("meanwhile", "Mientras tanto"),
    ("at least", "al menos"),
    ("overnight", "toda la noche"),
    ("hours", "horas"),
    ("hour", "hora"),
    ("minutes", "minutos"),
    ("minute", "minuto"),
    ("until thoroughly cold", "hasta que este bien frio"),
    ("until fully melted", "hasta que se derrita por completo"),
    ("until heated well", "hasta que se caliente bien"),
    ("until sugar dissolves", "hasta que el azucar se disuelva"),
    ("until smooth", "hasta que quede suave"),
    ("until well-chilled", "hasta que este bien frio"),
    ("until dissolved", "hasta que se disuelva"),
    ("over low heat", "a fuego bajo"),
    ("heat slowly", "calienta lentamente"),
    ("boil water and sugar", "hierve el agua con azucar"),
    ("bring sugar and", "lleva el azucar y"),
    ("to a boil", "a ebullicion"),
    ("cook, stirring constantly", "cocina revolviendo constantemente"),
    ("stirring constantly", "revolviendo constantemente"),
    ("remove from heat", "retira del fuego"),
    ("let sit", "deja reposar"),
    ("through a fine-mesh sieve", "por un colador fino"),
    ("cover and chill until cold", "cubre y enfria hasta que este frio"),
    ("transfer blender jar to freezer", "lleva la jarra de la licuadora al congelador"),
    ("freeze until almost solid", "congela hasta que este casi solido"),
    ("blend again", "licua nuevamente"),
    ("divide among glasses", "reparte entre los vasos"),
    ("using bar spoon", "usando una cuchara de bar"),
    ("revolutions", "giros"),
    ("old fashioned glass", "vaso old fashioned"),
    ("old fashioned vaso", "vaso old fashioned"),
    ("cocktail shaker", "coctelera"),
    ("take care to", "Procura"),
    ("moisten only the outer rim", "humedecer solo el borde exterior"),
    ("sprinkle the salt on it", "espolvorea la sal sobre el borde"),
    ("rub the rim of the glass with", "Humedece el borde del vaso con"),
    ("rub the rim of the vaso with", "Humedece el borde del vaso con"),
    ("to make the salt stick to it", "para que la sal se adhiera"),
    ("the salt should present to the lips of the imbiber and never mix into the cocktail", "Deja la sal solo en el borde para que no se mezcle con el coctel"),
    ("all of the ingredients", "todos los ingredientes"),
    ("all ingredients", "todos los ingredientes"),
    ("mint leaves", "hojas de menta"),
    ("lemon juice", "jugo de limon"),
    ("lime juice", "jugo de lima"),
    ("orange juice", "jugo de naranja"),
    ("cranberry juice", "jugo de arandano"),
    ("pineapple juice", "jugo de pinia"),
    ("simple syrup", "jarabe simple"),
    ("sweet vermouth", "vermut dulce"),
    ("dry vermouth", "vermut seco"),
    ("sparkling wine", "vino espumante"),
    ("orange slice", "rodaja de naranja"),
    ("lemon slice", "rodaja de limon"),
    ("lime slice", "rodaja de lima"),
    ("orange peel", "cascara de naranja"),
    ("lemon peel", "cascara de limon"),
    ("lime peel", "cascara de lima"),
    ("cherry", "cereza"),
    ("cracked ice", "hielo picado"),
    ("crushed ice", "hielo triturado"),
    ("ice cubes", "cubos de hielo"),
    ("ice cube", "cubo de hielo"),
    ("over ice", "sobre hielo"),
    ("with ice", "con hielo"),
    ("with cracked ice", "con hielo picado"),
    ("with crushed ice", "con hielo triturado"),
    ("filled with ice", "lleno de hielo"),
    ("filled with cubos de hielo", "lleno de cubos de hielo"),
    ("in a shaker half-filled with ice cubes", "En una coctelera medio llena de cubos de hielo"),
    ("in a shaker half-filled with cubos de hielo", "En una coctelera medio llena de cubos de hielo"),
    ("in a mixing glass half-filled with ice cubes", "En un vaso mezclador medio lleno de cubos de hielo"),
    ("in a mixing glass half-filled with cubos de hielo", "En un vaso mezclador medio lleno de cubos de hielo"),
    ("in a highball glass", "en un vaso highball"),
    ("in a tall glass", "en un vaso alto"),
    ("into a chilled glass", "en un vaso frio"),
    ("into a cold glass", "en un vaso frio"),
    ("into a cocktail glass", "en una copa de coctel"),
    ("into a shot glass", "en un vaso de shot"),
    ("into a highball glass", "en un vaso highball"),
    ("into a collins glass", "en un vaso collins"),
    ("into a flute", "en una copa flauta"),
    ("top up with", "completa con"),
    ("top with", "completa con"),
    ("build", "vierte"),
    ("layer", "sirve en capas"),
    ("fill the glass with", "llena el vaso con"),
    ("fill a tall glass with", "llena un vaso alto con"),
    ("garnish with", "decora con"),
    ("serve with straw", "sirve con bombilla"),
    ("serve over ice", "sirve sobre hielo"),
    ("serve.", "sirve."),
    ("shake well", "agita bien"),
    ("stir gently", "revuelve suavemente"),
    ("stir well", "revuelve bien"),
    ("mix well", "mezcla bien"),
    ("let sit", "deja reposar"),
    ("remove from heat", "retira del fuego"),
    ("bring sugar and", "lleva el azucar y"),
    ("to a boil", "a ebullicion"),
    ("cover and chill until cold", "cubre y enfria hasta que este frio"),
    ("freeze until almost solid", "congela hasta que este casi solido"),
    ("until smooth", "hasta que quede suave"),
    ("divide among glasses", "reparte entre los vasos"),
    ("layer ingredients", "sirve los ingredientes en capas"),
    ("layer in order", "sirve en capas en este orden"),
    ("blend again", "licua nuevamente"),
    ("blend", "licua"),
    ("pour", "vierte"),
    ("add", "agrega"),
    ("shake", "agita"),
    ("stir", "revuelve"),
    ("strain", "cuela"),
    ("serve", "sirve"),
    ("garnish", "decora"),
    ("mix", "mezcla"),
    ("muddle", "macera"),
    ("combine", "combina"),
    ("fill", "llena"),
]


WORDS = {
    "all": "todos",
    "ingredients": "ingredientes",
    "ingredient": "ingrediente",
    "the": "el",
    "and": "y",
    "into": "en",
    "in": "en",
    "on": "sobre",
    "with": "con",
    "without": "sin",
    "then": "luego",
    "carefully": "cuidadosamente",
    "slightly": "suavemente",
    "well": "bien",
    "gently": "suavemente",
    "smooth": "suave",
    "other": "otros",
    "glass": "vaso",
    "shaker": "coctelera",
    "blender": "licuadora",
    "chilled": "frio",
    "cold": "frio",
    "warm": "caliente",
    "warmed": "caliente",
    "mug": "taza",
    "flute": "copa flauta",
    "rocks": "hielo",
    "slice": "rodaja",
    "twist": "twist",
    "cherry": "cereza",
    "orange": "naranja",
    "lemon": "limon",
    "lime": "lima",
    "mint": "menta",
    "leaves": "hojas",
    "sugar": "azucar",
    "syrup": "jarabe",
    "juice": "jugo",
    "soda": "soda",
    "water": "agua",
    "splash": "splash",
    "straw": "bombilla",
    "vodka": "vodka",
    "gin": "gin",
    "rum": "ron",
    "whisky": "whisky",
    "whiskey": "whisky",
    "tequila": "tequila",
    "pineapple": "pina",
    "strawberries": "frutillas",
    "strawberry": "frutilla",
    "pan": "fuente",
    "bowl": "bol",
    "small": "pequeno",
    "medium": "mediano",
    "together": "juntos",
    "except": "excepto",
    "through": "por",
    "fully": "por completo",
    "melted": "derretido",
    "freezer": "congelador",
    "jar": "jarra",
    "cook": "cocina",
    "toast": "tuesta",
    "dried": "seco",
    "smoke": "ahuma",
    "foil": "papel aluminio",
    "wrap": "envuelve",
    "oven": "horno",
    "cover": "cubre",
    "chill": "enfria",
    "thickened": "espeso",
    "slushy": "granizado",
    "scrape": "raspa",
    "press": "presiones",
    "solid": "solido",
}


CLEANUPS = [
    ("humedece el borde del vaso con el rodaja de lima", "Humedece el borde del vaso con la rodaja de lima"),
    ("procura moisten only el outer rim y sprinkle el salt sobre it", "Humedece solo el borde exterior y espolvorea la sal sobre el borde"),
    ("el salt should present to el lips of el imbiber y never mezcla en el cocktail", "Deja la sal solo en el borde para que no se mezcle con el coctel"),
    ("other ingredientes", "demas ingredientes"),
    ("over hielo", "sobre hielo"),
    ("over cubos de hielo", "sobre cubos de hielo"),
    (" over ", " sobre "),
    (" until ", " hasta "),
    (" with ", " con "),
    (" into ", " en "),
    ("straw", "bombilla"),
    ("splash of soda agua", "un splash de soda"),
    ("splash de soda agua", "un splash de soda"),
    ("splash of", "un splash de"),
    ("cracked hielo", "hielo picado"),
    ("naranja jugo", "jugo de naranja"),
    ("lima jugo", "jugo de lima"),
    ("limon jugo", "jugo de limon"),
    ("cranberry jugo", "jugo de arandano"),
    ("menta hojas", "hojas de menta"),
    ("peach pure", "pure de durazno"),
    ("simple jarabe", "jarabe simple"),
    ("blackberry liqueur", "licor de mora"),
    ("vermouth", "vermut"),
    ("Tonic", "agua tonica"),
    ("tonic", "agua tonica"),
    ("old fashioned vaso", "vaso old fashioned"),
    ("highball vaso", "vaso highball"),
    ("collins vaso", "vaso collins"),
    ("lima rodaja", "rodaja de lima"),
    ("limon rodaja", "rodaja de limon"),
    ("naranja rodaja", "rodaja de naranja"),
    ("el cereza", "la cereza"),
    ("el naranja rodaja", "la rodaja de naranja"),
    ("el lima rodaja", "la rodaja de lima"),
    ("el rodaja de naranja", "la rodaja de naranja"),
    ("half rodaja de naranja", "media rodaja de naranja"),
    ("half naranja rodaja", "media rodaja de naranja"),
    ("it todos juntos", "todo junto"),
    ("bunch of hielo", "abundante hielo"),
    ("casi lleno de cubos de hielo", "casi lleno de cubos de hielo"),
]


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def split_source_text(cocktail):
    raw = []
    instructions = (cocktail.get("instructions") or "").strip()
    if instructions:
        if re.search(r"step\s*\d+", instructions, re.IGNORECASE):
            parts = re.split(r"step\s*\d+\s*", instructions, flags=re.IGNORECASE)
            raw.extend([part.strip() for part in parts if part.strip()])
        else:
            raw.extend([step.get("instruction", "").strip() for step in cocktail.get("steps", []) if step.get("instruction")])
            if not raw:
                raw.append(instructions)
    else:
        raw.extend([step.get("instruction", "").strip() for step in cocktail.get("steps", []) if step.get("instruction")])
    expanded = []
    for item in raw:
        if not item or re.fullmatch(r"step\s*\d+", item, re.IGNORECASE):
            continue
        pieces = re.split(r"(?<=[.!?])\s+|\n+", item)
        expanded.extend([piece.strip() for piece in pieces if piece.strip() and not re.fullmatch(r"step\s*\d+", piece, re.IGNORECASE)])
    return expanded


def translate_sentence(text):
    sentence = " ".join((text or "").strip().split())
    if not sentence:
        return sentence
    for source, target in PHRASES:
        sentence = re.sub(rf"\b{re.escape(source)}\b", target, sentence, flags=re.IGNORECASE)
    for source, target in WORDS.items():
        sentence = re.sub(rf"\b{re.escape(source)}\b", target, sentence, flags=re.IGNORECASE)
    sentence = sentence.replace("the ", "")
    sentence = sentence.replace(" el el ", " el ")
    sentence = sentence.replace(" a coctelera", " una coctelera")
    sentence = sentence.replace(" a copa", " una copa")
    sentence = sentence.replace(" a vaso", " un vaso")
    sentence = sentence.replace(" an ", " un ")
    sentence = sentence.replace(" a ", " ")
    sentence = sentence.replace("  ", " ").strip()
    sentence = sentence.replace("mezcla into", "mezcla en")
    sentence = sentence.replace("agita the", "agita")
    sentence = sentence.replace("vierte the", "vierte")
    sentence = sentence.replace("agrega the", "agrega")
    sentence = sentence.replace("vierte all", "vierte todos")
    sentence = sentence.replace("mix and", "mezcla y")
    sentence = sentence.replace("serve over", "sirve sobre")
    sentence = sentence.replace("revuelve until", "revuelve hasta")
    sentence = sentence.replace("mezcla until", "mezcla hasta")
    sentence = sentence.replace("complete con", "completa con")
    sentence = sentence.replace("splash of", "splash de")
    sentence = sentence.replace("half orange slice", "media rodaja de naranja")
    sentence = sentence.replace("half-filled", "medio lleno")
    sentence = sentence.replace("almost", "casi")
    sentence = sentence.replace("almostt", "casi")
    sentence = sentence.replace("well-frio", "bien frio")
    sentence = sentence.replace("over", "sobre")
    sentence = sentence.replace("until", "hasta")
    sentence = sentence.replace("y sirve con bombilla.", "y sirve con bombilla.")
    sentence = sentence.replace("soda water", "agua con gas")
    sentence = sentence.replace("club soda", "club soda")
    sentence = sentence.replace("sparkling wine", "vino espumante")
    sentence = sentence.replace("old-fashioned", "old fashioned")
    sentence = sentence.replace("purée", "pure")
    sentence = sentence.replace("fine-mesh sieve", "colador fino")
    sentence = sentence.replace("won't", "no")
    sentence = sentence.replace("it won't completely solidify due to the alcohol", "no se solidificara por completo por el alcohol")
    sentence = sentence.replace("almazt", "casi")
    sentence = sentence.replace("alomst", "casi")
    sentence = sentence.replace("glas", "vaso")
    sentence = sentence.replace("Sambucca", "Sambuca")
    sentence = sentence.replace("Grnish", "Decora")
    sentence = sentence.replace("Poor in", "Vierte")
    sentence = sentence.replace("Bacardi", "Bacardi")
    for source, target in CLEANUPS:
        sentence = re.sub(re.escape(source), target, sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\bDo not mezcla\b", "No mezcles", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\bMix\.\b", "Mezcla.", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\bRevuelve\.\b", "Revuelve.", sentence, flags=re.IGNORECASE)
    sentence = sentence[0].upper() + sentence[1:] if sentence else sentence
    return sentence


def normalize_steps(cocktail):
    source_steps = split_source_text(cocktail)
    normalized = []
    for part in source_steps:
        translated = translate_sentence(part)
        translated = translated.strip(" .")
        if not translated:
            continue
        translated = translated[0].upper() + translated[1:]
        if not translated.endswith("."):
            translated += "."
        normalized.append(translated)
    if not normalized and cocktail.get("instructions"):
        normalized = [translate_sentence(cocktail["instructions"]).strip()]
    deduped = []
    seen = set()
    for step in normalized:
        key = step.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(step)
    cocktail["steps"] = [{"step_number": index + 1, "instruction": step} for index, step in enumerate(deduped)]
    cocktail["instructions"] = "\n".join(f"{index + 1}. {step}" for index, step in enumerate(deduped))


def main():
    store = load_store()
    for cocktail in store["cocktails"]:
        normalize_steps(cocktail)
    save_store(store)
    print(f"cocteles actualizados: {len(store['cocktails'])}")


if __name__ == "__main__":
    main()
