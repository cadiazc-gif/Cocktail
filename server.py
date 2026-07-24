import hashlib
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STORE_PATH = DATA_DIR / "store.json"
STATIC_DIR = BASE_DIR / "static"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))
DEFAULT_ADMIN_PASSWORD = "admin123"
SESSION_COOKIE = "cocktail_admin_session"
SESSION_TTL_SECONDS = 60 * 60 * 12
SESSIONS = {}
UPSTASH_REDIS_REST_URL = os.environ.get("UPSTASH_REDIS_REST_URL", "").rstrip("/")
UPSTASH_REDIS_REST_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
UPSTASH_STORE_KEY = "cocktail_bar_store"
_STORE_LOCK = threading.Lock()
_STORE_CACHE = None
DEFAULT_UNITS_CATALOG = [
    "oz",
    "ml",
    "cl",
    "shot",
    "shots",
    "cdita",
    "cda",
    "dash",
    "gotas",
    "partes",
    "parte",
    "taza",
    "tazas",
    "hojas",
    "rebanada",
    "rodaja",
    "cubos",
    "botella",
    "splash",
    "pizca",
    "unidad",
    "twist",
]
CANONICAL_INGREDIENT_CATEGORIES = [
    "Basicos",
    "Destilados",
    "Licores y aperitivos",
    "Bitters",
    "Jugos y nectares",
    "Endulzantes",
    "Hierbas",
    "Frutas",
    "Garnish",
    "Condimentos",
    "Cremas y lacteos",
    "Bebidas y mixers",
    "Vinos y espumantes",
    "Cervezas y fermentados",
    "Otros",
]


def json_response(handler, payload, status=200):
    raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def normalize_alcohol_level(value, is_alcoholic=True):
    raw = (value or "").strip().lower()
    if raw in {"sin alcohol", "none", "no alcohol"} or not is_alcoholic:
        return "Sin alcohol"
    if raw in {"fuerte", "strong", "alto", "high"}:
        return "Fuerte"
    if raw in {"suave", "light", "bajo", "low"}:
        return "Suave"
    return "Medio"


def read_json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b""
    return json.loads(raw.decode("utf-8")) if raw else {}


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def discover_local_ip():
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        ip_address = probe.getsockname()[0]
        probe.close()
        return ip_address
    except OSError:
        return "127.0.0.1"


def default_store():
    return {
        "settings": {"admin_password_hash": hash_password(DEFAULT_ADMIN_PASSWORD), "units_catalog": DEFAULT_UNITS_CATALOG},
        "ingredients": [
            {"id": 1, "name": "Tequila", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 2, "name": "Ron blanco", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 3, "name": "Whisky", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 4, "name": "Pisco", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 5, "name": "Gin", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 6, "name": "Vodka", "category": "Destilado", "alcoholic": True, "tags": ["destilado"], "image_url": ""},
            {"id": 7, "name": "Jugo de limon", "category": "Citricos", "alcoholic": False, "tags": ["jugo", "citricos"], "image_url": ""},
            {"id": 8, "name": "Jugo de lima", "category": "Citricos", "alcoholic": False, "tags": ["jugo", "citricos"], "image_url": ""},
            {"id": 9, "name": "Hielo", "category": "Basicos", "alcoholic": False, "tags": ["basico"], "image_url": ""},
            {"id": 10, "name": "Menta", "category": "Hierbas", "alcoholic": False, "tags": ["hojas", "decoracion"], "image_url": ""},
            {"id": 11, "name": "Agua con gas", "category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
            {"id": 12, "name": "Azucar", "category": "Endulzantes", "alcoholic": False, "tags": ["jarabe", "endulzante"], "image_url": ""},
            {"id": 13, "name": "Jarabe simple", "category": "Endulzantes", "alcoholic": False, "tags": ["jarabe", "endulzante"], "image_url": ""},
            {"id": 14, "name": "Triple sec", "category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
            {"id": 15, "name": "Vermut rojo", "category": "Licores", "alcoholic": True, "tags": ["licor"], "image_url": ""},
            {"id": 16, "name": "Amargo de angostura", "category": "Bitters", "alcoholic": True, "tags": ["bitters"], "image_url": ""},
            {"id": 17, "name": "Cola", "category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
            {"id": 18, "name": "Jugo de pinia", "category": "Jugos", "alcoholic": False, "tags": ["jugo"], "image_url": ""},
            {"id": 19, "name": "Crema de coco", "category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
            {"id": 20, "name": "Soda", "category": "Mezcladores", "alcoholic": False, "tags": ["mezclador"], "image_url": ""},
        ],
        "inventory": {
            "1": {"in_stock": True, "low_stock": False, "quantity_label": "1 botella"},
            "2": {"in_stock": True, "low_stock": True, "quantity_label": "queda poco"},
            "3": {"in_stock": True, "low_stock": False, "quantity_label": "2 botellas"},
            "4": {"in_stock": True, "low_stock": False, "quantity_label": "1 botella"},
            "5": {"in_stock": True, "low_stock": False, "quantity_label": "1 botella"},
            "7": {"in_stock": True, "low_stock": False, "quantity_label": "500 ml"},
            "9": {"in_stock": True, "low_stock": False, "quantity_label": "abundante"},
            "10": {"in_stock": True, "low_stock": True, "quantity_label": "pocas ramas"},
            "11": {"in_stock": True, "low_stock": False, "quantity_label": "6 botellas"},
            "13": {"in_stock": True, "low_stock": False, "quantity_label": "250 ml"},
            "14": {"in_stock": True, "low_stock": False, "quantity_label": "1 botella"},
            "16": {"in_stock": True, "low_stock": False, "quantity_label": "1 botella"},
            "17": {"in_stock": True, "low_stock": False, "quantity_label": "8 latas"},
            "18": {"in_stock": False, "low_stock": False, "quantity_label": ""},
            "19": {"in_stock": False, "low_stock": False, "quantity_label": ""},
            "20": {"in_stock": True, "low_stock": False, "quantity_label": "4 botellas"},
        },
        "shopping": [
            {"ingredient_id": 18, "note": "Comprar para cocteles tropicales", "done": False},
            {"ingredient_id": 19, "note": "Falta para pina colada", "done": False},
        ],
        "cocktails": [
            {"id": 1, "name": "Margarita", "description": "Clasico coctel citrico con tequila.", "image_url": "https://images.unsplash.com/photo-1551751299-1b51cab2694c?auto=format&fit=crop&w=900&q=80", "prep_time_minutes": 5, "alcohol_level": "Medio", "instructions": "Agita y sirve en copa fria.", "rating": 4.7, "is_favorite": True, "is_active": True, "tags": ["citricos", "fiesta", "fuerte"], "glassware": "Copa margarita", "steps": [{"step_number": 1, "instruction": "Enfria la copa."}, {"step_number": 2, "instruction": "Agrega tequila, citrico, triple sec y hielo a una coctelera."}, {"step_number": 3, "instruction": "Agita 15 segundos y cuela."}], "requirements": [{"group_key": "base", "amount": "2", "unit": "oz", "optional": False, "options": [1]}, {"group_key": "citrico", "amount": "1", "unit": "oz", "optional": False, "options": [7, 8]}, {"group_key": "licor", "amount": "1", "unit": "oz", "optional": False, "options": [14]}, {"group_key": "frio", "amount": "al gusto", "unit": "", "optional": False, "options": [9]}]},
            {"id": 2, "name": "Mojito", "description": "Refrescante, con menta y citricos.", "image_url": "https://images.unsplash.com/photo-1575023782549-62ca0d244b39?auto=format&fit=crop&w=900&q=80", "prep_time_minutes": 7, "alcohol_level": "Suave", "instructions": "Macerar, mezclar y completar con gas.", "rating": 4.8, "is_favorite": True, "is_active": True, "tags": ["refrescante", "citricos", "fiesta"], "glassware": "Vaso highball", "steps": [{"step_number": 1, "instruction": "Macerar menta suavemente con el citrico y el jarabe."}, {"step_number": 2, "instruction": "Agregar ron o pisco e incorporar hielo."}, {"step_number": 3, "instruction": "Completar con agua con gas y mezclar corto."}], "requirements": [{"group_key": "base", "amount": "2", "unit": "oz", "optional": False, "options": [2, 4]}, {"group_key": "hierba", "amount": "8", "unit": "hojas", "optional": False, "options": [10]}, {"group_key": "citrico", "amount": "1", "unit": "oz", "optional": False, "options": [7]}, {"group_key": "dulzor", "amount": "0.75", "unit": "oz", "optional": False, "options": [13]}, {"group_key": "gas", "amount": "top", "unit": "", "optional": False, "options": [11]}, {"group_key": "frio", "amount": "al gusto", "unit": "", "optional": False, "options": [9]}]},
            {"id": 3, "name": "Whisky Cola", "description": "Simple, rapido y directo.", "image_url": "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80", "prep_time_minutes": 3, "alcohol_level": "Medio", "instructions": "Servir sobre hielo y completar con cola.", "rating": 4.0, "is_favorite": False, "is_active": True, "tags": ["rapido", "fuerte"], "glassware": "Vaso highball", "steps": [{"step_number": 1, "instruction": "Llena el vaso con hielo."}, {"step_number": 2, "instruction": "Sirve whisky."}, {"step_number": 3, "instruction": "Completa con cola."}], "requirements": [{"group_key": "base", "amount": "2", "unit": "oz", "optional": False, "options": [3]}, {"group_key": "mezcla", "amount": "top", "unit": "", "optional": False, "options": [17]}, {"group_key": "frio", "amount": "al gusto", "unit": "", "optional": False, "options": [9]}]},
            {"id": 4, "name": "Pina Colada", "description": "Tropical y dulce.", "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80", "prep_time_minutes": 8, "alcohol_level": "Suave", "instructions": "Licuar o agitar hasta integrar.", "rating": 4.6, "is_favorite": True, "is_active": True, "tags": ["dulce", "fiesta"], "glassware": "Copa hurricane", "steps": [{"step_number": 1, "instruction": "Agrega todos los ingredientes a una licuadora."}, {"step_number": 2, "instruction": "Licua hasta obtener textura cremosa."}, {"step_number": 3, "instruction": "Sirve en vaso frio."}], "requirements": [{"group_key": "base", "amount": "2", "unit": "oz", "optional": False, "options": [2, 4]}, {"group_key": "jugo", "amount": "3", "unit": "oz", "optional": False, "options": [18]}, {"group_key": "crema", "amount": "1.5", "unit": "oz", "optional": False, "options": [19]}, {"group_key": "frio", "amount": "1", "unit": "taza", "optional": False, "options": [9]}]},
            {"id": 5, "name": "Virgin Fizz", "description": "Opcion sin alcohol para invitados.", "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80", "prep_time_minutes": 4, "alcohol_level": "Sin alcohol", "instructions": "Mezclar y servir sobre hielo.", "rating": 3.9, "is_favorite": False, "is_active": True, "tags": ["sin alcohol", "rapido", "refrescante"], "glassware": "Vaso highball", "steps": [{"step_number": 1, "instruction": "Sirve hielo en vaso alto."}, {"step_number": 2, "instruction": "Agrega jugo de limon y jarabe simple."}, {"step_number": 3, "instruction": "Completa con soda y decora con menta si tienes."}], "requirements": [{"group_key": "citrico", "amount": "1", "unit": "oz", "optional": False, "options": [7]}, {"group_key": "dulzor", "amount": "1", "unit": "oz", "optional": False, "options": [13]}, {"group_key": "gas", "amount": "top", "unit": "", "optional": False, "options": [20]}, {"group_key": "frio", "amount": "al gusto", "unit": "", "optional": False, "options": [9]}, {"group_key": "decoracion", "amount": "2", "unit": "hojas", "optional": True, "options": [10]}]},
        ],
        "lists": [
            {"id": 1, "name": "Rapidos de preparar", "description": "Carta corta para momentos con alta demanda", "is_public": True, "cocktail_ids": [3, 5]},
            {"id": 2, "name": "Fiesta tequila", "description": "Seleccion para una noche centrada en tequila", "is_public": True, "cocktail_ids": [1]},
        ],
    }


def upstash_enabled():
    return bool(UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN)


def _upstash_request(path, method="GET", body=None):
    request = urllib.request.Request(
        f"{UPSTASH_REDIS_REST_URL}/{path}",
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {UPSTASH_REDIS_REST_TOKEN}"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _upstash_get_store_text():
    return _upstash_request(f"get/{UPSTASH_STORE_KEY}").get("result")


def _upstash_set_store_text(raw_text):
    _upstash_request(f"set/{UPSTASH_STORE_KEY}", method="POST", body=raw_text.encode("utf-8"))


def initialize_store():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text(json.dumps(default_store(), ensure_ascii=True, indent=2), encoding="utf-8")


def _read_local_store():
    initialize_store()
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _normalize_store(store):
    settings = store.setdefault("settings", {})
    settings.setdefault("admin_password_hash", hash_password(DEFAULT_ADMIN_PASSWORD))
    settings["units_catalog"] = sorted(dict.fromkeys([*DEFAULT_UNITS_CATALOG, *(settings.get("units_catalog") or [])]), key=str.lower)
    store.setdefault("suggestions", [])
    for cocktail in store.get("cocktails", []):
        cocktail["alcohol_level"] = normalize_alcohol_level(cocktail.get("alcohol_level") or cocktail.get("strength"), cocktail.get("is_alcoholic", True))
        cocktail.pop("difficulty", None)
        cocktail.pop("strength", None)
        cocktail.pop("is_alcoholic", None)
        cocktail.setdefault("admin_rating", cocktail.get("rating", 0))
        cocktail.setdefault("guest_rating_sum", 0.0)
        cocktail.setdefault("guest_rating_count", 0)
    return store


def load_store():
    global _STORE_CACHE
    with _STORE_LOCK:
        if _STORE_CACHE is not None:
            return _STORE_CACHE
        if upstash_enabled():
            try:
                raw = _upstash_get_store_text()
            except (urllib.error.URLError, OSError, ValueError) as exc:
                # Upstash unreachable right now: keep the site working off the
                # local fallback for this process instead of hard-failing every
                # request. Nothing new is persisted until Upstash is reachable
                # again and save_store() succeeds.
                print(f"[store] Upstash unreachable on load, using local fallback: {exc}")
                store = _read_local_store()
            else:
                if raw:
                    store = json.loads(raw)
                else:
                    # First run with Upstash configured and nothing stored yet:
                    # seed it from whatever is on disk (the catalog shipped in
                    # the repo) so the migration doesn't lose existing data.
                    store = _read_local_store()
                    try:
                        _upstash_set_store_text(json.dumps(store, ensure_ascii=True))
                    except (urllib.error.URLError, OSError, ValueError) as exc:
                        print(f"[store] Could not seed Upstash: {exc}")
        else:
            store = _read_local_store()
        store = _normalize_store(store)
        _STORE_CACHE = store
        return store


def save_store(store):
    global _STORE_CACHE
    with _STORE_LOCK:
        if upstash_enabled():
            # Let failures raise: a save that silently doesn't reach the only
            # durable copy should surface as an error, not disappear quietly.
            _upstash_set_store_text(json.dumps(store, ensure_ascii=True))
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")
        _STORE_CACHE = store


def ingredient_map(store):
    return {ingredient["id"]: ingredient for ingredient in store["ingredients"]}


def ingredient_replacement_ids(store, ingredient_id):
    ingredient = ingredient_map(store).get(ingredient_id)
    if not ingredient:
        return []
    return [
        replacement_id
        for replacement_id in ingredient.get("replacement_ingredient_ids", []) or []
        if replacement_id != ingredient_id and replacement_id in ingredient_map(store)
    ]


def units_catalog(store):
    settings = store.setdefault("settings", {})
    settings["units_catalog"] = sorted(dict.fromkeys([*DEFAULT_UNITS_CATALOG, *(settings.get("units_catalog") or [])]), key=str.lower)
    return settings["units_catalog"]


def add_unit_to_catalog(store, unit_value):
    unit = (unit_value or "").strip()
    if not unit:
        return
    catalog = units_catalog(store)
    if unit not in catalog:
        catalog.append(unit)
        store["settings"]["units_catalog"] = sorted(dict.fromkeys(catalog), key=str.lower)


def find_or_create_ingredient(store, ingredient_name, category_hint="Otros"):
    candidate = (ingredient_name or "").strip()
    if not candidate:
        raise ValueError("ingredient_name_required")
    existing = next((item for item in store["ingredients"] if item["name"].lower() == candidate.lower()), None)
    if existing:
        return existing["id"]
    ingredient_id = next_id(store["ingredients"])
    store["ingredients"].append(
        {
            "id": ingredient_id,
            "name": candidate,
            "category": category_hint,
            "alcoholic": False,
            "tags": [],
            "image_url": "",
        }
    )
    return ingredient_id


def find_existing_ingredient_id(store, ingredient_name):
    candidate = (ingredient_name or "").strip().lower()
    if not candidate:
        return None
    existing = next((item for item in store["ingredients"] if item["name"].strip().lower() == candidate), None)
    return existing["id"] if existing else None


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def now_iso():
    return time.strftime("%Y-%m-%d %H:%M")


class IngredientNotFoundError(Exception):
    def __init__(self, ingredient_name):
        super().__init__(ingredient_name)
        self.ingredient_name = ingredient_name


def build_requirements_from_rows(store, rows):
    requirements = []
    for index, requirement in enumerate(rows, start=1):
        options = [option.strip() for option in requirement.get("options", []) if option.strip()]
        if not options:
            continue
        option_ids = []
        for option in options:
            ingredient_id = find_existing_ingredient_id(store, option)
            if ingredient_id is None:
                raise IngredientNotFoundError(option)
            option_ids.append(ingredient_id)
        unit_value = (requirement.get("unit") or "").strip()
        add_unit_to_catalog(store, unit_value)
        requirements.append(
            {
                "group_key": requirement.get("group_key") or f"group-{index}",
                "amount": requirement.get("amount", ""),
                "unit": unit_value,
                "optional": bool(requirement.get("optional")),
                "options": option_ids,
            }
        )
    return requirements


def apply_cocktail_content_fields(cocktail, fields, store):
    # Resolve/validate the requirements FIRST so a bad ingredient name aborts
    # before anything on the live cocktail has been mutated.
    requirements = build_requirements_from_rows(store, fields.get("requirements", []))
    cocktail["name"] = (fields.get("name") or cocktail.get("name", "")).strip()
    cocktail["description"] = fields.get("description", "")
    cocktail["image_url"] = fields.get("image_url", "")
    cocktail["prep_time_minutes"] = int(fields.get("prep_time_minutes", 5))
    cocktail["alcohol_level"] = normalize_alcohol_level(fields.get("alcohol_level"), fields.get("alcohol_level") != "Sin alcohol")
    cocktail["glassware"] = (fields.get("glassware") or "").strip()
    if "instructions" in fields:
        cocktail["instructions"] = fields.get("instructions", "")
    cocktail["tags"] = [tag.strip() for tag in fields.get("tags", []) if tag.strip()]
    cocktail["steps"] = [{"step_number": index + 1, "instruction": step.strip()} for index, step in enumerate(fields.get("steps", [])) if step.strip()]
    cocktail["requirements"] = requirements
    # Source/instructions aren't something guests can propose (not shown on the
    # public suggestion form) — only touch them when the caller actually sent
    # them, so an accepted suggestion never silently blanks out the admin's
    # existing source attribution.
    if "source_provider" in fields or "source_url" in fields:
        source = cocktail.get("source") or {}
        source["provider"] = (fields.get("source_provider") or source.get("provider") or "").strip()
        source["source_url"] = (fields.get("source_url") or source.get("source_url") or "").strip()
        cocktail["source"] = source


def recompute_rating(cocktail):
    admin_rating = cocktail.get("admin_rating", cocktail.get("rating", 0))
    count = cocktail.get("guest_rating_count", 0)
    if not count:
        cocktail["rating"] = admin_rating
        return
    guest_sum = cocktail.get("guest_rating_sum", 0.0)
    if admin_rating:
        # Admin has an actual rating on record: it counts as one more "vote"
        # anchoring the blend.
        cocktail["rating"] = (admin_rating + guest_sum) / (1 + count)
    else:
        # rating 0 means "nobody has rated this yet" (same convention as the
        # admin's "Sin probar (0)" filter) — it's an empty slot, not a real
        # zero score, so don't let it drag down the guests' own average.
        cocktail["rating"] = guest_sum / count


def apply_admin_rating_if_changed(cocktail, new_rating_value):
    new_rating_value = float(new_rating_value)
    if new_rating_value != cocktail.get("admin_rating", cocktail.get("rating", 0)):
        cocktail["admin_rating"] = new_rating_value
        cocktail["guest_rating_sum"] = 0.0
        cocktail["guest_rating_count"] = 0
    recompute_rating(cocktail)


def inventory_state(store, ingredient_id):
    return store["inventory"].get(str(ingredient_id), {"in_stock": False, "low_stock": False, "quantity_label": ""})


def normalized_category(ingredient):
    raw = (ingredient.get("category") or "").strip().lower()
    name = (ingredient.get("name") or "").strip().lower()
    canonical_map = {item.lower(): item for item in CANONICAL_INGREDIENT_CATEGORIES}
    if raw in canonical_map:
        return canonical_map[raw]
    if raw == "basicos":
        return "Basicos"
    if raw == "destilado":
        return "Destilados"
    if raw == "licores":
        return "Licores"
    if raw == "hierbas":
        return "Hojas y hierbas"
    if raw == "jugos":
        return "Jugos"
    if raw == "citricos":
        return "Citricos"
    if raw == "endulzantes":
        return "Endulzantes"
    if raw == "mezcladores":
        return "Mezcladores"
    if raw == "bitters":
        return "Bitters"
    keyword_map = {
        "Destilados": ["vodka", "gin", "whisky", "whiskey", "rum", "ron", "tequila", "pisco", "bourbon", "brandy", "cognac", "mezcal", "scotch"],
        "Licores": ["liqueur", "liqueur", "vermouth", "campari", "aperol", "triple sec", "amaretto", "curacao", "chartreuse", "baileys", "schnapps", "licor"],
        "Jugos": ["juice", "jugo", "nectar", "puree", "pure"],
        "Citricos": ["lime", "lemon", "limon", "lima", "citron", "citrus"],
        "Hojas y hierbas": ["mint", "menta", "basil", "albahaca", "romero", "thyme", "hierba"],
        "Endulzantes": ["syrup", "jarabe", "sugar", "azucar", "honey", "miel", "grenadine", "agave"],
        "Bitters": ["bitters", "amargo", "angostura"],
        "Mezcladores": ["cola", "soda", "tonic", "agua", "water", "ginger ale", "ginger beer", "coconut cream", "cream", "milk", "leche"],
        "Basicos": ["ice", "hielo", "salt", "sal", "pepper", "egg", "clear", "foam"],
    }
    for category, keywords in keyword_map.items():
        if any(keyword in name for keyword in keywords):
            return category
    return "Otros"


def normalize_ingredient_tokens(values):
    normalized = []
    seen = set()
    for value in values or []:
        token = " ".join(str(value or "").strip().split()).lower()
        if not token or token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return sorted(normalized)


def infer_ingredient_tags(ingredient):
    existing = [tag.strip().lower() for tag in ingredient.get("tags", []) if tag.strip()]
    if existing:
        return normalize_ingredient_tokens(existing)
    name = (ingredient.get("name") or "").lower()
    category = normalized_category(ingredient).lower()
    tags = []
    if "destilado" in category:
        tags.append("destilado")
    if "licor" in category:
        tags.append("licor")
    if "jugo" in category:
        tags.append("jugo")
    if "citric" in category or "citricos" in category:
        tags.extend(["jugo", "citricos"])
    if "hierbas" in category:
        tags.extend(["hojas", "decoracion"])
    if "endulz" in category:
        tags.append("jarabe")
    if "bitters" in category:
        tags.append("bitters")
    if "mezcladores" in category:
        tags.append("mezclador")
    if "mint" in name or "menta" in name:
        tags.extend(["hojas", "decoracion"])
    if "juice" in name or "jugo" in name:
        tags.append("jugo")
    if "syrup" in name or "jarabe" in name or "grenadine" in name:
        tags.append("jarabe")
    if "vodka" in name or "gin" in name or "whisk" in name or "rum" in name or "ron" in name or "tequila" in name or "pisco" in name or "mezcal" in name:
        tags.append("destilado")
    if "triple sec" in name or "vermouth" in name or "campari" in name or "aperol" in name:
        tags.append("licor")
    if "salt" in name or "sal" in name or "ice" in name or "hielo" in name:
        tags.append("basico")
    return normalize_ingredient_tokens(tag for tag in tags if tag)


def category_rank(category_name):
    order = [
        "Basicos",
        "Destilados",
        "Licores",
        "Bitters",
        "Hojas y hierbas",
        "Citricos",
        "Jugos",
        "Endulzantes",
        "Mezcladores",
        "Otros",
    ]
    return order.index(category_name) if category_name in order else len(order)


def infer_glassware_from_text(cocktail):
    text = " ".join(
        [
            cocktail.get("description", ""),
            cocktail.get("instructions", ""),
            *(step.get("instruction", "") for step in cocktail.get("steps", [])),
        ]
    ).lower()
    if "vaso de shot" in text or "shot glass" in text:
        return "Vaso de shot"
    if "vaso collins" in text or "collins glass" in text:
        return "Vaso collins"
    if "vaso highball" in text or "highball glass" in text or "vaso alto" in text:
        return "Vaso highball"
    if "vaso old fashioned" in text or "old fashioned" in text:
        return "Vaso old fashioned"
    if "copa flauta" in text or "champagne flute" in text or "flute" in text:
        return "Copa flauta"
    if "copa martini" in text or "martini glass" in text:
        return "Copa martini"
    if "copa margarita" in text or "margarita glass" in text:
        return "Copa margarita"
    if "copa de vino" in text or "wine glass" in text:
        return "Copa de vino"
    if "copa de coctel" in text or "cocktail glass" in text:
        return "Copa de coctel"
    if "taza" in text or "mug" in text or "coffee mug" in text:
        return "Taza"
    return ""


def cocktail_payload(store):
    ingredients = ingredient_map(store)
    cocktails = []
    for cocktail in sorted(store["cocktails"], key=lambda item: item["name"]):
        if not cocktail.get("is_active", True):
            continue
        requirements = []
        is_available = True
        for requirement in cocktail["requirements"]:
            options = []
            selected_options = []
            selected_ids = set()
            for ingredient_id in requirement["options"]:
                ingredient = ingredients[ingredient_id]
                stock = inventory_state(store, ingredient_id)
                replacement_options = []
                if stock["in_stock"] and ingredient_id not in selected_ids:
                    selected_options.append({"ingredient_id": ingredient_id, "name": ingredient["name"], "in_stock": True, "low_stock": bool(stock["low_stock"]), "is_replacement": False})
                    selected_ids.add(ingredient_id)
                for replacement_id in ingredient_replacement_ids(store, ingredient_id):
                    replacement = ingredients[replacement_id]
                    replacement_stock = inventory_state(store, replacement_id)
                    replacement_payload = {
                        "ingredient_id": replacement_id,
                        "name": replacement["name"],
                        "in_stock": bool(replacement_stock["in_stock"]),
                        "low_stock": bool(replacement_stock["low_stock"]),
                    }
                    replacement_options.append(replacement_payload)
                    if replacement_stock["in_stock"] and replacement_id not in selected_ids:
                        selected_options.append({**replacement_payload, "is_replacement": True, "replaces_ingredient_id": ingredient_id})
                        selected_ids.add(replacement_id)
                options.append(
                    {
                        "ingredient_id": ingredient_id,
                        "name": ingredient["name"],
                        "in_stock": bool(stock["in_stock"]),
                        "low_stock": bool(stock["low_stock"]),
                        "replacement_options": replacement_options,
                    }
                )
            available = bool(selected_options) or requirement["optional"]
            if not available:
                is_available = False
            requirements.append({"group_key": requirement["group_key"], "amount": requirement["amount"], "unit": requirement["unit"], "optional": requirement["optional"], "options": options, "selected_options": selected_options, "available": available})
        payload = dict(cocktail)
        payload["glassware"] = cocktail.get("glassware") or infer_glassware_from_text(cocktail)
        payload["requirements"] = requirements
        payload["is_available"] = is_available
        cocktails.append(payload)
    return cocktails


def filtered_public_payload(store, query):
    cocktails = cocktail_payload(store)
    ingredient_filter = (query.get("ingredient", [""])[0] or "").strip().lower()
    tag_filter = (query.get("tag", [""])[0] or "").strip().lower()
    alcohol_filter = (query.get("alcohol", ["all"])[0] or "all").strip().lower()
    list_filter = (query.get("list_id", [""])[0] or "").strip()
    if list_filter:
        list_item = next((item for item in store["lists"] if str(item["id"]) == list_filter and item["is_public"]), None)
        allowed_ids = set(list_item["cocktail_ids"]) if list_item else set()
        cocktails = [cocktail for cocktail in cocktails if cocktail["id"] in allowed_ids]
    if ingredient_filter:
        cocktails = [cocktail for cocktail in cocktails if any(ingredient_filter in option["name"].lower() for requirement in cocktail["requirements"] for option in requirement["options"])]
    if tag_filter:
        cocktails = [cocktail for cocktail in cocktails if tag_filter in [tag.lower() for tag in cocktail["tags"]]]
    if alcohol_filter == "with":
        cocktails = [cocktail for cocktail in cocktails if cocktail.get("alcohol_level") != "Sin alcohol"]
    elif alcohol_filter == "without":
        cocktails = [cocktail for cocktail in cocktails if cocktail.get("alcohol_level") == "Sin alcohol"]
    elif alcohol_filter in {"fuerte", "medio", "suave", "sin alcohol"}:
        cocktails = [cocktail for cocktail in cocktails if (cocktail.get("alcohol_level") or "").lower() == alcohol_filter]
    return cocktails


def public_lists(store):
    return [{"id": item["id"], "name": item["name"], "description": item["description"]} for item in sorted(store["lists"], key=lambda x: x["name"]) if item["is_public"]]


def shopping_suggestions(store):
    suggestions = {}
    by_ingredient = ingredient_map(store)
    cocktails = cocktail_payload(store)
    for cocktail in cocktails:
        if cocktail["is_available"]:
            continue
        missing_required_groups = [group for group in cocktail["requirements"] if not group["available"] and not group["optional"]]
        if len(missing_required_groups) != 1:
            continue
        missing_group = missing_required_groups[0]
        for option in missing_group["options"]:
            ingredient_id = option["ingredient_id"]
            bucket = suggestions.setdefault(
                ingredient_id,
                {
                    "ingredient_id": ingredient_id,
                    "ingredient_name": by_ingredient[ingredient_id]["name"],
                    "cocktail_count": 0,
                    "cocktails": [],
                },
            )
            bucket["cocktail_count"] += 1
            bucket["cocktails"].append(cocktail["name"])
    return sorted(suggestions.values(), key=lambda item: (-item["cocktail_count"], item["ingredient_name"]))


def admin_dashboard(store):
    active_shopping_ids = {item["ingredient_id"] for item in store["shopping"] if not item.get("done")}
    ingredients_by_id = ingredient_map(store)
    ingredients = []
    for ingredient in sorted(store["ingredients"], key=lambda item: item["name"]):
        ingredient.setdefault("image_url", "")
        ingredient["tags"] = normalize_ingredient_tokens(infer_ingredient_tags(ingredient))
        ingredient.setdefault("replacement_ingredient_ids", [])
        stock = inventory_state(store, ingredient["id"])
        ingredients.append({
            "id": ingredient["id"],
            "name": ingredient["name"],
            "category": ingredient["category"],
            "normalized_category": normalized_category(ingredient),
            "alcoholic": ingredient["alcoholic"],
            "in_stock": stock["in_stock"],
            "low_stock": stock["low_stock"],
            "quantity_label": stock["quantity_label"],
            "tags": ingredient.get("tags", []),
            "image_url": ingredient.get("image_url", ""),
            "in_shopping": ingredient["id"] in active_shopping_ids,
            "replacement_ingredient_ids": ingredient.get("replacement_ingredient_ids", []),
            "replacement_names": [ingredients_by_id[item_id]["name"] for item_id in ingredient.get("replacement_ingredient_ids", []) if item_id in ingredients_by_id],
        })
    shopping = []
    by_id = ingredient_map(store)
    for item in sorted(store["shopping"], key=lambda x: (x["done"], by_id[x["ingredient_id"]]["name"])):
        shopping.append({"ingredient_id": item["ingredient_id"], "note": item["note"], "done": item["done"], "ingredient_name": by_id[item["ingredient_id"]]["name"], "normalized_category": normalized_category(by_id[item["ingredient_id"]])})
    low_stock_items = [
        {
            "ingredient_id": ingredient["id"],
            "ingredient_name": ingredient["name"],
            "quantity_label": inventory_state(store, ingredient["id"])["quantity_label"],
            "normalized_category": normalized_category(ingredient),
        }
        for ingredient in sorted(store["ingredients"], key=lambda item: item["name"])
        if inventory_state(store, ingredient["id"])["low_stock"]
    ]
    return {
        "ingredients": ingredients,
        "cocktails": cocktail_payload(store),
        "shopping": shopping,
        "low_stock_items": low_stock_items,
        "shopping_suggestions": shopping_suggestions(store),
        "lists": public_lists(store),
        "units_catalog": units_catalog(store),
        "ingredient_tag_catalog": sorted({item["category"] for item in ingredients if item.get("category")}, key=str.lower),
        "suggestions": sorted(store["suggestions"], key=lambda item: item["id"], reverse=True),
    }


def parse_cookie(header_value):
    jar = cookies.SimpleCookie()
    if header_value:
        jar.load(header_value)
    return jar


def create_session():
    token = hashlib.sha256(f"{time.time()}-{os.urandom(16).hex()}".encode("utf-8")).hexdigest()
    SESSIONS[token] = time.time() + SESSION_TTL_SECONDS
    return token


def is_authenticated(handler):
    jar = parse_cookie(handler.headers.get("Cookie"))
    token = jar.get(SESSION_COOKIE)
    if not token:
        return False
    expires_at = SESSIONS.get(token.value)
    if not expires_at or expires_at < time.time():
        SESSIONS.pop(token.value, None)
        return False
    return True


class CocktailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path in ("/", "/menu", "/m"):
            self.serve_static_file("menu.html", "text/html; charset=utf-8")
            return
        if path in ("/admin", "/a"):
            self.serve_static_file("admin.html", "text/html; charset=utf-8")
            return
        if path == "/healthz":
            json_response(self, {"ok": True}, 200)
            return
        if path.startswith("/static/"):
            self.serve_asset(path.replace("/static/", "", 1))
            return

        store = load_store()
        if path == "/api/public/access":
            local_ip = discover_local_ip()
            json_response(self, {"menu_url": f"http://{local_ip}:{PORT}/", "admin_url": f"http://{local_ip}:{PORT}/a", "local_ip": local_ip, "port": PORT})
            return
        if path == "/api/session":
            json_response(self, {"authenticated": is_authenticated(self)})
            return
        if path == "/api/public/cocktails":
            json_response(self, {"cocktails": filtered_public_payload(store, query)})
            return
        if path == "/api/public/lists":
            json_response(self, {"lists": public_lists(store)})
            return
        if path == "/api/admin/dashboard":
            if not is_authenticated(self):
                json_response(self, {"error": "unauthorized"}, 401)
                return
            json_response(self, admin_dashboard(store))
            return
        json_response(self, {"error": "not_found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = read_json_body(self)
        store = load_store()
        if path == "/api/login":
            if hash_password(body.get("password", "")) != store["settings"]["admin_password_hash"]:
                json_response(self, {"ok": False, "error": "invalid_credentials"}, 401)
                return
            token = create_session()
            payload = json.dumps({"ok": True}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/api/public/cocktail-vote":
            cocktail = next((item for item in store["cocktails"] if item["id"] == body.get("cocktail_id")), None)
            if not cocktail:
                json_response(self, {"error": "not_found"}, 404)
                return
            try:
                vote = float(body.get("rating"))
            except (TypeError, ValueError):
                json_response(self, {"error": "invalid_rating"}, 400)
                return
            if not (1 <= vote <= 5):
                json_response(self, {"error": "invalid_rating"}, 400)
                return
            previous = body.get("previous_rating")
            try:
                previous = float(previous) if previous is not None else None
            except (TypeError, ValueError):
                previous = None
            if previous is not None:
                cocktail["guest_rating_sum"] = cocktail.get("guest_rating_sum", 0.0) + (vote - previous)
            else:
                cocktail["guest_rating_sum"] = cocktail.get("guest_rating_sum", 0.0) + vote
                cocktail["guest_rating_count"] = cocktail.get("guest_rating_count", 0) + 1
            recompute_rating(cocktail)
            save_store(store)
            json_response(self, {"ok": True, "rating": cocktail["rating"], "guest_rating_count": cocktail["guest_rating_count"]})
            return
        if path == "/api/public/cocktail-suggest":
            cocktail = next((item for item in store["cocktails"] if item["id"] == body.get("cocktail_id")), None)
            if not cocktail:
                json_response(self, {"error": "not_found"}, 404)
                return
            try:
                build_requirements_from_rows(store, body.get("requirements", []))
            except IngredientNotFoundError as exc:
                json_response(self, {"error": "ingredient_not_found", "ingredient_name": exc.ingredient_name}, 400)
                return
            suggestion = {
                "id": next_id(store["suggestions"]),
                "cocktail_id": cocktail["id"],
                "cocktail_name": cocktail["name"],
                "submitted_at": now_iso(),
                "submitted_by": (body.get("submitted_by") or "").strip(),
                "status": "pending",
                # Only fields the public form actually shows — deliberately
                # omits instructions/source_provider/source_url, which guests
                # never see, so apply_cocktail_content_fields() leaves those
                # untouched on the cocktail when this suggestion is accepted.
                "proposed": {
                    "name": (body.get("name") or "").strip(),
                    "description": body.get("description", ""),
                    "image_url": body.get("image_url", ""),
                    "prep_time_minutes": body.get("prep_time_minutes", 5),
                    "alcohol_level": body.get("alcohol_level", ""),
                    "glassware": body.get("glassware", ""),
                    "tags": body.get("tags", []),
                    "steps": body.get("steps", []),
                    "requirements": body.get("requirements", []),
                },
            }
            store["suggestions"].append(suggestion)
            save_store(store)
            json_response(self, {"ok": True, "suggestion_id": suggestion["id"]})
            return
        if not is_authenticated(self):
            json_response(self, {"error": "unauthorized"}, 401)
            return
        if path == "/api/admin/inventory":
            store["inventory"][str(body["ingredient_id"])] = {"in_stock": bool(body.get("in_stock")), "low_stock": bool(body.get("low_stock")), "quantity_label": body.get("quantity_label", "")}
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/shopping":
            current = next((item for item in store["shopping"] if item["ingredient_id"] == body["ingredient_id"]), None)
            if current:
                current["note"] = body.get("note", "")
                current["done"] = bool(body.get("done"))
            else:
                store["shopping"].append({"ingredient_id": body["ingredient_id"], "note": body.get("note", ""), "done": bool(body.get("done"))})
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/ingredient-save":
            ingredient = next(item for item in store["ingredients"] if item["id"] == body["ingredient_id"])
            ingredient["name"] = (body.get("name") or ingredient["name"]).strip()
            ingredient["image_url"] = (body.get("image_url") or "").strip()
            ingredient["tags"] = normalize_ingredient_tokens(body.get("tags", []))
            ingredient["replacement_ingredient_ids"] = sorted(
                {
                    int(item)
                    for item in body.get("replacement_ingredient_ids", [])
                    if str(item).strip().isdigit() and int(item) != ingredient["id"] and any(existing["id"] == int(item) for existing in store["ingredients"])
                }
            )
            category = (body.get("category") or "").strip()
            if category:
                ingredient["category"] = category
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/ingredient-merge":
            source_id = body["source_ingredient_id"]
            target_id = body["target_ingredient_id"]
            if source_id == target_id:
                json_response(self, {"error": "same_ingredient"}, 400)
                return
            source = next(item for item in store["ingredients"] if item["id"] == source_id)
            target = next(item for item in store["ingredients"] if item["id"] == target_id)
            affected_cocktails = set()
            for cocktail in store["cocktails"]:
                for requirement in cocktail.get("requirements", []):
                    if source_id in requirement.get("options", []):
                        affected_cocktails.add(cocktail["id"])
                    options = [target_id if option == source_id else option for option in requirement.get("options", [])]
                    requirement["options"] = sorted(dict.fromkeys(options))
            if str(source_id) in store["inventory"]:
                source_inventory = store["inventory"].pop(str(source_id))
                target_inventory = store["inventory"].get(str(target_id), {"in_stock": False, "low_stock": False, "quantity_label": ""})
                store["inventory"][str(target_id)] = {
                    "in_stock": target_inventory["in_stock"] or source_inventory["in_stock"],
                    "low_stock": target_inventory["low_stock"] or source_inventory["low_stock"],
                    "quantity_label": target_inventory["quantity_label"] or source_inventory["quantity_label"],
                }
            for item in store["shopping"]:
                if item["ingredient_id"] == source_id:
                    item["ingredient_id"] = target_id
            for ingredient in store["ingredients"]:
                replacements = []
                for replacement_id in ingredient.get("replacement_ingredient_ids", []) or []:
                    replacements.append(target_id if replacement_id == source_id else replacement_id)
                ingredient["replacement_ingredient_ids"] = sorted(dict.fromkeys(item for item in replacements if item != ingredient["id"]))
            merged_shopping = {}
            for item in store["shopping"]:
                bucket = merged_shopping.setdefault(
                    item["ingredient_id"],
                    {"ingredient_id": item["ingredient_id"], "note": "", "done": True},
                )
                if item.get("note") and not bucket["note"]:
                    bucket["note"] = item.get("note", "")
                bucket["done"] = bucket["done"] and bool(item.get("done", False))
            store["shopping"] = list(merged_shopping.values())
            target["tags"] = normalize_ingredient_tokens([*(target.get("tags", []) or []), *(source.get("tags", []) or [])])
            target["replacement_ingredient_ids"] = sorted(
                dict.fromkeys(
                    [
                        *(target.get("replacement_ingredient_ids", []) or []),
                        *(source.get("replacement_ingredient_ids", []) or []),
                    ]
                )
            )
            target["replacement_ingredient_ids"] = [item for item in target["replacement_ingredient_ids"] if item not in {target_id, source_id}]
            if not target.get("image_url"):
                target["image_url"] = source.get("image_url", "")
            store["ingredients"] = [item for item in store["ingredients"] if item["id"] != source_id]
            save_store(store)
            json_response(
                self,
                {
                    "ok": True,
                    "removed_ingredient_id": source_id,
                    "removed_ingredient_name": source["name"],
                    "target_ingredient_id": target_id,
                    "target_ingredient_name": target["name"],
                    "updated_cocktails": len(affected_cocktails),
                },
            )
            return
        if path == "/api/admin/ingredient-delete":
            ingredient_id = body["ingredient_id"]
            for cocktail in store["cocktails"]:
                filtered_requirements = []
                for requirement in cocktail.get("requirements", []):
                    options = [option for option in requirement.get("options", []) if option != ingredient_id]
                    if options:
                        requirement["options"] = options
                        filtered_requirements.append(requirement)
                cocktail["requirements"] = filtered_requirements
            for ingredient in store["ingredients"]:
                ingredient["replacement_ingredient_ids"] = [item for item in ingredient.get("replacement_ingredient_ids", []) or [] if item != ingredient_id]
            store["ingredients"] = [item for item in store["ingredients"] if item["id"] != ingredient_id]
            store["inventory"].pop(str(ingredient_id), None)
            store["shopping"] = [item for item in store["shopping"] if item["ingredient_id"] != ingredient_id]
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/cocktail-rating":
            cocktail = next(item for item in store["cocktails"] if item["id"] == body["cocktail_id"])
            apply_admin_rating_if_changed(cocktail, body.get("rating", 0))
            cocktail["is_favorite"] = bool(body.get("is_favorite"))
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/cocktail-source":
            cocktail = next(item for item in store["cocktails"] if item["id"] == body["cocktail_id"])
            source = cocktail.get("source") or {}
            source["provider"] = (body.get("provider") or "").strip()
            source["source_url"] = (body.get("source_url") or "").strip()
            cocktail["source"] = source
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/cocktail-save":
            cocktail = next(item for item in store["cocktails"] if item["id"] == body["cocktail_id"])
            try:
                apply_cocktail_content_fields(cocktail, body, store)
            except IngredientNotFoundError as exc:
                json_response(self, {"error": "ingredient_not_found", "ingredient_name": exc.ingredient_name}, 400)
                return
            apply_admin_rating_if_changed(cocktail, body.get("rating", 0))
            cocktail["is_favorite"] = bool(body.get("is_favorite"))
            cocktail["is_active"] = bool(body.get("is_active", True))
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/cocktail-delete":
            cocktail_id = body["cocktail_id"]
            store["cocktails"] = [item for item in store["cocktails"] if item["id"] != cocktail_id]
            for list_item in store["lists"]:
                list_item["cocktail_ids"] = [item for item in list_item.get("cocktail_ids", []) if item != cocktail_id]
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/cocktails":
            name = (body.get("name") or "").strip()
            if not name:
                json_response(self, {"error": "name_required"}, 400)
                return
            try:
                requirements = build_requirements_from_rows(store, body.get("requirements", []))
            except IngredientNotFoundError as exc:
                json_response(self, {"error": "ingredient_not_found", "ingredient_name": exc.ingredient_name}, 400)
                return
            rating_value = float(body.get("rating", 0))
            store["cocktails"].append({"id": next_id(store["cocktails"]), "name": name, "description": body.get("description", ""), "image_url": body.get("image_url", ""), "prep_time_minutes": int(body.get("prep_time_minutes", 5)), "alcohol_level": normalize_alcohol_level(body.get("alcohol_level"), body.get("alcohol_level") != "Sin alcohol"), "glassware": (body.get("glassware") or "").strip(), "instructions": body.get("instructions", ""), "rating": rating_value, "admin_rating": rating_value, "guest_rating_sum": 0.0, "guest_rating_count": 0, "is_favorite": bool(body.get("is_favorite")), "is_active": True, "tags": [], "steps": [{"step_number": index + 1, "instruction": step.strip()} for index, step in enumerate(body.get("steps", [])) if step.strip()], "requirements": requirements})
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/suggestions/accept":
            suggestion = next((item for item in store["suggestions"] if item["id"] == body.get("suggestion_id")), None)
            if not suggestion:
                json_response(self, {"error": "not_found"}, 404)
                return
            cocktail = next((item for item in store["cocktails"] if item["id"] == suggestion["cocktail_id"]), None)
            if not cocktail:
                json_response(self, {"error": "cocktail_not_found"}, 404)
                return
            try:
                apply_cocktail_content_fields(cocktail, suggestion["proposed"], store)
            except IngredientNotFoundError as exc:
                json_response(self, {"error": "ingredient_not_found", "ingredient_name": exc.ingredient_name}, 400)
                return
            suggestion["status"] = "accepted"
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/suggestions/reject":
            suggestion = next((item for item in store["suggestions"] if item["id"] == body.get("suggestion_id")), None)
            if not suggestion:
                json_response(self, {"error": "not_found"}, 404)
                return
            suggestion["status"] = "rejected"
            save_store(store)
            json_response(self, {"ok": True})
            return
        if path == "/api/admin/lists":
            name = (body.get("name") or "").strip()
            if not name:
                json_response(self, {"error": "name_required"}, 400)
                return
            store["lists"].append({"id": next_id(store["lists"]), "name": name, "description": body.get("description", ""), "is_public": bool(body.get("is_public", True)), "cocktail_ids": []})
            save_store(store)
            json_response(self, {"ok": True})
            return
        json_response(self, {"error": "not_found"}, 404)

    def log_message(self, format, *args):
        return

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def serve_static_file(self, filename, content_type):
        file_path = STATIC_DIR / filename
        raw = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def serve_asset(self, relative_name):
        file_path = STATIC_DIR / relative_name
        if not file_path.exists() or not file_path.is_file():
            json_response(self, {"error": "not_found"}, 404)
            return
        extension = file_path.suffix.lower()
        content_type = {".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8", ".html": "text/html; charset=utf-8"}.get(extension, "application/octet-stream")
        self.serve_static_file(relative_name, content_type)


def main():
    initialize_store()
    server = ThreadingHTTPServer((HOST, PORT), CocktailHandler)
    local_ip = discover_local_ip()
    print(f"Cocktail Bar Manager local: http://127.0.0.1:{PORT}/m")
    print(f"Cocktail Bar Manager red local: http://{local_ip}:{PORT}/m")
    server.serve_forever()


if __name__ == "__main__":
    main()
