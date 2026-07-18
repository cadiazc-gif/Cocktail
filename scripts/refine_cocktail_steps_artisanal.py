import json
import shutil
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"


ARTISANAL_STEPS = {
    "Martini": [
        "Enfriar una copa de coctel.",
        "Agregar Gin y Vermut seco a un vaso mezclador con hielo.",
        "Revolver hasta enfriar, colar y servir.",
        "Decorar con una aceituna.",
    ],
    "Dry Martini": [
        "Enfriar una copa de coctel.",
        "Agregar Gin y Vermut seco a un vaso mezclador con hielo.",
        "Revolver hasta enfriar, colar y servir.",
        "Decorar con una aceituna.",
    ],
    "Dirty Martini": [
        "Enfriar una copa de coctel.",
        "Agregar Vodka, Vermut seco y salmuera de aceituna a un vaso mezclador con hielo.",
        "Revolver hasta enfriar, colar y servir.",
        "Decorar con aceituna y, si deseas, un gajo de limon.",
    ],
    "Negroni": [
        "Agregar Gin, Campari y Vermut dulce a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso old fashioned.",
    ],
    "White Negroni": [
        "Agregar Gin, Suze y Lillet Blanc a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
        "Decorar con piel de limon.",
    ],
    "Negroni Sbagliato": [
        "Llenar un vaso bajo con hielo.",
        "Agregar Campari y Vermut rojo.",
        "Completar con espumante y mezclar suavemente.",
        "Decorar con una rodaja de naranja.",
    ],
    "Boulevardier": [
        "Agregar Whiskey Bourbon, Campari y Vermut rojo a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
        "Decorar con piel de naranja.",
    ],
    "Old Fashioned": [
        "Agregar el azucar, el agua y el Amargo de angostura al vaso.",
        "Mezclar hasta disolver o integrar bien el azucar.",
        "Agregar Whiskey Bourbon y hielo grande.",
        "Revolver suavemente y servir.",
    ],
    "Manhattan": [
        "Enfriar una copa de coctel.",
        "Agregar Whiskey Bourbon, Vermut dulce y Amargo de angostura a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien, colar y servir.",
        "Decorar con cereza marrasquino y, si deseas, piel de naranja.",
    ],
    "Daiquiri": [
        "Agregar Ron claro, lima y azucar flor a una coctelera.",
        "Agregar hielo y agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Margarita": [
        "Escarchar la copa con sal si deseas.",
        "Agregar Tequila, Triple sec y jugo de lima a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en la copa.",
    ],
    "Tommy's Margarita": [
        "Escarchar el vaso con sal si deseas.",
        "Agregar Tequila, jugo de lima y jarabe de agave a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
    ],
    "Whiskey Sour": [
        "Agregar Whisky mezclado, limon y azucar flor a una coctelera.",
        "Agregar hielo y agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso old fashioned.",
        "Decorar con cereza marrasquino y rodaja de limon.",
    ],
    "Boston Sour": [
        "Agregar Whisky mezclado, limon, azucar flor y clara de huevo a una coctelera.",
        "Agitar primero sin hielo para emulsionar.",
        "Agregar hielo y volver a agitar hasta enfriar bien.",
        "Colar y servir en copa sour.",
        "Decorar con rodaja de limon y cereza marrasquino.",
    ],
    "Pisco Sour": [
        "Agregar Pisco, jugo de limon, azucar y clara de huevo a una coctelera.",
        "Agitar primero sin hielo para integrar la clara.",
        "Agregar hielo y agitar nuevamente hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Amaretto Sour": [
        "Agregar Amaretto, jugo de limon, jarabe simple y clara de huevo a una coctelera.",
        "Agitar primero sin hielo para emulsionar.",
        "Agregar hielo y volver a agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
        "Terminar con unas gotas de Amargo de angostura si deseas.",
    ],
    "Mai Tai": [
        "Agregar Ron claro, jarabe de horchata, Triple sec y mezcla agridulce a una coctelera.",
        "Agregar hielo y agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso collins.",
        "Decorar con cereza marrasquino.",
    ],
    "Mojito": [
        "Agregar Menta, azucar y lima al vaso.",
        "Macerar suavemente para extraer aroma sin romper demasiado la menta.",
        "Agregar Ron claro y hielo.",
        "Completar con agua con gas, mezclar suavemente y servir.",
    ],
    "Aperol Spritz": [
        "Llenar una copa de vino con hielo.",
        "Agregar Aperol y luego Prosecco.",
        "Completar con agua con gas y mezclar suavemente.",
        "Decorar con una rodaja de naranja.",
    ],
    "French 75": [
        "Agregar Gin, azucar y jugo de limon a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar en un vaso collins o copa flauta.",
        "Completar con Champagne.",
        "Decorar con naranja y cereza si deseas.",
    ],
    "Corpse Reviver #2": [
        "Enfriar una copa coupe.",
        "Agregar Gin, Lillet Blanc, Cointreau, jugo de limon y Absenta a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir.",
    ],
    "Paper Plane": [
        "Agregar Whiskey Bourbon, Aperol, Amaro Nonino y jugo de limon a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa coupe.",
    ],
    "Naked and Famous": [
        "Agregar Mezcal, Aperol, Chartreuse amarillo y jugo de lima a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa coupe.",
    ],
    "Division Bell": [
        "Agregar Mezcal, Aperol, licor de maraschino y jugo de lima a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa coupe.",
    ],
    "Final Ward": [
        "Agregar Whiskey de centeno, Chartreuse verde, licor de maraschino y jugo de limon a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa coupe.",
    ],
    "Gold Rush": [
        "Agregar Whiskey Bourbon, jugo de limon y jarabe de miel a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
    ],
    "Gin Basil Smash": [
        "Agregar Albahaca, jarabe simple y jugo de limon a una coctelera.",
        "Macerar suavemente para extraer aroma.",
        "Agregar Gin y hielo, luego agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
        "Decorar con albahaca.",
    ],
    "Jungle Bird": [
        "Agregar Ron oscuro, Campari, jugo de piña, jugo de lima y jarabe simple a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar sobre hielo fresco en un vaso bajo.",
    ],
    "Caipirinha": [
        "Cortar la lima en trozos y agregarla al vaso con el azucar.",
        "Macerar para extraer el jugo de la fruta.",
        "Agregar Cachaca y bastante hielo.",
        "Mezclar y servir.",
    ],
    "Caipiroska": [
        "Cortar la lima en trozos y agregarla al vaso con el azucar.",
        "Macerar para extraer el jugo de la fruta.",
        "Agregar Vodka y bastante hielo.",
        "Mezclar y servir.",
    ],
    "Moscow Mule": [
        "Llenar un vaso highball con hielo.",
        "Agregar Vodka y jugo de lima.",
        "Completar con Ginger Ale y mezclar suavemente.",
    ],
    "Dark and Stormy": [
        "Llenar un vaso highball con hielo.",
        "Agregar Ron oscuro.",
        "Completar con cerveza de jengibre y mezclar suavemente.",
    ],
    "Espresso Martini": [
        "Enfriar una copa de coctel.",
        "Agregar Vodka, Kahlua y jarabe a una coctelera con hielo.",
        "Agitar con fuerza hasta enfriar y generar espuma.",
        "Colar y servir.",
    ],
    "Tom Collins": [
        "Agregar Gin, jugo de limon y azucar a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar en un vaso collins con hielo fresco.",
        "Completar con club soda.",
        "Decorar con naranja y cereza marrasquino.",
    ],
    "Gin Fizz": [
        "Agregar Gin, limon y azucar flor a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar en un vaso highball.",
        "Completar con agua con gas.",
    ],
    "Clover Club": [
        "Agregar Gin, granadina, limon y clara de huevo a una coctelera.",
        "Agitar primero sin hielo para emulsionar.",
        "Agregar hielo y volver a agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Sidecar": [
        "Agregar Cognac, Cointreau y jugo de limon a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Between the Sheets": [
        "Agregar Cognac, Ron claro, Cointreau y jugo de limon a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa coupe.",
    ],
    "Paloma": [
        "Llenar un vaso collins con hielo.",
        "Agregar Tequila.",
        "Completar con bebida de uva y mezclar suavemente.",
    ],
    "Batanga": [
        "Escarchar el vaso con una pizca de sal si deseas.",
        "Llenar un vaso highball con hielo.",
        "Agregar Tequila y jugo de lima.",
        "Completar con cola y mezclar suavemente.",
    ],
    "Garibaldi": [
        "Llenar un vaso highball con hielo.",
        "Agregar Campari.",
        "Completar con jugo de naranja y mezclar suavemente.",
    ],
    "Hugo Spritz": [
        "Llenar una copa de vino con hielo.",
        "Agregar licor de flor de saúco y Prosecco.",
        "Completar con agua con gas y mezclar suavemente.",
        "Decorar con menta y una rodaja de lima.",
    ],
    "Rossini": [
        "Enfriar una copa flauta.",
        "Agregar nectar de frutilla.",
        "Completar con Prosecco y mezclar suavemente.",
    ],
    "Pichuncho": [
        "Enfriar una copa de coctel.",
        "Agregar Pisco, Vermut rojo y Araucano a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien, colar y servir.",
    ],
    "Piscola": [
        "Llenar un vaso highball con hielo.",
        "Agregar Pisco.",
        "Completar con Coca-Cola y mezclar suavemente.",
        "Decorar con limon o lima si deseas.",
    ],
    "Terremoto": [
        "Servir el vino blanco en un vaso alto o jarro.",
        "Agregar helado de piña y granadina.",
        "Completar con Champagne.",
        "Terminar con Fernet si deseas y servir bien frio.",
    ],
    "Vaina": [
        "Agregar vino dulce, huevo, cafe y azucar flor a una licuadora.",
        "Agregar hielo y licuar hasta obtener una mezcla cremosa.",
        "Servir en una copa de coctel.",
        "Terminar con unas gotas de Cognac o Brandy y una pizca de canela si deseas.",
    ],
    "Chilcano": [
        "Llenar un vaso highball con hielo.",
        "Agregar Pisco y jugo de lima.",
        "Completar con Ginger Ale y mezclar suavemente.",
        "Terminar con Amargo de angostura si deseas.",
    ],
    "Americano": [
        "Llenar un vaso collins con hielo.",
        "Agregar Campari y Vermut dulce.",
        "Mezclar suavemente para enfriar.",
        "Decorar con piel de limon o naranja.",
    ],
    "Aviation": [
        "Agregar Gin, jugo de limon y licor de maraschino a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Cosmopolitan": [
        "Agregar Vodka, Cointreau, jugo de lima y jugo de arandano a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "French Martini": [
        "Agregar Vodka, licor de frambuesa y jugo de piña a una coctelera con hielo.",
        "Agitar hasta enfriar bien.",
        "Colar y servir en una copa de coctel.",
    ],
    "Brooklyn": [
        "Enfriar una copa de coctel.",
        "Agregar Whiskey de centeno, Vermut seco, licor de maraschino y Amargo de angostura a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien, colar y servir.",
        "Decorar con cereza marrasquino.",
    ],
    "Bijou": [
        "Enfriar una copa de coctel.",
        "Agregar Gin, Chartreuse verde, Vermut dulce y Amargo de naranja a un vaso mezclador con hielo.",
        "Revolver hasta enfriar bien, colar y servir.",
    ],
}


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-step-artisanal-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(STORE_PATH, backup_path)
    return backup_path


def apply_artisanal_steps():
    store = load_store()
    backup = backup_store()
    updated = 0
    touched = []

    for cocktail in store.get("cocktails", []):
        lines = ARTISANAL_STEPS.get(cocktail.get("name"))
        if not lines:
            continue
        new_steps = [{"step_number": index, "instruction": line} for index, line in enumerate(lines, start=1)]
        new_text = "\n".join(lines)
        old_text = "\n".join(step.get("instruction", "") for step in cocktail.get("steps", []))
        if new_text != old_text:
            cocktail["steps"] = new_steps
            cocktail["instructions"] = new_text
            updated += 1
            touched.append(cocktail["name"])

    save_store(store)
    print(json.dumps({
        "backup": str(backup),
        "updated": updated,
        "touched": touched,
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    apply_artisanal_steps()
