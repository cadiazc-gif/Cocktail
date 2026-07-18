import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


BASE = {
    "Agua": "Basicos",
    "Hielo": "Basicos",
    "Huevo": "Basicos",
    "Clara de huevo": "Basicos",
    "Yema de huevo": "Basicos",
}

FRUITS = {
    "Lima",
    "Limon",
    "Naranja",
    "Pina",
    "Manzana",
    "Mango",
    "Kiwi",
    "Papaya",
    "Platano",
    "Fruta",
    "Frutillas",
    "Moras",
    "Cereza",
    "Cerezas",
    "Figs",
    "Naranja sanguina",
    "Pepino",
}

HERBS = {"Menta", "Romero", "Tomillo", "Lavanda", "Cilantro", "Wormwood"}

GARNISH = {
    "Aceituna",
    "Cascara de lima",
    "Cascara de limon",
    "Cascara de naranja",
    "Espiral de naranja",
    "Cereza marrasquino",
    "Oreo cookie",
    "Rosa",
    "Salmuera de aceituna",
}

CONDIMENTS = {
    "Aji en hojuelas",
    "Almond flavoring",
    "Asafoetida",
    "Cacao en polvo",
    "Canela",
    "Caramel coloring",
    "Cardamomo",
    "Chocolate",
    "Clavos de olor",
    "Extracto de vainilla",
    "Ginger",
    "Nuez moscada",
    "Pimienta",
    "Pimienta cayena",
    "Pimienta de Jamaica",
    "Pimienta negra",
    "Sal",
    "Sal de apio",
    "Salsa Worcestershire",
    "Salsa de soya",
    "Salsa picante",
    "Semilla de comino",
    "Tabasco sauce",
    "Vainilla",
}

DAIRY = {
    "Crema",
    "Crema batida",
    "Crema de coco",
    "Crema espesa",
    "Crema ligera",
    "Crema para batir",
    "Helado",
    "Helado de vainilla",
    "Hot Chocolate",
    "Leche",
    "Leche condensada",
    "Leche de coco",
    "Mantequilla",
    "Mitad crema mitad leche",
    "Yogur",
}

WINES = {"Champagne", "Jerez", "Oporto", "Oporto rubi", "Prosecco", "Vino", "Vino blanco", "Vino tinto"}

BEERS = {"Cerveza", "Cerveza de jengibre", "Cerveza de raiz", "Cerveza lager", "Corona", "Guinness stout", "Sarsaparilla", "Sidra", "Zima"}

MIXERS = {
    "7-Up",
    "Agua con gas",
    "Agua tonica",
    "Bebida",
    "Bebida de limon",
    "Bebida de uva",
    "Bebida lima-limon",
    "Club soda",
    "Coca-Cola",
    "Cola",
    "Dr. Pepper",
    "Fresca",
    "Ginger ale",
    "Jello",
    "Kool-Aid",
    "Limonada",
    "Mountain Dew",
    "Pepsi Cola",
    "Schweppes Russchian",
    "Soda",
    "Sprite",
    "Surge",
    "Te",
    "Te helado",
    "Cafe",
    "Cafe espresso",
}

SWEETENERS = {
    "Azucar",
    "Azucar demerara",
    "Azucar flor",
    "Azucar rubia",
    "Corn syrup",
    "Grenadine",
    "Miel",
    "Marshmallows",
}

JUICES = {
    "Cordial de flor de sauco",
    "Cordial de grosella negra",
    "Daiquiri mix",
    "Jugo de arandano",
    "Jugo de cereza",
    "Jugo de frutas",
    "Jugo de granada",
    "Jugo de lima",
    "Jugo de limon",
    "Jugo de manzana",
    "Jugo de maracuya",
    "Jugo de naranja",
    "Jugo de pinia",
    "Jugo de pomelo",
    "Jugo de tomate",
    "Jugo de uva",
    "Nectar de damasco",
    "Nectar de durazno",
    "Mezcla agridulce",
    "Mezcla sour",
    "Pina colada mix",
    "Ponche de frutas",
}

BITTERS = {"Amargo", "Amargo Peychaud", "Amargo de angostura", "Amargo de durazno", "Amargo de naranja"}


def category_for(name: str) -> str:
    if name in BASE:
        return BASE[name]
    if name in FRUITS:
        return "Frutas"
    if name in HERBS:
        return "Hierbas"
    if name in GARNISH:
        return "Garnish"
    if name in CONDIMENTS:
        return "Condimentos"
    if name in DAIRY:
        return "Cremas y lacteos"
    if name in WINES:
        return "Vinos y espumantes"
    if name in BEERS:
        return "Cervezas y fermentados"
    if name in MIXERS:
        return "Bebidas y mixers"
    if name in SWEETENERS or name.startswith("Jarabe de ") or name == "Jarabe simple":
        return "Endulzantes"
    if name in JUICES:
        return "Jugos y nectares"
    if name in BITTERS:
        return "Bitters"
    if name.startswith("Licor de ") or name.startswith("Crema de ") or name in {
        "Absenta", "Advocaat", "Amaretto", "Amaro Montenegro", "Anis", "Aniseta", "Aperol", "Apfelkorn",
        "Baileys crema irlandesa", "Benedictine", "Campari", "Chambord raspberry liqueur", "Cherry Heering",
        "Cointreau", "Crema irlandesa", "Curacao azul", "Curacao naranja", "Drambuie", "Dubonnet Rouge",
        "Falernum", "Frangelico", "Galliano", "Goldschlager", "Grand Marnier", "Green Chartreuse",
        "Jägermeister", "Kahlua", "Licor Godiva", "Lillet", "Lillet Blanc", "Ouzo", "Passoa", "Peachtree schnapps",
        "Pernod", "Pisang Ambon", "Ricard", "Sambuca", "Sambuca negra", "Schnapps de caramelo",
        "Schnapps de durazno", "Schnapps de frutilla", "Southern Comfort", "St. Germain", "Tia maria",
        "Triple sec", "Vermut", "Vermut dulce", "Vermut rojo", "Vermut seco", "Yellow Chartreuse",
    }:
        return "Licores y aperitivos"
    if name.startswith("Brandy de ") or name.startswith("Vodka de ") or name.startswith("Ron ") or name.startswith("Whisky ") or name in {
        "Aguardiente", "Alcohol de grano", "Applejack", "Bacardi Limon", "Brandy", "Cachaca", "Cognac",
        "Crown Royal", "Everclear", "Fireball", "Gin", "Jack Daniels", "Jim Beam", "Mezcal", "Pisco", "Ron",
        "Ron 151 grados", "Ron Malibu", "Scotch mezclado", "Scotch single malt", "Sloe gin", "Tequila",
        "Vodka", "Whiskey Bourbon", "Whisky", "Wild Turkey", "Whisky de Tennessee", "Whisky de centeno",
        "Whisky escoces", "Whisky irlandes", "Whisky mezclado", "Vodka Citron", "Vodka Kurant", "Vodka Pepper",
        "Yukon Jack",
    }:
        return "Destilados"
    return "Otros"


def main():
    store = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    changed = 0
    summary = {}
    for ingredient in store["ingredients"]:
      new_category = category_for(ingredient["name"])
      if ingredient.get("category") != new_category:
          ingredient["category"] = new_category
          changed += 1
      summary[new_category] = summary.get(new_category, 0) + 1
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")
    print("ingredientes actualizados:", changed)
    for key in sorted(summary):
        print(f"{key}: {summary[key]}")


if __name__ == "__main__":
    main()
