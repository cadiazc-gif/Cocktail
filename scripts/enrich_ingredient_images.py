import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


TRANSLATION_MAP = {
    "Ron blanco": ["White rum", "Rum"],
    "Ron claro": ["Light rum", "Rum"],
    "Ron oscuro": ["Dark rum", "Rum"],
    "Ron dorado": ["Gold rum", "Rum"],
    "Ron añejo": ["Aged rum", "Rum"],
    "Ron especiado": ["Spiced rum", "Rum"],
    "Ron Malibu": ["Malibu rum", "Malibu"],
    "Whiskey Bourbon": ["Bourbon whiskey", "Bourbon"],
    "Whisky escoces": ["Scotch whisky", "Scotch"],
    "Scotch single malt": ["Single malt Scotch", "Scotch whisky"],
    "Agua con gas": ["Sparkling water", "Carbonated water"],
    "Agua tonica": ["Tonic water"],
    "Azucar": ["Sugar"],
    "Azucar rubia": ["Brown sugar"],
    "Azucar flor": ["Powdered sugar"],
    "Azucar demerara": ["Demerara sugar"],
    "Jarabe simple": ["Simple syrup"],
    "Jugo de limon": ["Lemon juice", "Lemon"],
    "Jugo de lima": ["Lime juice", "Lime"],
    "Jugo de pinia": ["Pineapple juice", "Pineapple"],
    "Jugo de manzana": ["Apple juice", "Apple"],
    "Jugo de cereza": ["Cherry juice", "Cherry"],
    "Jugo de arandano": ["Cranberry juice", "Cranberry"],
    "Jugo de frutas": ["Fruit juice", "Fruit"],
    "Jugo de uva": ["Grape juice", "Grape"],
    "Jugo de pomelo": ["Grapefruit juice", "Grapefruit"],
    "Jugo de naranja": ["Orange juice", "Orange"],
    "Jugo de maracuya": ["Passion fruit juice", "Passion fruit"],
    "Jugo de granada": ["Pomegranate juice", "Pomegranate"],
    "Jugo de tomate": ["Tomato juice", "Tomato"],
    "Jarabe de coco": ["Coconut syrup", "Coconut"],
    "Jarabe de jengibre": ["Ginger syrup", "Ginger"],
    "Jarabe de miel": ["Honey syrup", "Honey"],
    "Jarabe de menta": ["Mint syrup", "Mint"],
    "Jarabe de maracuya": ["Passion fruit syrup", "Passion fruit"],
    "Jarabe de pina": ["Pineapple syrup", "Pineapple"],
    "Jarabe de frambuesa": ["Raspberry syrup", "Raspberry"],
    "Jarabe de romero": ["Rosemary syrup", "Rosemary"],
    "Jarabe de vainilla": ["Vanilla syrup", "Vanilla"],
    "Jarabe de rosas": ["Rose syrup", "Rose"],
    "Jarabe de horchata": ["Orgeat syrup", "Orgeat"],
    "Crema de coco": ["Cream of coconut"],
    "Crema de cacao": ["Creme de Cacao"],
    "Crema de cassis": ["Creme de Cassis"],
    "Crema de banana": ["Creme de Banane"],
    "Crema de mora": ["Creme de Mure"],
    "Crema de menta verde": ["Green Creme de Menthe"],
    "Crema de menta blanca": ["White Creme de Menthe"],
    "Crema irlandesa": ["Irish cream", "Baileys irish cream"],
    "Amargo de angostura": ["Angostura bitters"],
    "Amargo de naranja": ["Orange bitters"],
    "Amargo de durazno": ["Peach bitters"],
    "Amargo Peychaud": ["Peychaud bitters"],
    "Amargo": ["Bitters"],
    "Menta": ["Mint"],
    "Hielo": ["Ice cube", "Ice"],
    "Cola": ["Cola"],
    "Soda": ["Soda water", "Club soda"],
    "Bebida lima-limon": ["Lemon-lime soda"],
    "Bebida de limon": ["Bitter lemon", "Lemon soda"],
    "Bebida de uva": ["Grape soda"],
    "Bebida": ["Soft drink"],
    "Vermut rojo": ["Sweet vermouth", "Red vermouth"],
    "Vermut seco": ["Dry vermouth"],
    "Vermut dulce": ["Sweet vermouth"],
    "Vermut": ["Vermouth"],
    "Cerveza de jengibre": ["Ginger beer"],
    "Cerveza de raiz": ["Root beer"],
    "Whisky": ["Whisky"],
    "Whisky mezclado": ["Blended whisky", "Blended whiskey", "Whisky"],
    "Whisky de centeno": ["Rye whiskey", "Rye whisky"],
    "Whisky de Tennessee": ["Tennessee whiskey", "Whiskey"],
    "Whisky irlandes": ["Irish whiskey", "Whiskey"],
    "Gin": ["Gin"],
    "Vodka": ["Vodka"],
    "Vodka de durazno": ["Peach vodka", "Vodka"],
    "Vodka de arandano": ["Cranberry vodka", "Vodka"],
    "Vodka de lima": ["Lime vodka", "Vodka"],
    "Vodka de frambuesa": ["Raspberry vodka", "Vodka"],
    "Pisco": ["Pisco"],
    "Tequila": ["Tequila"],
    "Mezcal": ["Mezcal"],
    "Cachaca": ["Cachaca"],
    "Aguardiente": ["Aguardiente"],
    "Cognac": ["Cognac"],
    "Whiskey Bourbon": ["Bourbon", "Whiskey"],
    "Scotch mezclado": ["Blended Scotch", "Scotch"],
    "Scotch single malt": ["Single malt Scotch", "Scotch"],
    "Ron": ["Rum"],
    "Ron 151 grados": ["151 proof rum", "Rum"],
    "Ron blackstrap": ["Blackstrap rum", "Rum"],
    "Platano": ["Banana"],
    "Limon": ["Lemon"],
    "Lima": ["Lime"],
    "Naranja": ["Orange"],
    "Pina": ["Pineapple"],
    "Miel": ["Honey"],
    "Leche": ["Milk"],
    "Leche de coco": ["Coconut milk"],
    "Leche condensada": ["Condensed milk"],
    "Cafe": ["Coffee"],
    "Cafe espresso": ["Espresso"],
    "Helado": ["Ice cream"],
    "Helado de vainilla": ["Vanilla ice cream"],
    "Te": ["Tea"],
    "Te helado": ["Iced tea"],
    "Sal": ["Salt"],
    "Pimienta": ["Pepper"],
    "Pimienta negra": ["Black pepper"],
    "Pimienta cayena": ["Cayenne pepper"],
    "Pimienta de Jamaica": ["Allspice"],
    "Sal de apio": ["Celery salt"],
    "Semilla de comino": ["Cumin seed"],
    "Cardamomo": ["Cardamom"],
    "Canela": ["Cinnamon"],
    "Clavos de olor": ["Cloves"],
    "Nuez moscada": ["Nutmeg"],
    "Tomillo": ["Thyme"],
    "Romero": ["Rosemary"],
    "Lavanda": ["Lavender"],
    "Cilantro": ["Coriander"],
    "Aji en hojuelas": ["Red chili flakes"],
    "Pepino": ["Cucumber"],
    "Moras": ["Blackberries"],
    "Frutillas": ["Strawberries", "Strawberry"],
    "Cereza": ["Cherry"],
    "Cerezas": ["Cherries", "Cherry"],
    "Manzana": ["Apple"],
    "Fruta": ["Fruit"],
    "Nectar de damasco": ["Apricot nectar", "Apricot"],
    "Nectar de durazno": ["Peach nectar", "Peach"],
    "Cordial de grosella negra": ["Blackcurrant cordial", "Blackcurrant"],
    "Cordial de flor de sauco": ["Elderflower cordial", "Elderflower"],
    "Ponche de frutas": ["Fruit punch", "Punch"],
    "Mitad crema mitad leche": ["Half-and-half", "Cream"],
    "Vainilla": ["Vanilla"],
    "Extracto de vainilla": ["Vanilla extract", "Vanilla"],
    "Aceituna": ["Olive"],
    "Salmuera de aceituna": ["Olive brine", "Olive"],
    "Salsa picante": ["Hot sauce"],
    "Salsa Worcestershire": ["Worcestershire Sauce"],
    "Salsa de soya": ["Soy Sauce"],
    "Cacao en polvo": ["Cocoa powder", "Chocolate"],
    "Bebida": ["Soft drink"],
    "Cerveza": ["Beer"],
    "Cerveza lager": ["Lager", "Beer"],
    "Sidra": ["Cider"],
    "Oporto": ["Port"],
    "Oporto rubi": ["Ruby Port", "Port"],
    "Jerez": ["Sherry"],
    "Vino": ["Wine"],
    "Vino tinto": ["Red wine", "Wine"],
    "Vino blanco": ["White wine", "Wine"],
    "Absenta": ["Absinthe"],
    "Baileys crema irlandesa": ["Baileys irish cream", "Baileys"],
    "Fireball": ["Fireball", "Cinnamon schnapps"],
    "Licor de cafe": ["Coffee liqueur", "Kahlua"],
    "Licor de coco": ["Coconut liqueur"],
    "Licor de frambuesa": ["Raspberry liqueur", "Raspberry"],
    "Licor de cereza": ["Cherry liqueur", "Cherry"],
    "Licor de melon Midori": ["Midori melon liqueur", "Midori"],
    "Licor Godiva": ["Godiva liqueur", "Godiva"],
    "Curacao azul": ["Blue Curacao", "Curacao"],
    "Curacao naranja": ["Orange Curacao", "Curacao"],
    "Brandy de damasco": ["Apricot brandy", "Apricot"],
    "Brandy de cereza": ["Cherry brandy", "Cherry"],
    "Brandy de manzana": ["Apple brandy", "Applejack"],
    "Brandy de mora": ["Blackberry brandy", "Blackberry"],
    "Brandy de cafe": ["Coffee brandy", "Coffee"],
    "Brandy de durazno": ["Peach brandy", "Peach"],
    "Aniseta": ["Anisette"],
    "Crema": ["Cream"],
    "Crema espesa": ["Heavy cream", "Cream"],
    "Crema ligera": ["Light cream", "Cream"],
    "Crema batida": ["Whipped cream", "Cream"],
    "Crema para batir": ["Whipping cream", "Cream"],
    "Agua": ["Water"],
    "Cascara de naranja": ["Orange peel", "Orange"],
    "Cascara de limon": ["Lemon peel", "Lemon"],
    "Cascara de lima": ["Lime peel", "Lime"],
    "Espiral de naranja": ["Orange spiral", "Orange"],
    "Huevo": ["Egg"],
    "Clara de huevo": ["Egg white", "Egg"],
    "Yema de huevo": ["Egg yolk", "Egg"],
    "Limonada": ["Lemonade"],
    "Schnapps de frutilla": ["Strawberry schnapps", "Strawberry"],
    "Schnapps de durazno": ["Peach schnapps", "Peach"],
    "Schnapps de caramelo": ["Butterscotch schnapps", "Butterscotch"],
    "Cereza marrasquino": ["Maraschino cherry", "Cherry"],
    "Naranja sanguina": ["Blood Orange", "Orange"],
}


THECOCKTAILDB_IMAGE = "https://www.thecocktaildb.com/images/ingredients/{name}-Medium.png"
MANUAL_IMAGE_MAP = {
    "Jarabe simple": "https://www.thecocktaildb.com/images/ingredients/Sugar-Medium.png",
    "Mezcla sour": "https://www.thecocktaildb.com/images/ingredients/Lemon%20juice-Medium.png",
    "Mezcla agridulce": "https://www.thecocktaildb.com/images/ingredients/Lemon%20juice-Medium.png",
    "Helado": "https://commons.wikimedia.org/wiki/Special:FilePath/Ice-cream.jpg?width=144",
    "Helado de vainilla": "https://commons.wikimedia.org/wiki/Special:FilePath/Vanilla_ice_cream.jpg?width=144",
    "Rosa": "https://commons.wikimedia.org/wiki/Special:FilePath/Rose%2C.jpg?width=144",
    "Yogur": "https://commons.wikimedia.org/wiki/Special:FilePath/Yogurt%20(8500216176).png?width=144",
    "Aguardiente": "https://commons.wikimedia.org/wiki/Special:FilePath/Aguardiente.jpg?width=144",
    "Bebida": "https://commons.wikimedia.org/wiki/Special:FilePath/Soft%20drinks.jpg?width=144",
    "Mantequilla": "https://commons.wikimedia.org/wiki/Special:FilePath/NCI%20butter.jpg?width=144",
    "Alcohol de grano": "https://commons.wikimedia.org/wiki/Special:FilePath/GemClear-GrainAlcohol.jpg?width=144",
    "Sambuca negra": "https://commons.wikimedia.org/wiki/Special:FilePath/Carcelli%20Black%20Sambuca.jpg?width=144",
}


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return ascii_text


def url_exists(url, timeout=15):
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False


def ingredient_candidates(name):
    candidates = [name]
    if name in TRANSLATION_MAP:
        candidates.extend(TRANSLATION_MAP[name])

    patterns = [
        (r"^Jugo de (.+)$", lambda m: [f"{m.group(1)} juice", m.group(1)]),
        (r"^Jarabe de (.+)$", lambda m: [f"{m.group(1)} syrup", m.group(1)]),
        (r"^Licor de (.+)$", lambda m: [f"{m.group(1)} liqueur", m.group(1)]),
        (r"^Vodka de (.+)$", lambda m: [f"{m.group(1)} vodka", m.group(1)]),
        (r"^Brandy de (.+)$", lambda m: [f"{m.group(1)} brandy", m.group(1)]),
        (r"^Amargo de (.+)$", lambda m: [f"{m.group(1)} bitters", m.group(1)]),
        (r"^Crema de (.+)$", lambda m: [f"Cream of {m.group(1)}", f"{m.group(1)} cream"]),
        (r"^Cordial de (.+)$", lambda m: [f"{m.group(1)} cordial", m.group(1)]),
        (r"^Nectar de (.+)$", lambda m: [f"{m.group(1)} nectar", m.group(1)]),
    ]
    for pattern, builder in patterns:
        match = re.match(pattern, name, flags=re.IGNORECASE)
        if match:
            candidates.extend(builder(match))

    cleaned = slugify(name)
    candidates.append(cleaned)
    deduped = []
    seen = set()
    for item in candidates:
        candidate = " ".join(str(item).strip().split())
        if not candidate:
            continue
        key = candidate.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def enrich_image(ingredient):
    if ingredient["name"] in MANUAL_IMAGE_MAP:
        return MANUAL_IMAGE_MAP[ingredient["name"]]
    for candidate in ingredient_candidates(ingredient["name"]):
        cocktaildb_url = THECOCKTAILDB_IMAGE.format(name=urllib.parse.quote(candidate))
        if url_exists(cocktaildb_url):
            return cocktaildb_url
    return ""


def main():
    store = load_store()
    updated = 0
    unresolved = []

    for index, ingredient in enumerate(store["ingredients"], start=1):
        if ingredient.get("image_url"):
            continue
        image_url = enrich_image(ingredient)
        if image_url:
            ingredient["image_url"] = image_url
            updated += 1
        else:
            unresolved.append(ingredient["name"])
        if index % 10 == 0:
            save_store(store)
            time.sleep(0.1)

    save_store(store)
    print("ingredientes actualizados:", updated)
    print("sin resolver:", len(unresolved))
    for name in unresolved[:40]:
        print(name)


if __name__ == "__main__":
    main()
