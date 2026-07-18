import json
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = ROOT / "data" / "store.json"


def load_store():
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save_store(store):
    STORE_PATH.write_text(json.dumps(store, ensure_ascii=True, indent=2), encoding="utf-8")


def normalize_glass(glass):
    mapping = {
        "Cocktail glass": "Copa de coctel",
        "Highball glass": "Vaso highball",
        "Old-fashioned glass": "Vaso old fashioned",
        "Old-Fashioned glass": "Vaso old fashioned",
        "Collins glass": "Vaso collins",
        "Champagne flute": "Copa flauta",
        "Whiskey sour glass": "Copa sour",
        "Shot glass": "Vaso de shot",
        "Coffee mug": "Taza",
        "Hurricane glass": "Copa hurricane",
        "Margarita glass": "Copa margarita",
        "Martini Glass": "Copa martini",
        "Martini glass": "Copa martini",
        "Pint glass": "Vaso pinta",
        "Copper Mug": "Mug de cobre",
        "Copper mug": "Mug de cobre",
        "Beer mug": "Jarro cervecero",
        "Beer pilsner": "Vaso pilsner",
        "Pousse cafe glass": "Copa pousse cafe",
        "Punch bowl": "Ponchera",
        "Pitcher": "Jarra",
        "Mason jar": "Frasco mason",
        "Wine Glass": "Copa de vino",
        "Wine glass": "Copa de vino",
        "White wine glass": "Copa de vino blanco",
        "Brandy snifter": "Copa balón",
        "Balloon Glass": "Copa balón",
        "Balloon glass": "Copa balón",
        "Parfait glass": "Copa parfait",
        "Irish coffee cup": "Copa irlandesa",
        "Jar": "Jarra",
    }
    return mapping.get((glass or "").strip(), (glass or "").strip())


def infer_glassware(cocktail):
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
    if "copa flauta" in text or "champagne flute" in text:
        return "Copa flauta"
    if "copa martini" in text or "martini glass" in text:
        return "Copa martini"
    if "copa margarita" in text or "margarita glass" in text:
        return "Copa margarita"
    if "copa de vino" in text or "wine glass" in text:
        return "Copa de vino"
    if "copa de coctel" in text or "cocktail glass" in text:
        return "Copa de coctel"
    if "taza" in text or "mug" in text:
        return "Taza"
    return ""


def fetch_glass(source_id):
    url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={source_id}"
    data = json.load(urllib.request.urlopen(url, timeout=15))
    drinks = data.get("drinks") or []
    if not drinks:
        return ""
    return normalize_glass(drinks[0].get("strGlass", ""))


def main():
    store = load_store()
    inferred = 0
    fetched = 0
    failures = []

    for cocktail in store["cocktails"]:
        if cocktail.get("glassware"):
            continue
        inferred_value = infer_glassware(cocktail)
        if inferred_value:
            cocktail["glassware"] = inferred_value
            inferred += 1

    save_store(store)

    for index, cocktail in enumerate(store["cocktails"], start=1):
        if cocktail.get("glassware"):
            continue
        source = cocktail.get("source") or {}
        source_id = source.get("source_id")
        if not source_id:
            continue
        try:
            glass = fetch_glass(source_id)
            if glass:
                cocktail["glassware"] = glass
                fetched += 1
            if index % 25 == 0:
                save_store(store)
            time.sleep(0.15)
        except Exception as exc:
            failures.append((cocktail.get("name"), str(exc)))
            save_store(store)

    if not next((c for c in store["cocktails"] if c["name"] == "Whisky Cola"), None).get("glassware"):
        next(c for c in store["cocktails"] if c["name"] == "Whisky Cola")["glassware"] = "Vaso highball"
    if not next((c for c in store["cocktails"] if c["name"] == "Virgin Fizz"), None).get("glassware"):
        next(c for c in store["cocktails"] if c["name"] == "Virgin Fizz")["glassware"] = "Vaso highball"

    save_store(store)
    print("inferidos:", inferred)
    print("consultados:", fetched)
    print("sin resolver:", sum(1 for c in store["cocktails"] if not c.get("glassware")))
    print("fallos:", len(failures))
    for name, error in failures[:20]:
        print(name, error)


if __name__ == "__main__":
    main()
