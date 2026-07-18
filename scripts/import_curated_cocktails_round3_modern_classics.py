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
        "name": "Naked and Famous",
        "description": "Moderno clasico de mezcal, Aperol, Yellow Chartreuse y lima, creado por Joaquin Simo.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Naked+and+Famous&mood=bold&abv=26&method=Shake&glass=Coupe&spirit=mezcal&desc=An+equal-parts+mezcal+cocktail+balancing+smoke+with+yellow+Chartreuse+and+Aperol&tags=smoky+and+herbaceous",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["moderno", "mezcal", "amargo", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve sin garnish."],
        "requirements": [
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Mezcal", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Aperol", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Yellow Chartreuse", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/naked-and-famous", "ingredients_text": ["Mezcal", "Aperol", "Yellow Chartreuse", "Jugo de lima"]},
    },
    {
        "name": "Tommy's Margarita",
        "description": "Version moderna de la Margarita creada en Tommy's, centrada en tequila y agave.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Tommys+Margarita&mood=crisp&abv=20&method=Shake&glass=Rocks+Glass&spirit=tequila&desc=A+pure+agave-focused+Margarita+using+agave+nectar+instead+of+orange+liqueur&tags=clean+and+agave-forward",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "tequila", "agave", "top-bars"],
        "steps": ["Agrega tequila, jugo de lima y jarabe de agave a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo.", "Escarcha con sal si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Tequila", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jarabe de agave", "category": "Endulzantes"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Sal", "category": "Condimentos"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/tommys-margarita", "ingredients_text": ["Tequila", "Jugo de lima", "Jarabe de agave"]},
    },
    {
        "name": "Gold Rush",
        "description": "Sour moderno de bourbon y miel popularizado por Milk & Honey.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Gold+Rush&mood=bold&abv=20&method=Shake&glass=Rocks+Glass&spirit=bourbon&desc=A+silky+bourbon+sour+sweetened+with+honey+syrup+instead+of+sugar&tags=smooth+and+honeyed",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "bourbon", "sour", "top-bars"],
        "steps": ["Agrega bourbon, jugo de limon y jarabe de miel a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Whiskey Bourbon", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jarabe de miel", "category": "Endulzantes"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/gold-rush", "ingredients_text": ["Whiskey bourbon", "Jugo de limon", "Jarabe de miel"]},
    },
    {
        "name": "Oaxaca Old Fashioned",
        "description": "Old Fashioned de agave con tequila y mezcal, creado por Phil Ward.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Oaxaca+Old+Fashioned&mood=bold&abv=30&method=Stir&glass=Rocks+Glass&spirit=mezcal&desc=A+smoky+twist+on+the+classic+Old+Fashioned+featuring+mezcal+and+tequila&tags=smoky+and+agave-forward",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "mezcal", "old-fashioned", "top-bars"],
        "steps": ["Agrega tequila, mezcal, jarabe de agave y bitters a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela sobre un gran cubo de hielo en vaso bajo.", "Decora con piel de naranja si deseas."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Tequila", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Mezcal", "category": "Destilados"}]},
            {"amount": "1", "unit": "cdita", "optional": False, "options": [{"name": "Jarabe de agave", "category": "Endulzantes"}]},
            {"amount": "2", "unit": "gotas", "optional": False, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1", "unit": "twist", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/oaxaca-old-fashioned", "ingredients_text": ["Tequila", "Mezcal", "Jarabe de agave", "Amargo de angostura"]},
    },
    {
        "name": "White Negroni",
        "description": "Interpretacion moderna del Negroni con Suze y Lillet Blanc.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=White+Negroni&mood=bold&abv=22&method=Stir&glass=Rocks+Glass&spirit=gin&desc=A+lighter+Negroni+variation+with+gin+Suze+and+Lillet+Blanc&tags=bitter+herbal",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "negroni", "gin", "top-bars"],
        "steps": ["Agrega gin, Suze y Lillet Blanc a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo.", "Decora con una piel de limon si deseas."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Suze", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Lillet Blanc", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "twist", "optional": True, "options": [{"name": "Limon", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/white-negroni", "ingredients_text": ["Gin", "Suze", "Lillet Blanc"]},
    },
    {
        "name": "Gin Basil Smash",
        "description": "Moderno clasico verde y aromatico creado por Jörg Meyer.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Gin+Basil+Smash&mood=crisp&abv=20&method=Shake&glass=Rocks+Glass&spirit=gin&desc=A+modern+classic+that+muddles+fresh+basil+with+gin+and+citrus+for+an+aromatic+green+cocktail.&tags=herbal+citrusy",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "gin", "herbal", "top-bars"],
        "steps": ["Maja suavemente la albahaca en la coctelera.", "Agrega gin, jugo de limon y jarabe simple.", "Añade hielo y agita con fuerza.", "Haz doble colado sobre un vaso bajo con hielo."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
            {"amount": "8", "unit": "hojas", "optional": False, "options": [{"name": "Albahaca", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/gin-basil-smash", "ingredients_text": ["Gin", "Jugo de limon", "Jarabe simple", "Albahaca"]},
    },
    {
        "name": "Eastside",
        "description": "Coctel de gin, pepino y menta asociado a la escuela de Milk & Honey.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Eastside&mood=crisp&abv=20&method=Shake&glass=Coupe&spirit=gin&desc=A+refreshing+gin+cocktail+with+muddled+cucumber+and+mint%2C+lime+juice%2C+and+simple+syrup.&tags=fresh%2Cherbaceous%2Ccooling%2Cbright",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["moderno", "gin", "pepino", "top-bars"],
        "steps": ["Maja suavemente el pepino y la menta en una coctelera.", "Agrega gin, jugo de lima y jarabe simple.", "Añade hielo y agita con fuerza.", "Haz doble colado en una copa coupe fria."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
            {"amount": "3", "unit": "rodajas", "optional": False, "options": [{"name": "Pepino", "category": "Frutas"}]},
            {"amount": "6", "unit": "hojas", "optional": False, "options": [{"name": "Menta", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/eastside", "ingredients_text": ["Gin", "Jugo de lima", "Jarabe simple", "Pepino", "Menta"]},
    },
    {
        "name": "Jungle Bird",
        "description": "Tropical amargo con ron oscuro, Campari y pina; un clasico muy vigente en bares modernos.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Jungle+Bird&mood=tropical&abv=18&method=Shake&glass=Rocks+Glass&spirit=rum&desc=A+tropical+tiki+drink+balancing+rum+sweetness+with+bitter+Campari&tags=tropical+and+bitter",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "tiki", "campari", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo.", "Decora con pina o limon si deseas."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Ron oscuro", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de pinia", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/jungle-bird", "ingredients_text": ["Ron oscuro", "Campari", "Jugo de pina", "Jugo de lima", "Jarabe simple"]},
    },
    {
        "name": "Amaretto Sour",
        "description": "Sour moderno de perfil almendrado, mejorado con clara para una textura sedosa.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Amaretto+Sour&mood=crisp&abv=14&method=Shake&glass=Rocks+Glass&spirit=amaretto&desc=A+sweet+and+nutty+almond-flavored+sour+with+bright+citrus&tags=sweet+and+nutty",
        "prep_time_minutes": 6,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["moderno", "sour", "amaretto", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera sin hielo y agita en seco.", "Añade hielo y vuelve a agitar con fuerza.", "Cuela sobre hielo fresco en un vaso bajo.", "Decora con unas gotas de bitters si deseas."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Amaretto", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
            {"amount": "1/2", "unit": "oz", "optional": True, "options": [{"name": "Clara de huevo", "category": "Cremas y lacteos"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/amaretto-sour", "ingredients_text": ["Amaretto", "Jugo de limon", "Jarabe simple", "Clara de huevo"]},
    },
    {
        "name": "The Business",
        "description": "Sour de gin con miel y lima, una especie de Bee's Knees mas afilado.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=The+Business&mood=crisp&abv=24&method=Shake&glass=Coupe&spirit=gin&desc=A+lime-forward+honey+and+gin+cocktail+-+the+Bee%27s+Knees%27+zestier+cousin.&tags=tart+floral+botanical",
        "prep_time_minutes": 4,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["moderno", "gin", "miel", "top-bars"],
        "steps": ["Agrega gin, jugo de lima y jarabe de miel a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve sin garnish o con piel de lima si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jarabe de miel", "category": "Endulzantes"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/the-business", "ingredients_text": ["Gin", "Jugo de lima", "Jarabe de miel"]},
    },
    {
        "name": "Siesta",
        "description": "Coctel moderno de tequila, Campari, citricos y jarabe simple.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Siesta&mood=party&abv=20&method=Shake&glass=Coupe&spirit=tequila&desc=A+tequila+variation+on+the+Hemingway+Daiquiri+with+Campari+for+bitterness&tags=citrusy+and+bitter",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Copa coupe",
        "tags": ["moderno", "tequila", "campari", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Tequila", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de pomelo", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jarabe simple", "category": "Endulzantes"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/siesta", "ingredients_text": ["Tequila", "Campari", "Jugo de limon", "Jugo de pomelo", "Jarabe simple"]},
    },
    {
        "name": "Trinidad Sour",
        "description": "Moderno clasico extremo que usa Angostura como base junto a whisky y falernum.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Trinidad+Sour&mood=crisp&abv=24&method=Shake&glass=Coupe&spirit=amaro&desc=A+startling+sour+using+a+full+ounce+of+Angostura+bitters+as+the+base&tags=spiced+and+complex",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["moderno", "bitters", "falernum", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve sin garnish."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Whiskey de centeno", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Falernum", "category": "Licores y aperitivos"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/trinidad-sour", "ingredients_text": ["Amargo de angostura", "Whiskey de centeno", "Jugo de limon", "Falernum"]},
    },
    {
        "name": "Division Bell",
        "description": "Variante moderna de la familia Last Word con mezcal, Aperol y maraschino.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Division+Bell&mood=bold&abv=24&method=Shake&glass=Coupe&spirit=mezcal&desc=A+mezcal-based+Last+Word+variation+with+Aperol+adding+bitter+orange+notes&tags=smoky+and+bittersweet",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["moderno", "mezcal", "last-word-family", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Mezcal", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Aperol", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Licor de maraschino", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/division-bell", "ingredients_text": ["Mezcal", "Aperol", "Licor de maraschino", "Jugo de lima"]},
    },
    {
        "name": "Final Ward",
        "description": "Twist moderno sobre el Last Word con whiskey de centeno y limon.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Final+Ward&mood=bold&abv=26&method=Shake&glass=Coupe&spirit=rye-whiskey&desc=A+rye+whiskey+Last+Word+variation+with+lemon+replacing+lime&tags=herbaceous+and+citrusy",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["moderno", "rye", "last-word-family", "top-bars"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Whiskey de centeno", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Green Chartreuse", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Licor de maraschino", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/final-ward", "ingredients_text": ["Whiskey de centeno", "Green Chartreuse", "Licor de maraschino", "Jugo de limon"]},
    },
]


def normalized(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-curated-round3-{time.strftime('%Y%m%d-%H%M%S')}.json"
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
