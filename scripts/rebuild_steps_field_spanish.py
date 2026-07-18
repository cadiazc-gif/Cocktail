import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


PHRASES = [
    ("rub the rim of the glass with the lime slice to make the salt stick to it", "Humedece el borde del vaso con una rodaja de lima para que la sal se adhiera"),
    ("rub the rim of the vaso with the lime slice to make the salt stick to it", "Humedece el borde del vaso con una rodaja de lima para que la sal se adhiera"),
    ("take care to moisten only the outer rim and sprinkle the salt on it", "Humedece solo el borde exterior y espolvorea la sal sobre el borde"),
    ("the salt should present to the lips of the imbiber and never mix into the cocktail", "Deja la sal solo en el borde para que no se mezcle con el coctel"),
    ("muddle mint leaves with sugar and lime juice", "Macera las hojas de menta con azucar y jugo de lima"),
    ("add a splash of soda water and fill the glass with cracked ice", "Agrega un splash de soda y llena el vaso con hielo picado"),
    ("pour the rum and top with soda water", "Vierte el ron y completa con soda"),
    ("garnish and serve with straw", "Decora y sirve con bombilla"),
    ("mix with crushed ice in blender until smooth", "Licua con hielo triturado hasta que quede suave"),
    ("pour into chilled glass, garnish and serve", "Vierte en un vaso frio, decora y sirve"),
    ("pour all ingredients into a cocktail shaker, mix and serve over ice into a chilled glass", "Vierte todos los ingredientes en una coctelera, mezcla y sirve sobre hielo en un vaso frio"),
    ("pour vodka and gin over ice, add tonic and stir", "Vierte el vodka y el gin sobre hielo, agrega agua tonica y revuelve"),
    ("in a shaker half-filled with ice cubes, combine all of the ingredients", "En una coctelera medio llena de cubos de hielo, mezcla todos los ingredientes"),
    ("shake well", "Agita bien"),
    ("strain into a cocktail glass", "Cuela en una copa de coctel"),
    ("shake ingredients with ice, strain into a cocktail glass, and serve", "Agita los ingredientes con hielo, cuela en una copa de coctel y sirve"),
    ("pour schnapps, orange juice, and cranberry juice over ice in a highball glass", "Vierte el schnapps, el jugo de naranja y el jugo de arandano sobre hielo en un vaso highball"),
    ("top with club soda and serve", "Completa con club soda y sirve"),
    ("fill a tall glass with ice", "Llena un vaso alto con hielo"),
    ("layer ingredients into a shot glass", "Sirve los ingredientes en capas en un vaso de shot"),
    ("serve with a stirrer", "Sirve con removedor"),
    ("stir gently", "Revuelve suavemente"),
    ("fill glass with crushed ice", "Llena el vaso con hielo triturado"),
    ("build gin, lemon juice and simple syrup over", "Vierte el gin, el jugo de limon y el jarabe simple"),
    ("pour the campari and vermouth over ice into glass, add a splash of soda water and garnish with half orange slice", "Vierte el Campari y el vermut sobre hielo en un vaso, agrega un splash de soda y decora con media rodaja de naranja"),
    ("stir all ingredients with ice, strain into a cocktail glass, and serve", "Revuelve todos los ingredientes con hielo, cuela en una copa de coctel y sirve"),
    ("shake all ingredients with ice and strain contents into a cocktail glass", "Agita todos los ingredientes con hielo y cuela en una copa de coctel"),
    ("shake all ingredients with ice, then strain into a cold glass", "Agita todos los ingredientes con hielo y luego cuela en un vaso frio"),
    ("pour into a highball glass almost filled with ice cubes", "Vierte en un vaso highball casi lleno de cubos de hielo"),
    ("add all ingredients into shaker filled with ice", "Agrega todos los ingredientes a una coctelera llena de hielo"),
    ("garnish with a cherry", "Decora con una cereza"),
    ("stir in mixing glass with ice and strain", "Revuelve en un vaso mezclador con hielo y cuela"),
    ("blend again until slushy", "Licua nuevamente hasta obtener una textura granizada"),
    ("divide among glasses", "Reparte entre los vasos"),
]


WORD_REPLACEMENTS = [
    (" over ", " sobre "),
    (" into ", " en "),
    (" with ", " con "),
    (" and ", " y "),
    (" then ", " luego "),
    (" until ", " hasta "),
    (" all ingredients", " todos los ingredientes"),
    (" ingredients", " ingredientes"),
    (" ingredient", " ingrediente"),
    (" shaker", " coctelera"),
    (" glass", " vaso"),
    (" cocktail", " coctel"),
    (" strain", " cuela"),
    (" shake", " agita"),
    (" stir", " revuelve"),
    (" pour", " vierte"),
    (" add", " agrega"),
    (" serve", " sirve"),
    (" garnish", " decora"),
    (" mix", " mezcla"),
    (" muddle", " macera"),
    (" combine", " mezcla"),
    (" fill", " llena"),
    (" top ", " completa "),
    (" club soda", " club soda"),
    (" soda water", " soda"),
    (" tonic", " agua tonica"),
    (" mint leaves", " hojas de menta"),
    (" lime juice", " jugo de lima"),
    (" lemon juice", " jugo de limon"),
    (" orange juice", " jugo de naranja"),
    (" cranberry juice", " jugo de arandano"),
    (" pineapple juice", " jugo de pinia"),
    (" simple syrup", " jarabe simple"),
    (" sugar", " azucar"),
    (" ice cubes", " cubos de hielo"),
    (" cracked ice", " hielo picado"),
    (" crushed ice", " hielo triturado"),
    (" ice", " hielo"),
    (" cherry", " cereza"),
    (" orange slice", " rodaja de naranja"),
    (" lime slice", " rodaja de lima"),
    (" lemon slice", " rodaja de limon"),
    (" chilled", " frio"),
    (" cold", " frio"),
    (" flute", " copa flauta"),
    (" sparkling wine", " vino espumante"),
    (" old-fashioned", " old fashioned"),
    (" old fashioned", " old fashioned"),
]


SPECIAL_CLEANUPS = [
    ("el rodaja", "la rodaja"),
    ("el otros ingredientes", "los otros ingredientes"),
    ("el ingredientes", "los ingredientes"),
    ("el hojas", "las hojas"),
    ("el cereza", "la cereza"),
    ("el rodaja de naranja", "la rodaja de naranja"),
    ("el rodaja de lima", "la rodaja de lima"),
    ("splash de soda", "un splash de soda"),
    ("sobre hielo en un vaso", "sobre hielo en un vaso"),
    ("copa de coctel y.", "copa de coctel."),
]


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def source_lines(cocktail):
    lines = [step.get("instruction", "").strip() for step in cocktail.get("steps", []) if step.get("instruction")]
    if not lines and cocktail.get("instructions"):
        lines = [line.strip() for line in str(cocktail["instructions"]).splitlines() if line.strip()]
    cleaned = []
    for line in lines:
        line = re.sub(r"^\s*\d+\.\s*", "", line)
        line = re.sub(r"^\s*step\s*\d+\s*:?\s*", "", line, flags=re.IGNORECASE)
        if line:
            cleaned.append(line)
    return cleaned


def split_line(line):
    pieces = re.split(r"(?<=[.!?])\s+|\n+", line)
    result = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        result.append(piece)
    return result or [line]


def translate_piece(text):
    piece = " ".join(text.strip().split())
    lower = piece.lower()
    for source, target in PHRASES:
        if lower == source:
            return target
    wrapped = f" {piece} "
    for source, target in WORD_REPLACEMENTS:
        wrapped = re.sub(re.escape(source), f" {target} ", wrapped, flags=re.IGNORECASE)
    piece = " ".join(wrapped.split())
    for source, target in SPECIAL_CLEANUPS:
        piece = re.sub(re.escape(source), target, piece, flags=re.IGNORECASE)
    piece = piece.replace("Procura moisten only el outer rim y sprinkle el salt sobre it", "Humedece solo el borde exterior y espolvorea la sal sobre el borde")
    piece = piece.replace("El salt should present to el lips of el imbiber y never mezcla en el coctel", "Deja la sal solo en el borde para que no se mezcle con el coctel")
    piece = piece.replace("Agrega splash de soda y llena el vaso con hielo picado", "Agrega un splash de soda y llena el vaso con hielo picado")
    piece = piece.replace("Vierte el ron y completa con soda", "Vierte el ron y completa con soda")
    piece = piece.replace("Decora y sirve con bombilla", "Decora y sirve con bombilla")
    piece = piece.replace("la rodaja de lima", "la rodaja de lima")
    piece = piece.replace("el gin", "el gin")
    piece = piece.replace("gin", "gin")
    piece = piece.strip(" .")
    if piece:
        piece = piece[0].upper() + piece[1:]
    return piece


def rebuild_steps(cocktail):
    translated = []
    for line in source_lines(cocktail):
        for piece in split_line(line):
            step = translate_piece(piece)
            if not step:
                continue
            if not step.endswith("."):
                step += "."
            translated.append(step)
    deduped = []
    seen = set()
    for step in translated:
        key = step.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(step)
    cocktail["steps"] = [{"step_number": index + 1, "instruction": step} for index, step in enumerate(deduped)]


def main():
    store = load_store()
    for cocktail in store["cocktails"]:
        rebuild_steps(cocktail)
    save_store(store)
    print(f"steps actualizados: {len(store['cocktails'])}")


if __name__ == "__main__":
    main()
