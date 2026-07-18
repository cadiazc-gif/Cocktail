import json
import shutil
import time
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
STORE_PATH = BASE_DIR / "data" / "store.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"

NEW_COCKTAILS = [
    {
        "name": "Pichuncho",
        "description": "Clasico chileno de pisco, vermut rosso y Araucano, muy presente en barras de raiz local.",
        "image_url": "https://freight.cargo.site/t/original/i/aad02bbd7a607a7233eccbef8424268c406a7419d1e1c6ab3fa75d26d4a2dd05/PICHUCHO.png",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Copa de coctel",
        "tags": ["chileno", "pisco", "clasico", "bar-top-chile"],
        "steps": ["Agrega pisco, vermut rosso y Araucano a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela en una copa fria.", "Sirve sin garnish o con piel de naranja si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Vermut rojo", "category": "Licores y aperitivos"}, {"name": "Vermut dulce", "category": "Licores y aperitivos"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Araucano", "category": "Bitters"}]},
        ],
        "source": {"provider": "Bar La Providencia", "source_url": "https://barlaprovidencia.cl/COCTELES-CLASICOS-CHILENOS", "ingredients_text": ["Pisco Black Heron", "Vermut Cinzano Rosso", "Araucano"]},
    },
    {
        "name": "Pistón",
        "description": "Highball chileno simple y seco de pisco con tónica.",
        "image_url": "https://freight.cargo.site/t/original/i/304059428e0c8a948db2474ae0fa172881e7a52fd9a1342a4e98acb0e2ec2541/PISTON.png",
        "prep_time_minutes": 2,
        "alcohol_level": "Suave",
        "glassware": "Vaso highball",
        "tags": ["chileno", "pisco", "highball", "bar-top-chile"],
        "steps": ["Llena un vaso alto con hielo.", "Agrega el pisco.", "Completa con agua tonica.", "Mezcla suavemente y sirve."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Agua tonica", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Bar La Providencia", "source_url": "https://barlaprovidencia.cl/COCTELES-CLASICOS-CHILENOS", "ingredients_text": ["Pisco Norterra Transparente", "Tonica"]},
    },
    {
        "name": "Pisco Negroni",
        "description": "Relectura chilena del Negroni donde el pisco toma el lugar del gin.",
        "image_url": "https://freight.cargo.site/t/original/i/b79661538b47490f703ceb32326fdd259f30015d2abb3579e3a33608b1bc62b3/NEGRONI.png",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Vaso bajo",
        "tags": ["chileno", "pisco", "negroni", "bar-top-chile"],
        "steps": ["Agrega pisco, vermut rosso y Campari a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo.", "Decora con piel de naranja si deseas."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Vermut rojo", "category": "Licores y aperitivos"}, {"name": "Vermut dulce", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
        ],
        "source": {"provider": "Bar La Providencia", "source_url": "https://barlaprovidencia.cl/COCTELES-CLASICOS-CHILENOS", "ingredients_text": ["Pisco Endemico Pedro Jimenez", "Cinzano Rosso", "Campari"]},
    },
    {
        "name": "Pisco Martini",
        "description": "Version chilena del Martini, seca y salina, con pisco y vermut dry.",
        "image_url": "https://freight.cargo.site/t/original/i/d74746abc880ebe7854aa81543d9e4eaf4daf70f81469d5076de8b3a5c535f61/MARTINI.png",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Copa martini",
        "tags": ["chileno", "pisco", "martini", "bar-top-chile"],
        "steps": ["Agrega pisco, vermut dry y unas gotas de salmuera a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela en una copa martini bien fria.", "Decora con aceituna si deseas."],
        "requirements": [
            {"amount": "2 1/2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Martini Dry", "category": "Licores y aperitivos"}, {"name": "Vermut seco", "category": "Licores y aperitivos"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Salmuera de aceituna", "category": "Condimentos"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Aceituna", "category": "Garnish"}]},
        ],
        "source": {"provider": "Bar La Providencia", "source_url": "https://barlaprovidencia.cl/COCTELES-CLASICOS-CHILENOS", "ingredients_text": ["Pisco Hanac Pacha", "Vermut Martini Dry", "Salmuera"]},
    },
    {
        "name": "Pisco in the Air",
        "description": "Signature de Chipe Libre que mezcla pisco con albahaca, frambuesa y papaya.",
        "image_url": "https://static.wixstatic.com/media/36de2c_525ed647821749c4b1ec41f264a8c0b5~mv2.jpg/v1/fill/w_2500,h_1399,al_c/36de2c_525ed647821749c4b1ec41f264a8c0b5~mv2.jpg",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["chileno", "pisco", "autor", "bar-top-chile"],
        "steps": ["Agrega pisco, jugo de lima, papaya, frambuesa y albahaca a una coctelera con hielo.", "Agita con fuerza hasta integrar y enfriar.", "Haz doble colado en una copa fria.", "Decora con albahaca o fruta fresca si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Papaya", "category": "Frutas"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Frambuesa", "category": "Frutas"}]},
            {"amount": "4", "unit": "hojas", "optional": False, "options": [{"name": "Albahaca", "category": "Hierbas"}]},
            {"amount": "1/2", "unit": "oz", "optional": True, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
        ],
        "source": {"provider": "Chipe Libre / Elite Traveler", "source_url": "https://elitetraveler.com/travel/experiences-travel/a-luxury-weekend-guide-to-santiago-chile", "ingredients_text": ["Pisco", "Jugo de lima", "Frambuesa", "Papaya", "Albahaca"]},
    },
    {
        "name": "Zafiro",
        "description": "Coctel citrico, refrescante y tipo ponche de Siam Thai.",
        "image_url": "https://static.wixstatic.com/media/6940f2_cd1bccb2c71e416a8c70aa922c217ff3~mv2.png/v1/fill/w_90,h_134,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_cd1bccb2c71e416a8c70aa922c217ff3~mv2.png",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso alto",
        "tags": ["chileno-autor", "siam-thai", "gin", "bar-top-chile"],
        "steps": ["Agrega gin, St. Germain, pomelo y lemongrass a una coctelera con hielo.", "Agita con fuerza hasta enfriar.", "Cuela en vaso con hielo.", "Perfuma con limon y sirve."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "St. Germain", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Jugo de pomelo", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "rama", "optional": True, "options": [{"name": "Lemongrass", "category": "Hierbas"}]},
            {"amount": "1", "unit": "twist", "optional": True, "options": [{"name": "Limon", "category": "Frutas"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Gin Bombay Sapphire", "ST Germain", "Pomelo", "Lemongrass", "Perfume con limon"]},
    },
    {
        "name": "Diamante",
        "description": "Coctel seco y frutal de Siam Thai con gin, jerez fino, soju de ciruela y yuzu.",
        "image_url": "https://static.wixstatic.com/media/6940f2_775ede83deed48579c555436a6270825~mv2.png/v1/fill/w_46,h_67,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_775ede83deed48579c555436a6270825~mv2.png",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["chileno-autor", "siam-thai", "jerez", "bar-top-chile"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza.", "Cuela en copa fria.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Fino", "category": "Vinos y espumantes"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Soju de ciruela", "category": "Licores y aperitivos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Yuzu", "category": "Frutas"}]},
            {"amount": "1/2", "unit": "oz", "optional": True, "options": [{"name": "Vermut con coco tostado", "category": "Licores y aperitivos"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Gin Bombay Sapphire", "Jerez Palomino Fino", "Soju de ciruela", "Yuzu", "Vermut con coco tostado"]},
    },
    {
        "name": "Esmeralda",
        "description": "Coctel frutal, aperitivo y ligero de Siam Thai con ron blanco y notas salinas.",
        "image_url": "https://static.wixstatic.com/media/6940f2_3ec25ca3cd6e405c8bff5482b7b2557c~mv2.png/v1/fill/w_46,h_68,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_3ec25ca3cd6e405c8bff5482b7b2557c~mv2.png",
        "prep_time_minutes": 5,
        "alcohol_level": "Suave",
        "glassware": "Vaso alto",
        "tags": ["chileno-autor", "siam-thai", "aperitivo", "bar-top-chile"],
        "steps": ["Agrega ron, licor de melon y durazno y salmuera a una coctelera con hielo.", "Agita hasta enfriar.", "Cuela en vaso con hielo.", "Completa con soda y termina con albahaca y garnish."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Ron blanco", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Licor de melon y durazno", "category": "Licores y aperitivos"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Salmuera de alcaparron", "category": "Condimentos"}]},
            {"amount": "top", "unit": "", "optional": False, "options": [{"name": "Soda", "category": "Bebidas y mixers"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Gomita de frutas", "category": "Garnish"}]},
            {"amount": "2", "unit": "hojas", "optional": True, "options": [{"name": "Albahaca", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Ron Flor de Caña Blanco", "Licor de melon y durazno", "Salmuera de alcaparron", "Soda", "Gomita de frutas con albahaca"]},
    },
    {
        "name": "Thai Aperol",
        "description": "Interpretacion especiada y citrica del Aperol hecha en Siam Thai.",
        "image_url": "https://static.wixstatic.com/media/6940f2_8134a00d42454a259936618dc4290c4e~mv2.jpg/v1/fill/w_147,h_221,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_8134a00d42454a259936618dc4290c4e~mv2.jpg",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso alto",
        "tags": ["chileno-autor", "siam-thai", "aperol", "bar-top-chile"],
        "steps": ["Agrega Aperol, gin, jugo de limon, naranja, jengibre y syrup especiado a una coctelera con hielo.", "Agita hasta enfriar bien.", "Cuela en vaso con hielo.", "Termina con angostura y romero."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Aperol", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de naranja", "category": "Jugos y nectares"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Jengibre", "category": "Condimentos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Syrup especiado", "category": "Endulzantes"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1", "unit": "rama", "optional": True, "options": [{"name": "Romero", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Aperol", "Gin", "Jugo de limon", "Naranja", "Jengibre", "Syrup especiado", "Amargo angostura", "Romero"]},
    },
    {
        "name": "London Mule",
        "description": "Mule de gin y ginger beer local de la carta de Siam Thai.",
        "image_url": "https://static.wixstatic.com/media/6940f2_45cff08b2f184ef2a8b7adf216a747d4~mv2.png/v1/fill/w_66,h_92,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_45cff08b2f184ef2a8b7adf216a747d4~mv2.png",
        "prep_time_minutes": 4,
        "alcohol_level": "Suave",
        "glassware": "Vaso alto",
        "tags": ["chileno-autor", "siam-thai", "mule", "bar-top-chile"],
        "steps": ["Agrega gin, jugo de limon, jengibre y syrup de la casa a un vaso con hielo.", "Completa con ginger beer.", "Mezcla suavemente y sirve."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Jengibre", "category": "Condimentos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Syrup especiado", "category": "Endulzantes"}]},
            {"amount": "top", "unit": "", "optional": False, "options": [{"name": "Ginger beer local", "category": "Bebidas y mixers"}, {"name": "Cerveza de jengibre", "category": "Bebidas y mixers"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Gin Bombay Sapphire", "Jugo de limon", "Jengibre", "Syrup de la casa", "Ginger beer local"]},
    },
    {
        "name": "Mojito Mekong",
        "description": "Mojito especiado y citrico con ron dorado, jengibre y garnish picante.",
        "image_url": "https://static.wixstatic.com/media/6940f2_55426dc669444b96a7db39b72933c440~mv2.png/v1/fill/w_90,h_109,al_c,q_85,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_55426dc669444b96a7db39b72933c440~mv2.png",
        "prep_time_minutes": 6,
        "alcohol_level": "Medio",
        "glassware": "Vaso alto",
        "tags": ["chileno-autor", "siam-thai", "mojito", "bar-top-chile"],
        "steps": ["Agrega ron, jugo de limon, naranja, jengibre y syrup especiado a un vaso o coctelera.", "Incorpora menta y hielo.", "Completa con soda.", "Termina con angostura, aji, menta y deshidratado."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Ron dorado", "category": "Destilados"}, {"name": "Ron oscuro", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de naranja", "category": "Jugos y nectares"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Jengibre", "category": "Condimentos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Syrup especiado", "category": "Endulzantes"}]},
            {"amount": "6", "unit": "hojas", "optional": False, "options": [{"name": "Menta", "category": "Hierbas"}]},
            {"amount": "top", "unit": "", "optional": False, "options": [{"name": "Soda", "category": "Bebidas y mixers"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Aji", "category": "Condimentos"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Deshidratado de naranja", "category": "Garnish"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Ron dorado", "Jugo de limon", "Naranja", "Jengibre", "Syrup especiado", "Menta", "Soda", "Angostura", "Aji"]},
    },
    {
        "name": "The Artesian Siam Sour",
        "description": "Sour de pisco especiado con maracuya, jengibre y toques aromaticos.",
        "image_url": "https://static.wixstatic.com/media/6940f2_f38cde7d9297402e9c446424c8942890~mv2.jpg/v1/fill/w_147,h_147,al_c,q_80,usm_0.66_1.00_0.01,blur_2,enc_auto/6940f2_f38cde7d9297402e9c446424c8942890~mv2.jpg",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["chileno-autor", "siam-thai", "pisco", "bar-top-chile"],
        "steps": ["Agrega pisco, syrup especiado, maracuya, jugo de limon y jengibre a una coctelera con hielo.", "Agita con fuerza hasta enfriar.", "Cuela en copa fria.", "Termina con angostura, pimienta rosa y romero."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}, {"name": "Pisco El Gobernador", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Syrup especiado", "category": "Endulzantes"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de maracuya", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Jengibre", "category": "Condimentos"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Pimienta rosa", "category": "Condimentos"}]},
            {"amount": "1", "unit": "rama", "optional": True, "options": [{"name": "Romero", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Siam Thai", "source_url": "https://www.siamthai.cl/menu", "ingredients_text": ["Pisco El Gobernador", "Syrup especiado", "Maracuya", "Jugo de limon", "Jengibre", "Angostura", "Pimienta rosa", "Romero"]},
    },
]


def normalized(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-curated-round4-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(STORE_PATH, backup_path)
    return backup_path


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def ingredient_index(store):
    return {normalized(item["name"]): item for item in store["ingredients"]}


def ensure_unit_catalog(store, unit):
    clean = (unit or "").strip()
    if not clean:
        return
    catalog = store.setdefault("settings", {}).setdefault("units_catalog", [])
    if clean not in catalog:
        catalog.append(clean)
        store["settings"]["units_catalog"] = sorted(dict.fromkeys(catalog), key=str.lower)


def ensure_ingredient(store, name, category):
    index = ingredient_index(store)
    key = normalized(name)
    if key in index:
        ingredient = index[key]
        if not ingredient.get("category") or ingredient.get("category") == "Otros":
            ingredient["category"] = category
        return ingredient["id"]
    ingredient_id = next_id(store["ingredients"])
    store["ingredients"].append(
        {
            "id": ingredient_id,
            "name": name,
            "category": category,
            "alcoholic": category in {"Destilados", "Licores y aperitivos", "Bitters", "Vinos y espumantes", "Cervezas y fermentados"},
            "tags": [],
            "image_url": "",
            "replacement_ingredient_ids": [],
        }
    )
    return ingredient_id


def cocktail_exists(store, name):
    existing = {normalized(item["name"]) for item in store["cocktails"]}
    return normalized(name) in existing


def build_requirements(store, cocktail_name, requirements):
    rows = []
    for index, requirement in enumerate(requirements, start=1):
        ensure_unit_catalog(store, requirement["unit"])
        option_ids = [ensure_ingredient(store, option["name"], option["category"]) for option in requirement["options"]]
        rows.append(
            {
                "group_key": f"{normalized(cocktail_name).replace(' ', '-')}-{index}",
                "amount": requirement["amount"],
                "unit": requirement["unit"],
                "optional": bool(requirement.get("optional")),
                "options": option_ids,
            }
        )
    return rows


def import_curated_cocktails():
    store = load_store()
    backup_path = backup_store()
    created = []
    skipped = []
    for cocktail in NEW_COCKTAILS:
        if cocktail_exists(store, cocktail["name"]):
            skipped.append(cocktail["name"])
            continue
        cocktail_id = next_id(store["cocktails"])
        requirements = build_requirements(store, cocktail["name"], cocktail["requirements"])
        steps = [{"step_number": index, "instruction": instruction} for index, instruction in enumerate(cocktail["steps"], start=1)]
        store["cocktails"].append(
            {
                "id": cocktail_id,
                "name": cocktail["name"],
                "description": cocktail["description"],
                "image_url": cocktail["image_url"],
                "prep_time_minutes": cocktail["prep_time_minutes"],
                "instructions": "\n".join(f"{index}. {instruction}" for index, instruction in enumerate(cocktail["steps"], start=1)),
                "rating": 0,
                "is_favorite": False,
                "is_active": True,
                "tags": cocktail["tags"],
                "steps": steps,
                "requirements": requirements,
                "source": cocktail["source"],
                "glassware": cocktail["glassware"],
                "alcohol_level": cocktail["alcohol_level"],
            }
        )
        created.append(cocktail["name"])
    save_store(store)
    print(json.dumps({"backup": str(backup_path), "created": created, "skipped": skipped, "total_cocktails": len(store["cocktails"])}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    import_curated_cocktails()
