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
        "name": "Piscola",
        "description": "Highball chileno muy popular, preparado con pisco, cola y hielo.",
        "image_url": "https://commons.wikimedia.org/wiki/Special:FilePath/Vaso%20de%20piscola.jpg",
        "prep_time_minutes": 3,
        "alcohol_level": "Medio",
        "glassware": "Vaso highball",
        "tags": ["chileno", "clasico", "verano", "rapido"],
        "steps": [
            "Llena un vaso highball con abundante hielo.",
            "Agrega el pisco.",
            "Completa con cola y mezcla suavemente.",
            "Decora con una rodaja de limon o lima si deseas.",
        ],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Cola", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Limon", "category": "Frutas"}, {"name": "Lima", "category": "Frutas"}]},
        ],
        "source": {
            "provider": "Wikipedia / Wikimedia Commons",
            "source_url": "https://en.wikipedia.org/wiki/Piscola",
            "ingredients_text": ["Pisco", "Cola", "Hielo", "Limon o lima"],
        },
    },
    {
        "name": "Terremoto",
        "description": "Trago chileno muy veraniego, servido con vino, espumante, granadina y helado de piña.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2023/07/terremoto-2.jpg",
        "prep_time_minutes": 10,
        "alcohol_level": "Medio",
        "glassware": "Vaso alto",
        "tags": ["chileno", "verano", "fiestas patrias", "vino"],
        "steps": [
            "Coloca una cucharada de granadina en un vaso grande.",
            "Agrega el vino blanco y el espumante, dejando espacio para el helado.",
            "Añade con cuidado el helado de piña para evitar demasiada espuma.",
            "Termina con un poco más de granadina y sirve de inmediato.",
        ],
        "requirements": [
            {"amount": "2", "unit": "cucharadas", "optional": False, "options": [{"name": "Granadina", "category": "Endulzantes"}]},
            {"amount": "1/2", "unit": "taza", "optional": False, "options": [{"name": "Vino blanco", "category": "Vinos y espumantes"}]},
            {"amount": "1/2", "unit": "taza", "optional": False, "options": [{"name": "Champagne", "category": "Vinos y espumantes"}]},
            {"amount": "3", "unit": "bolas", "optional": False, "options": [{"name": "Helado de pina", "category": "Bebidas y mixers"}]},
            {"amount": "1", "unit": "cucharada", "optional": True, "options": [{"name": "Fernet", "category": "Licores y aperitivos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/terremoto-trago-chileno/",
            "ingredients_text": ["Granadina", "Vino blanco", "Espumante", "Helado de pina"],
        },
    },
    {
        "name": "Cola de mono",
        "description": "Bebida chilena navideña cremosa, con leche, cafe y licor.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2012/12/cola-de-mono-5.jpg",
        "prep_time_minutes": 30,
        "alcohol_level": "Suave",
        "glassware": "Vaso bajo",
        "tags": ["chileno", "navidad", "cremoso", "cafe"],
        "steps": [
            "Calienta la leche con la leche condensada o el azucar, la canela y los clavos de olor.",
            "Disuelve el cafe en un poco de leche tibia y reincorporaló a la olla.",
            "Hierve suavemente unos minutos, retira del fuego y deja enfriar.",
            "Cuela la mezcla, agrega el licor y embotella bien frio.",
        ],
        "requirements": [
            {"amount": "3", "unit": "tazas", "optional": False, "options": [{"name": "Leche", "category": "Cremas y lacteos"}]},
            {"amount": "300", "unit": "ml", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}, {"name": "Aguardiente", "category": "Destilados"}, {"name": "Vodka", "category": "Destilados"}, {"name": "Brandy", "category": "Destilados"}]},
            {"amount": "1", "unit": "unidad", "optional": False, "options": [{"name": "Leche condensada", "category": "Cremas y lacteos"}, {"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "4", "unit": "cucharadas", "optional": False, "options": [{"name": "Cafe instantaneo", "category": "Basicos"}]},
            {"amount": "3", "unit": "unidad", "optional": True, "options": [{"name": "Clavos de olor", "category": "Condimentos"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Canela", "category": "Condimentos"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Pimienta de Jamaica", "category": "Condimentos"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Cardamomo", "category": "Condimentos"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Anis estrellado", "category": "Condimentos"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Nuez moscada", "category": "Condimentos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/cola-de-mono-chilean-coffee-eggnog/",
            "ingredients_text": ["Leche", "Pisco o aguardiente", "Leche condensada o azucar", "Cafe", "Especias"],
        },
    },
    {
        "name": "Borgoña",
        "description": "Clasico chileno de verano con vino tinto y frutillas maceradas.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2016/01/borgona-vino-h.jpg",
        "prep_time_minutes": 15,
        "alcohol_level": "Suave",
        "glassware": "Vaso corto",
        "tags": ["chileno", "verano", "vino", "frutal"],
        "steps": [
            "Pela los duraznos y cortalos en trozos pequenos sobre el jarro para aprovechar su jugo.",
            "Agrega las frutillas picadas y mezcla con azucar a gusto.",
            "Incorpora el vino tinto y el licor de naranja.",
            "Refrigera al menos 2 horas y sirve sobre hielo.",
        ],
        "requirements": [
            {"amount": "1", "unit": "botella", "optional": False, "options": [{"name": "Vino tinto", "category": "Vinos y espumantes"}]},
            {"amount": "1", "unit": "caja", "optional": False, "options": [{"name": "Frutillas", "category": "Frutas"}]},
            {"amount": "2", "unit": "unidad", "optional": True, "options": [{"name": "Durazno", "category": "Frutas"}]},
            {"amount": "a gusto", "unit": "", "optional": True, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "2", "unit": "cucharadas", "optional": True, "options": [{"name": "Cointreau", "category": "Licores y aperitivos"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/borgona-vino-tinto-frutillas/",
            "ingredients_text": ["Vino tinto", "Frutillas", "Durazno", "Azucar", "Cointreau"],
        },
    },
    {
        "name": "Clery",
        "description": "Version chilena de verano con vino blanco o late harvest y frutillas.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2011/06/vino-frutillas-clery.jpg",
        "prep_time_minutes": 20,
        "alcohol_level": "Suave",
        "glassware": "Vaso corto",
        "tags": ["chileno", "verano", "vino", "frutal"],
        "steps": [
            "Pela los duraznos y cortalos en trozos pequenos dentro del jarro.",
            "Agrega las frutillas picadas.",
            "Si el vino no es dulce, mezcla primero la fruta con un poco de azucar.",
            "Incorpora el vino y el Cointreau, refrigera al menos 2 horas y sirve bien frio.",
        ],
        "requirements": [
            {"amount": "375", "unit": "ml", "optional": False, "options": [{"name": "Vino Late Harvest", "category": "Vinos y espumantes"}, {"name": "Vino blanco", "category": "Vinos y espumantes"}]},
            {"amount": "6", "unit": "unidad", "optional": False, "options": [{"name": "Frutillas", "category": "Frutas"}]},
            {"amount": "2", "unit": "unidad", "optional": True, "options": [{"name": "Durazno", "category": "Frutas"}]},
            {"amount": "1", "unit": "cucharada", "optional": True, "options": [{"name": "Cointreau", "category": "Licores y aperitivos"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/vino-con-frutillas/",
            "ingredients_text": ["Vino late harvest o vino blanco", "Frutillas", "Durazno", "Cointreau"],
        },
    },
    {
        "name": "Melón con vino",
        "description": "Clasico veraniego chileno servido dentro de un melon ahuecado.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2014/01/Melon-con-vino-4-1-scaled.jpg",
        "prep_time_minutes": 15,
        "alcohol_level": "Suave",
        "glassware": "Melon ahuecado",
        "tags": ["chileno", "verano", "frutal", "vino"],
        "steps": [
            "Corta una base delgada del melon para estabilizarlo y abre la parte superior.",
            "Retira semillas y parte de la pulpa.",
            "Agrega el azucar, la pulpa picada y las frutas opcionales.",
            "Vierte el vino blanco bien frio, mezcla y sirve de inmediato o enfria hasta 2 horas.",
        ],
        "requirements": [
            {"amount": "1", "unit": "unidad", "optional": False, "options": [{"name": "Melon tuna", "category": "Frutas"}]},
            {"amount": "1/2", "unit": "litro", "optional": False, "options": [{"name": "Vino blanco", "category": "Vinos y espumantes"}]},
            {"amount": "1/2", "unit": "taza", "optional": False, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Platano", "category": "Frutas"}]},
            {"amount": "1", "unit": "unidad", "optional": True, "options": [{"name": "Durazno", "category": "Frutas"}, {"name": "Frutillas", "category": "Frutas"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/melon-con-vino-honeydew-melon-with-wine/",
            "ingredients_text": ["Melon tuna", "Platano", "Duraznos o frutillas", "Azucar", "Vino blanco"],
        },
    },
    {
        "name": "Ponche a la romana",
        "description": "Clasico chileno festivo, muy frio, con espumante y helado de pina.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2014/12/ponche-romana-pina-4.jpg",
        "prep_time_minutes": 15,
        "alcohol_level": "Suave",
        "glassware": "Copa flauta",
        "tags": ["chileno", "fiestas", "espumante", "verano"],
        "steps": [
            "Enfria las copas en el refrigerador.",
            "Sirve el helado de pina en cada copa.",
            "Rellena con champagne bien frio.",
            "Sirve de inmediato.",
        ],
        "requirements": [
            {"amount": "1", "unit": "botella", "optional": False, "options": [{"name": "Champagne", "category": "Vinos y espumantes"}]},
            {"amount": "1/2", "unit": "litro", "optional": False, "options": [{"name": "Helado de pina", "category": "Bebidas y mixers"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/ponche-de-pina-la-romana/",
            "ingredients_text": ["Champagne", "Helado de pina"],
        },
    },
    {
        "name": "Vino navegado",
        "description": "Bebida chilena caliente para invierno, preparada con vino tinto, naranja y especias.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2019/07/navegado-chileno-5.jpg",
        "prep_time_minutes": 20,
        "alcohol_level": "Medio",
        "glassware": "Tazon",
        "tags": ["chileno", "invierno", "caliente", "vino"],
        "steps": [
            "Rebana las naranjas e inserta los clavos de olor en la cascara para que no queden sueltos.",
            "Coloca el vino, el azucar, las naranjas y la canela en una olla.",
            "Calienta a fuego medio hasta que hierva suavemente.",
            "Baja el fuego, cocina unos minutos y sirve caliente en tazones.",
        ],
        "requirements": [
            {"amount": "2", "unit": "botellas", "optional": False, "options": [{"name": "Vino tinto", "category": "Vinos y espumantes"}]},
            {"amount": "1", "unit": "unidad", "optional": False, "options": [{"name": "Naranja", "category": "Frutas"}]},
            {"amount": "1", "unit": "taza", "optional": False, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "3", "unit": "unidad", "optional": True, "options": [{"name": "Canela", "category": "Condimentos"}]},
            {"amount": "5", "unit": "unidad", "optional": True, "options": [{"name": "Clavos de olor", "category": "Condimentos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/vino-navegado-chileno/",
            "ingredients_text": ["Vino tinto", "Naranja", "Canela", "Clavos de olor", "Azucar"],
        },
    },
    {
        "name": "Vaina",
        "description": "Trago chileno antiguo y cremoso, preparado con jerez o vino dulce, huevo y cacao.",
        "image_url": "https://cocinachilena.cl/wp-content/uploads/2014/10/vaina-trago-1.jpg",
        "prep_time_minutes": 10,
        "alcohol_level": "Fuerte",
        "glassware": "Copa de coctel",
        "tags": ["chileno", "clasico", "cremoso", "sobremesa"],
        "steps": [
            "Coloca todos los ingredientes en la licuadora.",
            "Procesa a velocidad alta durante un minuto.",
            "Prueba, corrige el dulzor si hace falta y sirve en copas.",
            "Espolvorea canela por encima y sirve de inmediato.",
        ],
        "requirements": [
            {"amount": "1", "unit": "taza", "optional": False, "options": [{"name": "Jerez", "category": "Vinos y espumantes"}, {"name": "Vino dulce", "category": "Vinos y espumantes"}]},
            {"amount": "1", "unit": "unidad", "optional": False, "options": [{"name": "Huevo", "category": "Cremas y lacteos"}]},
            {"amount": "1", "unit": "cucharadita", "optional": False, "options": [{"name": "Cacao en polvo", "category": "Condimentos"}]},
            {"amount": "1/4", "unit": "taza", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
            {"amount": "4", "unit": "cucharadas", "optional": False, "options": [{"name": "Azucar flor", "category": "Endulzantes"}]},
            {"amount": "unas", "unit": "gotas", "optional": True, "options": [{"name": "Whisky", "category": "Destilados"}, {"name": "Cognac", "category": "Destilados"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Canela", "category": "Condimentos"}]},
        ],
        "source": {
            "provider": "La Cocina Chilena de Pilar Hernandez",
            "source_url": "https://cocinachilena.cl/vaina-trago-chileno/",
            "ingredients_text": ["Jerez o vino dulce", "Huevo", "Cacao", "Whisky o cognac", "Hielo", "Azucar flor"],
        },
    },
    {
        "name": "Chilcano",
        "description": "Highball peruano de pisco, lima y ginger ale.",
        "image_url": "https://i.ytimg.com/vi/Oa98CmRzXpg/hqdefault.jpg",
        "prep_time_minutes": 4,
        "alcohol_level": "Suave",
        "glassware": "Vaso highball",
        "tags": ["peruano", "refrescante", "citrico", "rapido"],
        "steps": [
            "Llena un vaso highball con hielo.",
            "Agrega el pisco y el jugo de lima.",
            "Completa con ginger ale y mezcla suavemente.",
            "Termina con unas gotas de amargo de angostura si deseas.",
        ],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Ginger ale", "category": "Bebidas y mixers"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {
            "provider": "Smokeshow Mixology (YouTube)",
            "source_url": "https://www.youtube.com/watch?v=Oa98CmRzXpg",
            "ingredients_text": ["Pisco", "Jugo de lima", "Ginger ale", "Amargo de angostura"],
        },
    },
    {
        "name": "Fernet con coca",
        "description": "Clasico argentino que combina Fernet con cola en formato highball.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Fernet+con+Coca&mood=chill&abv=12&method=Build&glass=Highball+Glass&spirit=amaro&desc=Argentina%27s+iconic+national+cocktail%2C+blending+intensely+herbal+Fernet+Branca+with+sweet+cola+for+a+surprisingly+harmoni&tags=herbal%2Cminty%2Cbittersweet%2Ccola",
        "prep_time_minutes": 2,
        "alcohol_level": "Medio",
        "glassware": "Vaso highball",
        "tags": ["argentino", "clasico", "amargo", "rapido"],
        "steps": [
            "Llena un vaso highball con hielo.",
            "Agrega el Fernet.",
            "Completa con cola, idealmente vertiendola en angulo para mantener la burbuja.",
            "Mezcla suavemente y sirve de inmediato.",
        ],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Fernet", "category": "Licores y aperitivos"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Cola", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {
            "provider": "Jigger & Joy",
            "source_url": "https://jiggerandjoy.com/drinks/fernet-con-coca",
            "ingredients_text": ["Fernet Branca", "Cola", "Hielo"],
        },
    },
    {
        "name": "Aperol Spritz",
        "description": "Aperitivo italiano de baja graduacion con Aperol, Prosecco y soda.",
        "image_url": "https://www.aperol.com/app/uploads/2023/04/Tip-and-Tricks-5.jpg",
        "prep_time_minutes": 3,
        "alcohol_level": "Suave",
        "glassware": "Copa de vino",
        "tags": ["italiano", "aperitivo", "verano", "espumante"],
        "steps": [
            "Llena una copa de vino grande con hielo.",
            "Agrega el Prosecco.",
            "Incorpora el Aperol y luego la soda.",
            "Decora con una rodaja de naranja y mezcla suavemente.",
        ],
        "requirements": [
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Prosecco", "category": "Vinos y espumantes"}]},
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Aperol", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Agua con gas", "category": "Bebidas y mixers"}, {"name": "Soda", "category": "Bebidas y mixers"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {
            "provider": "Aperol",
            "source_url": "https://www.aperol.com/en-us/aperol-spritz-cocktail/",
            "ingredients_text": ["Prosecco", "Aperol", "Soda water", "Orange"],
        },
    },
    {
        "name": "Poncha",
        "description": "Bebida tradicional de Madeira con aguardiente de cana, miel y citricos.",
        "image_url": "https://i0.wp.com/rumdamadeira.com/wp-content/uploads/2021/04/receitas-poncha-1-1.jpg?fit=1200%2C800&ssl=1",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Vaso bajo",
        "tags": ["portugues", "madeira", "citrico", "tradicional"],
        "steps": [
            "Machaca o mezcla energicamente la miel con el jugo de limon y naranja.",
            "Agrega el aguardiente de cana o un ron blanco seco.",
            "Revuelve hasta integrar bien.",
            "Cuela en un vaso bajo y decora con una rodaja de naranja.",
        ],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Aguardiente", "category": "Destilados"}, {"name": "Ron blanco", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Miel", "category": "Endulzantes"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": True, "options": [{"name": "Jugo de naranja", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {
            "provider": "Madeira Rum / Jigger & Joy",
            "source_url": "https://rumdamadeira.com/en/recipe/poncha/",
            "ingredients_text": ["Aguardente de cana", "Miel", "Limon", "Naranja"],
        },
    },
]


def normalized(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-curated-round1-{time.strftime('%Y%m%d-%H%M%S')}.json"
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
