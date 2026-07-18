import hashlib
import json
import os
import sqlite3
import time
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "cocktail.db"
STATIC_DIR = BASE_DIR / "static"
HOST = "127.0.0.1"
PORT = 8000
DEFAULT_ADMIN_PASSWORD = "admin123"
SESSION_COOKIE = "cocktail_admin_session"
SESSION_TTL_SECONDS = 60 * 60 * 12
SESSIONS = {}


def json_response(handler, payload, status=200):
    raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def read_json_body(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length) if length else b""
    return json.loads(raw.decode("utf-8")) if raw else {}


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT,
            alcoholic INTEGER NOT NULL DEFAULT 0,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS inventory (
            ingredient_id INTEGER PRIMARY KEY,
            in_stock INTEGER NOT NULL DEFAULT 0,
            low_stock INTEGER NOT NULL DEFAULT 0,
            quantity_label TEXT DEFAULT '',
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        );
        CREATE TABLE IF NOT EXISTS shopping_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            note TEXT DEFAULT '',
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ingredient_id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        );
        CREATE TABLE IF NOT EXISTS cocktails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            image_url TEXT DEFAULT '',
            prep_time_minutes INTEGER NOT NULL DEFAULT 5,
            difficulty TEXT DEFAULT 'media',
            strength TEXT DEFAULT '',
            is_alcoholic INTEGER NOT NULL DEFAULT 1,
            instructions TEXT DEFAULT '',
            rating REAL NOT NULL DEFAULT 0,
            is_favorite INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS cocktail_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cocktail_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL,
            FOREIGN KEY (cocktail_id) REFERENCES cocktails(id)
        );
        CREATE TABLE IF NOT EXISTS cocktail_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cocktail_id INTEGER NOT NULL,
            group_key TEXT NOT NULL,
            ingredient_id INTEGER NOT NULL,
            amount TEXT DEFAULT '',
            unit TEXT DEFAULT '',
            optional_group INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (cocktail_id) REFERENCES cocktails(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        );
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS cocktail_tags (
            cocktail_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (cocktail_id, tag_id),
            FOREIGN KEY (cocktail_id) REFERENCES cocktails(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );
        CREATE TABLE IF NOT EXISTS cocktail_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            is_public INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS cocktail_list_items (
            list_id INTEGER NOT NULL,
            cocktail_id INTEGER NOT NULL,
            PRIMARY KEY (list_id, cocktail_id),
            FOREIGN KEY (list_id) REFERENCES cocktail_lists(id),
            FOREIGN KEY (cocktail_id) REFERENCES cocktails(id)
        );
        """
    )
    cursor.execute(
        "INSERT OR IGNORE INTO settings(key, value) VALUES('admin_password_hash', ?)",
        (hash_password(DEFAULT_ADMIN_PASSWORD),),
    )
    cursor.execute("SELECT COUNT(*) AS count FROM ingredients")
    if cursor.fetchone()["count"] == 0:
        seed_database(connection)
    connection.commit()
    connection.close()


def seed_database(connection):
    cursor = connection.cursor()
    ingredients = [
        ("Tequila", "Destilado", 1), ("Ron blanco", "Destilado", 1),
        ("Whisky", "Destilado", 1), ("Pisco", "Destilado", 1),
        ("Gin", "Destilado", 1), ("Vodka", "Destilado", 1),
        ("Jugo de limon", "Citricos", 0), ("Jugo de lima", "Citricos", 0),
        ("Hielo", "Basicos", 0), ("Menta", "Hierbas", 0),
        ("Agua con gas", "Mezcladores", 0), ("Azucar", "Endulzantes", 0),
        ("Jarabe simple", "Endulzantes", 0), ("Triple sec", "Licores", 1),
        ("Vermut rojo", "Licores", 1), ("Amargo de angostura", "Bitters", 1),
        ("Cola", "Mezcladores", 0), ("Jugo de pinia", "Jugos", 0),
        ("Crema de coco", "Mezcladores", 0), ("Soda", "Mezcladores", 0),
    ]
    cursor.executemany("INSERT INTO ingredients(name, category, alcoholic) VALUES(?, ?, ?)", ingredients)
    cursor.execute("SELECT id, name FROM ingredients")
    ingredient_ids = {row["name"]: row["id"] for row in cursor.fetchall()}

    inventory_seed = [
        ("Tequila", 1, 0, "1 botella"), ("Ron blanco", 1, 1, "queda poco"),
        ("Whisky", 1, 0, "2 botellas"), ("Pisco", 1, 0, "1 botella"),
        ("Gin", 1, 0, "1 botella"), ("Jugo de limon", 1, 0, "500 ml"),
        ("Hielo", 1, 0, "abundante"), ("Menta", 1, 1, "pocas ramas"),
        ("Agua con gas", 1, 0, "6 botellas"), ("Jarabe simple", 1, 0, "250 ml"),
        ("Triple sec", 1, 0, "1 botella"), ("Amargo de angostura", 1, 0, "1 botella"),
        ("Cola", 1, 0, "8 latas"), ("Jugo de pinia", 0, 0, ""),
        ("Crema de coco", 0, 0, ""), ("Soda", 1, 0, "4 botellas"),
    ]
    cursor.executemany(
        "INSERT INTO inventory(ingredient_id, in_stock, low_stock, quantity_label) VALUES(?, ?, ?, ?)",
        [(ingredient_ids[name], in_stock, low_stock, qty) for name, in_stock, low_stock, qty in inventory_seed],
    )

    tags = [("fuerte",), ("dulce",), ("citricos",), ("aperitivo",), ("rapido",), ("refrescante",), ("sin alcohol",), ("fiesta",)]
    cursor.executemany("INSERT INTO tags(name) VALUES(?)", tags)
    cursor.execute("SELECT id, name FROM tags")
    tag_ids = {row["name"]: row["id"] for row in cursor.fetchall()}

    cocktails = [
        ("Margarita", "Clasico coctel citrico con tequila.", "https://images.unsplash.com/photo-1551751299-1b51cab2694c?auto=format&fit=crop&w=900&q=80", 5, "media", "media", 1, "Agita y sirve en copa fria.", 4.7, 1),
        ("Mojito", "Refrescante, con menta y citricos.", "https://images.unsplash.com/photo-1575023782549-62ca0d244b39?auto=format&fit=crop&w=900&q=80", 7, "media", "suave", 1, "Macerar, mezclar y completar con gas.", 4.8, 1),
        ("Whisky Cola", "Simple, rapido y directo.", "https://images.unsplash.com/photo-1544145945-f90425340c7e?auto=format&fit=crop&w=900&q=80", 3, "facil", "media", 1, "Servir sobre hielo y completar con cola.", 4.0, 0),
        ("Pina Colada", "Tropical y dulce.", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=900&q=80", 8, "media", "suave", 1, "Licuar o agitar hasta integrar.", 4.6, 1),
        ("Virgin Fizz", "Opcion sin alcohol para invitados.", "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?auto=format&fit=crop&w=900&q=80", 4, "facil", "sin alcohol", 0, "Mezclar y servir sobre hielo.", 3.9, 0),
    ]
    cursor.executemany(
        "INSERT INTO cocktails(name, description, image_url, prep_time_minutes, difficulty, strength, is_alcoholic, instructions, rating, is_favorite) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        cocktails,
    )
    cursor.execute("SELECT id, name FROM cocktails")
    cocktail_ids = {row["name"]: row["id"] for row in cursor.fetchall()}

    requirements = [
        ("Margarita", "base", "Tequila", "2", "oz", 0), ("Margarita", "citrico", "Jugo de limon", "1", "oz", 0),
        ("Margarita", "citrico", "Jugo de lima", "1", "oz", 0), ("Margarita", "licor", "Triple sec", "1", "oz", 0),
        ("Margarita", "frio", "Hielo", "al gusto", "", 0), ("Mojito", "base", "Ron blanco", "2", "oz", 0),
        ("Mojito", "base", "Pisco", "2", "oz", 0), ("Mojito", "hierba", "Menta", "8", "hojas", 0),
        ("Mojito", "citrico", "Jugo de limon", "1", "oz", 0), ("Mojito", "dulzor", "Jarabe simple", "0.75", "oz", 0),
        ("Mojito", "gas", "Agua con gas", "top", "", 0), ("Mojito", "frio", "Hielo", "al gusto", "", 0),
        ("Whisky Cola", "base", "Whisky", "2", "oz", 0), ("Whisky Cola", "mezcla", "Cola", "top", "", 0),
        ("Whisky Cola", "frio", "Hielo", "al gusto", "", 0), ("Pina Colada", "base", "Ron blanco", "2", "oz", 0),
        ("Pina Colada", "base", "Pisco", "2", "oz", 0), ("Pina Colada", "jugo", "Jugo de pinia", "3", "oz", 0),
        ("Pina Colada", "crema", "Crema de coco", "1.5", "oz", 0), ("Pina Colada", "frio", "Hielo", "1", "taza", 0),
        ("Virgin Fizz", "citrico", "Jugo de limon", "1", "oz", 0), ("Virgin Fizz", "dulzor", "Jarabe simple", "1", "oz", 0),
        ("Virgin Fizz", "gas", "Soda", "top", "", 0), ("Virgin Fizz", "frio", "Hielo", "al gusto", "", 0),
        ("Virgin Fizz", "decoracion", "Menta", "2", "hojas", 1),
    ]
    cursor.executemany(
        "INSERT INTO cocktail_requirements(cocktail_id, group_key, ingredient_id, amount, unit, optional_group) VALUES(?, ?, ?, ?, ?, ?)",
        [(cocktail_ids[c], g, ingredient_ids[i], a, u, o) for c, g, i, a, u, o in requirements],
    )

    steps = [
        ("Margarita", 1, "Enfria la copa."), ("Margarita", 2, "Agrega tequila, citrico, triple sec y hielo a una coctelera."),
        ("Margarita", 3, "Agita 15 segundos y cuela."), ("Mojito", 1, "Macerar menta suavemente con el citrico y el jarabe."),
        ("Mojito", 2, "Agregar ron o pisco e incorporar hielo."), ("Mojito", 3, "Completar con agua con gas y mezclar corto."),
        ("Whisky Cola", 1, "Llena el vaso con hielo."), ("Whisky Cola", 2, "Sirve whisky."),
        ("Whisky Cola", 3, "Completa con cola."), ("Pina Colada", 1, "Agrega todos los ingredientes a una licuadora."),
        ("Pina Colada", 2, "Licua hasta obtener textura cremosa."), ("Pina Colada", 3, "Sirve en vaso frio."),
        ("Virgin Fizz", 1, "Sirve hielo en vaso alto."), ("Virgin Fizz", 2, "Agrega jugo de limon y jarabe simple."),
        ("Virgin Fizz", 3, "Completa con soda y decora con menta si tienes."),
    ]
    cursor.executemany(
        "INSERT INTO cocktail_steps(cocktail_id, step_number, instruction) VALUES(?, ?, ?)",
        [(cocktail_ids[name], step, instruction) for name, step, instruction in steps],
    )

    cocktail_tags = [
        ("Margarita", "citricos"), ("Margarita", "fiesta"), ("Margarita", "fuerte"),
        ("Mojito", "refrescante"), ("Mojito", "citricos"), ("Mojito", "fiesta"),
        ("Whisky Cola", "rapido"), ("Whisky Cola", "fuerte"), ("Pina Colada", "dulce"),
        ("Pina Colada", "fiesta"), ("Virgin Fizz", "sin alcohol"), ("Virgin Fizz", "rapido"),
        ("Virgin Fizz", "refrescante"),
    ]
    cursor.executemany("INSERT INTO cocktail_tags(cocktail_id, tag_id) VALUES(?, ?)", [(cocktail_ids[c], tag_ids[t]) for c, t in cocktail_tags])

    lists = [("Rapidos de preparar", "Carta corta para momentos con alta demanda", 1), ("Fiesta tequila", "Seleccion para una noche centrada en tequila", 1)]
    cursor.executemany("INSERT INTO cocktail_lists(name, description, is_public) VALUES(?, ?, ?)", lists)
    cursor.execute("SELECT id, name FROM cocktail_lists")
    list_ids = {row["name"]: row["id"] for row in cursor.fetchall()}
    cursor.executemany(
        "INSERT INTO cocktail_list_items(list_id, cocktail_id) VALUES(?, ?)",
        [(list_ids["Rapidos de preparar"], cocktail_ids["Whisky Cola"]), (list_ids["Rapidos de preparar"], cocktail_ids["Virgin Fizz"]), (list_ids["Fiesta tequila"], cocktail_ids["Margarita"])],
    )
    cursor.executemany(
        "INSERT INTO shopping_items(ingredient_id, note, done) VALUES(?, ?, ?)",
        [(ingredient_ids["Jugo de pinia"], "Comprar para cocteles tropicales", 0), (ingredient_ids["Crema de coco"], "Falta para pina colada", 0)],
    )


def load_settings(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT key, value FROM settings")
    return {row["key"]: row["value"] for row in cursor.fetchall()}


def fetch_tags_map(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM tags ORDER BY name")
    return {row["id"]: row["name"] for row in cursor.fetchall()}


def ingredient_stock_map(connection):
    cursor = connection.cursor()
    cursor.execute(
        "SELECT i.id, i.name, COALESCE(inv.in_stock, 0) AS in_stock, COALESCE(inv.low_stock, 0) AS low_stock, COALESCE(inv.quantity_label, '') AS quantity_label FROM ingredients i LEFT JOIN inventory inv ON inv.ingredient_id = i.id ORDER BY i.name"
    )
    return {row["id"]: dict(row) for row in cursor.fetchall()}


def cocktail_payload(connection, public_only=False):
    cursor = connection.cursor()
    tag_map = fetch_tags_map(connection)
    stock_map = ingredient_stock_map(connection)
    cursor.execute("SELECT * FROM cocktails WHERE is_active = 1 ORDER BY name")
    cocktails = []
    for cocktail in cursor.fetchall():
        cocktail_id = cocktail["id"]
        cursor.execute(
            "SELECT cr.id, cr.group_key, cr.amount, cr.unit, cr.optional_group, i.id AS ingredient_id, i.name AS ingredient_name FROM cocktail_requirements cr JOIN ingredients i ON i.id = cr.ingredient_id WHERE cr.cocktail_id = ? ORDER BY cr.group_key, i.name",
            (cocktail_id,),
        )
        groups = {}
        for row in cursor.fetchall():
            group = groups.setdefault(row["group_key"], {"group_key": row["group_key"], "optional": bool(row["optional_group"]), "amount": row["amount"], "unit": row["unit"], "options": []})
            ingredient_state = stock_map[row["ingredient_id"]]
            group["options"].append({"ingredient_id": row["ingredient_id"], "name": row["ingredient_name"], "in_stock": bool(ingredient_state["in_stock"]), "low_stock": bool(ingredient_state["low_stock"])})

        availability_details = []
        is_available = True
        for group in groups.values():
            available_options = [option for option in group["options"] if option["in_stock"]]
            group_available = bool(available_options) or group["optional"]
            if not group_available:
                is_available = False
            availability_details.append({"group_key": group["group_key"], "optional": group["optional"], "amount": group["amount"], "unit": group["unit"], "options": group["options"], "available": group_available, "selected_options": available_options})

        if public_only and not is_available:
            continue
        cursor.execute("SELECT ct.tag_id FROM cocktail_tags ct WHERE ct.cocktail_id = ? ORDER BY ct.tag_id", (cocktail_id,))
        tags = [tag_map[row["tag_id"]] for row in cursor.fetchall()]
        cursor.execute("SELECT step_number, instruction FROM cocktail_steps WHERE cocktail_id = ? ORDER BY step_number", (cocktail_id,))
        steps = [dict(row) for row in cursor.fetchall()]
        cocktails.append({"id": cocktail_id, "name": cocktail["name"], "description": cocktail["description"], "image_url": cocktail["image_url"], "prep_time_minutes": cocktail["prep_time_minutes"], "difficulty": cocktail["difficulty"], "strength": cocktail["strength"], "is_alcoholic": bool(cocktail["is_alcoholic"]), "instructions": cocktail["instructions"], "rating": cocktail["rating"], "is_favorite": bool(cocktail["is_favorite"]), "tags": tags, "steps": steps, "requirements": availability_details, "is_available": is_available})
    return cocktails


def filtered_public_payload(connection, query):
    cocktails = cocktail_payload(connection, public_only=True)
    ingredient_filter = (query.get("ingredient", [""])[0] or "").strip().lower()
    tag_filter = (query.get("tag", [""])[0] or "").strip().lower()
    alcohol_filter = (query.get("alcohol", ["all"])[0] or "all").strip().lower()
    list_filter = (query.get("list_id", [""])[0] or "").strip()

    if list_filter:
        cursor = connection.cursor()
        cursor.execute("SELECT cocktail_id FROM cocktail_list_items WHERE list_id = ?", (list_filter,))
        allowed_ids = {row["cocktail_id"] for row in cursor.fetchall()}
        cocktails = [cocktail for cocktail in cocktails if cocktail["id"] in allowed_ids]
    if ingredient_filter:
        cocktails = [cocktail for cocktail in cocktails if any(ingredient_filter in option["name"].lower() for requirement in cocktail["requirements"] for option in requirement["options"])]
    if tag_filter:
        cocktails = [cocktail for cocktail in cocktails if tag_filter in [tag.lower() for tag in cocktail["tags"]]]
    if alcohol_filter == "with":
        cocktails = [cocktail for cocktail in cocktails if cocktail["is_alcoholic"]]
    elif alcohol_filter == "without":
        cocktails = [cocktail for cocktail in cocktails if not cocktail["is_alcoholic"]]
    return cocktails


def get_public_lists(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, description FROM cocktail_lists WHERE is_public = 1 ORDER BY name")
    return [dict(row) for row in cursor.fetchall()]


def get_admin_dashboard(connection):
    cocktails = cocktail_payload(connection, public_only=False)
    cursor = connection.cursor()
    cursor.execute("SELECT i.id, i.name, i.category, i.alcoholic, COALESCE(inv.in_stock, 0) AS in_stock, COALESCE(inv.low_stock, 0) AS low_stock, COALESCE(inv.quantity_label, '') AS quantity_label FROM ingredients i LEFT JOIN inventory inv ON inv.ingredient_id = i.id ORDER BY i.category, i.name")
    ingredients = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT s.id, s.ingredient_id, s.note, s.done, i.name AS ingredient_name FROM shopping_items s JOIN ingredients i ON i.id = s.ingredient_id ORDER BY s.done, i.name")
    shopping = [dict(row) for row in cursor.fetchall()]
    return {"ingredients": ingredients, "cocktails": cocktails, "shopping": shopping, "lists": get_public_lists(connection)}


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
    value = token.value
    expires_at = SESSIONS.get(value)
    if not expires_at or expires_at < time.time():
        SESSIONS.pop(value, None)
        return False
    return True


class CocktailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.redirect("/menu")
            return
        if path == "/menu":
            self.serve_static_file("menu.html", "text/html; charset=utf-8")
            return
        if path == "/admin":
            self.serve_static_file("admin.html", "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            self.serve_asset(path.replace("/static/", "", 1))
            return

        connection = get_connection()
        try:
            if path == "/api/session":
                json_response(self, {"authenticated": is_authenticated(self)})
                return
            if path == "/api/public/cocktails":
                json_response(self, {"cocktails": filtered_public_payload(connection, query)})
                return
            if path == "/api/public/lists":
                json_response(self, {"lists": get_public_lists(connection)})
                return
            if path == "/api/admin/dashboard":
                if not is_authenticated(self):
                    json_response(self, {"error": "unauthorized"}, 401)
                    return
                json_response(self, get_admin_dashboard(connection))
                return
            json_response(self, {"error": "not_found"}, 404)
        finally:
            connection.close()

    def do_POST(self):
        path = urlparse(self.path).path
        body = read_json_body(self)
        connection = get_connection()
        cursor = connection.cursor()

        try:
            if path == "/api/login":
                settings = load_settings(connection)
                if hash_password(body.get("password", "")) != settings.get("admin_password_hash"):
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

            if not is_authenticated(self):
                json_response(self, {"error": "unauthorized"}, 401)
                return

            if path == "/api/admin/inventory":
                cursor.execute(
                    "INSERT INTO inventory(ingredient_id, in_stock, low_stock, quantity_label) VALUES(?, ?, ?, ?) ON CONFLICT(ingredient_id) DO UPDATE SET in_stock = excluded.in_stock, low_stock = excluded.low_stock, quantity_label = excluded.quantity_label",
                    (body["ingredient_id"], 1 if body.get("in_stock") else 0, 1 if body.get("low_stock") else 0, body.get("quantity_label", "")),
                )
                connection.commit()
                json_response(self, {"ok": True})
                return

            if path == "/api/admin/shopping":
                cursor.execute(
                    "INSERT INTO shopping_items(ingredient_id, note, done) VALUES(?, ?, ?) ON CONFLICT(ingredient_id) DO UPDATE SET note = excluded.note, done = excluded.done",
                    (body["ingredient_id"], body.get("note", ""), 1 if body.get("done") else 0),
                )
                connection.commit()
                json_response(self, {"ok": True})
                return

            if path == "/api/admin/cocktail-rating":
                cursor.execute("UPDATE cocktails SET rating = ?, is_favorite = ? WHERE id = ?", (float(body.get("rating", 0)), 1 if body.get("is_favorite") else 0, body["cocktail_id"]))
                connection.commit()
                json_response(self, {"ok": True})
                return

            if path == "/api/admin/cocktails":
                name = (body.get("name") or "").strip()
                if not name:
                    json_response(self, {"error": "name_required"}, 400)
                    return
                cursor.execute(
                    "INSERT INTO cocktails(name, description, image_url, prep_time_minutes, difficulty, strength, is_alcoholic, instructions, rating, is_favorite, is_active) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
                    (name, body.get("description", ""), body.get("image_url", ""), int(body.get("prep_time_minutes", 5)), body.get("difficulty", "media"), body.get("strength", ""), 1 if body.get("is_alcoholic", True) else 0, body.get("instructions", ""), float(body.get("rating", 0)), 1 if body.get("is_favorite") else 0),
                )
                connection.commit()
                json_response(self, {"ok": True})
                return

            if path == "/api/admin/lists":
                name = (body.get("name") or "").strip()
                if not name:
                    json_response(self, {"error": "name_required"}, 400)
                    return
                cursor.execute("INSERT INTO cocktail_lists(name, description, is_public) VALUES(?, ?, ?)", (name, body.get("description", ""), 1 if body.get("is_public", True) else 0))
                connection.commit()
                json_response(self, {"ok": True})
                return

            json_response(self, {"error": "not_found"}, 404)
        finally:
            connection.close()

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
    initialize_db()
    server = ThreadingHTTPServer((HOST, PORT), CocktailHandler)
    print(f"Cocktail Bar Manager en http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
