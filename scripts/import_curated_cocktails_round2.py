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
        "name": "Rebujito",
        "description": "Copa festiva andaluza de fino o manzanilla con soda lima-limon y menta.",
        "image_url": "https://wwv.sherry.wine/media/images/rebujito_homeweb.width-876.jpg",
        "prep_time_minutes": 3,
        "alcohol_level": "Suave",
        "glassware": "Vaso corto",
        "tags": ["espanol", "feria", "refrescante", "jerez"],
        "steps": ["Llena un vaso con hielo.", "Agrega el fino o la manzanilla.", "Completa con bebida lima-limon.", "Decora con menta y mezcla suavemente."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Fino", "category": "Vinos y espumantes"}, {"name": "Manzanilla", "category": "Vinos y espumantes"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Bebida lima-limon", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
            {"amount": "4", "unit": "hojas", "optional": True, "options": [{"name": "Menta", "category": "Hierbas"}]},
        ],
        "source": {"provider": "Sherry Wines / Jigger & Joy", "source_url": "https://www.sherry.wine/enjoying-sherry/sherry-cocktails/rebujito", "ingredients_text": ["Fino o manzanilla", "Bebida lima-limon", "Menta", "Hielo"]},
    },
    {
        "name": "Kalimotxo",
        "description": "Combinado vasco de vino tinto y cola, simple y muy frio.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Kalimotxo&mood=party&abv=6&method=Build&glass=Highball+Glass&spirit=wine&desc=The+Basque+Country%27s+beloved+red+wine+and+cola+combination%2C+a+youthful+party+drink+that+sounds+wrong+but+tastes+surprisi&tags=sweet%2Ccola%2Cfruity%2Crefreshing",
        "prep_time_minutes": 2,
        "alcohol_level": "Suave",
        "glassware": "Vaso highball",
        "tags": ["espanol", "vasco", "vino", "rapido"],
        "steps": ["Llena un vaso alto con hielo.", "Agrega el vino tinto.", "Completa con cola en partes iguales.", "Remueve suavemente y sirve muy frio."],
        "requirements": [
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Vino tinto", "category": "Vinos y espumantes"}]},
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Cola", "category": "Bebidas y mixers"}, {"name": "Coca-Cola", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Limon", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/kalimotxo", "ingredients_text": ["Vino tinto", "Cola", "Hielo", "Limon opcional"]},
    },
    {
        "name": "Tinto de verano",
        "description": "Refresco espanol de vino tinto con soda lima-limon.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Tinto+de+Verano&mood=chill&abv=6&method=Build&glass=Wine+Glass&spirit=wine&desc=Spain%27s+simple+summer+wine+cooler+mixing+red+wine+with+lemon-lime+soda%2C+served+ice-cold+on+terraces+across+the+country+a&tags=fruity%2Crefreshing%2Csweet%2Ceffervescent",
        "prep_time_minutes": 2,
        "alcohol_level": "Suave",
        "glassware": "Copa de vino",
        "tags": ["espanol", "verano", "vino", "refrescante"],
        "steps": ["Llena una copa o vaso con hielo.", "Agrega el vino tinto.", "Completa con bebida lima-limon.", "Decora con una rodaja de citrico y sirve de inmediato."],
        "requirements": [
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Vino tinto", "category": "Vinos y espumantes"}]},
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Bebida lima-limon", "category": "Bebidas y mixers"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}, {"name": "Limon", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/tinto-de-verano", "ingredients_text": ["Vino tinto", "Bebida lima-limon", "Hielo", "Naranja o limon"]},
    },
    {
        "name": "Carajillo",
        "description": "Combinado de Licor 43 y cafe espresso, muy popular en sobremesa.",
        "image_url": "https://www.garnishdrinks.com/cocktail/carajillo/opengraph-image",
        "prep_time_minutes": 4,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["espanol", "sobremesa", "cafe", "digestivo"],
        "steps": ["Llena una coctelera con hielo.", "Agrega el Licor 43 y el cafe espresso.", "Agita con fuerza hasta enfriar bien.", "Cuela sobre hielo fresco en un vaso bajo."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Licor 43", "category": "Licores y aperitivos"}]},
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Cafe espresso", "category": "Basicos"}, {"name": "Cafe", "category": "Basicos"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Garnish", "source_url": "https://www.garnishdrinks.com/cocktail/carajillo", "ingredients_text": ["Licor 43", "Cafe espresso", "Hielo"]},
    },
    {
        "name": "Cantarito",
        "description": "Coctel mexicano de tequila con mezcla de citricos y soda.",
        "image_url": "https://grancentenario.com/wp-content/uploads/2025/06/Cantarito-Cocktails-GC-2.jpg",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Tarro de barro",
        "tags": ["mexicano", "citrico", "tequila", "festivo"],
        "steps": ["Escarcha el borde del vaso con sal si deseas.", "Llena el vaso con hielo.", "Agrega tequila y los jugos citricos.", "Completa con soda o agua con gas y mezcla suavemente."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Tequila", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Jugo de pomelo", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de naranja", "category": "Jugos y nectares"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "top", "unit": "", "optional": False, "options": [{"name": "Agua con gas", "category": "Bebidas y mixers"}, {"name": "Soda", "category": "Bebidas y mixers"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Sal", "category": "Condimentos"}]},
        ],
        "source": {"provider": "Gran Centenario / Jigger & Joy", "source_url": "https://grancentenario.com/recipes/cantarito/", "ingredients_text": ["Tequila", "Jugo de pomelo", "Jugo de naranja", "Jugo de lima", "Soda"]},
    },
    {
        "name": "Batanga",
        "description": "Highball mexicano de tequila, cola y lima, tradicionalmente removido con cuchillo.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Batanga&mood=party&abv=11&method=Build&glass=Highball+Glass&spirit=tequila&desc=A+simple+Mexican+highball+of+tequila+and+cola+with+lime+stirred+with+a+knife.&tags=sweet+citrusy+refreshing",
        "prep_time_minutes": 3,
        "alcohol_level": "Medio",
        "glassware": "Vaso highball",
        "tags": ["mexicano", "tequila", "rapido", "clasico"],
        "steps": ["Escarcha el vaso con sal si deseas.", "Llena el vaso con hielo.", "Agrega tequila y jugo de lima.", "Completa con cola y mezcla suavemente."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Tequila", "category": "Destilados"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de lima", "category": "Jugos y nectares"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Cola", "category": "Bebidas y mixers"}, {"name": "Coca-Cola", "category": "Bebidas y mixers"}]},
            {"amount": "1", "unit": "pizca", "optional": True, "options": [{"name": "Sal", "category": "Condimentos"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/batanga", "ingredients_text": ["Tequila", "Jugo de lima", "Cola", "Sal opcional"]},
    },
    {
        "name": "Negroni Sbagliato",
        "description": "Variante italiana del Negroni en la que el gin se reemplaza por prosecco.",
        "image_url": "https://www.campariacademy.com/en-us/wp-content/uploads/sites/3/2022/11/2022_5oC_Negroni-Sbagliato_Low-Res.jpg",
        "prep_time_minutes": 3,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["italiano", "aperitivo", "amargo", "espumante"],
        "steps": ["Llena un vaso con hielo.", "Agrega Campari y vermut dulce.", "Completa con prosecco.", "Remueve suavemente y sirve con una rodaja de naranja si deseas."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Vermut dulce", "category": "Licores y aperitivos"}, {"name": "Vermut rojo", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Prosecco", "category": "Vinos y espumantes"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {"provider": "Campari Academy", "source_url": "https://www.campariacademy.com/en-us/training/recipes/negroni-sbagliato/", "ingredients_text": ["Campari", "Vermut dulce", "Prosecco"]},
    },
    {
        "name": "Garibaldi",
        "description": "Aperitivo italiano muy simple de Campari con jugo de naranja.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Garibaldi&mood=chill&abv=8&method=Build&glass=Highball+Glass&spirit=aperitif-wine&desc=A+two-ingredient+masterpiece+honoring+Italy%27s+unification+hero%2C+where+Campari%27s+northern+bitterness+embraces+Sicilian+or&tags=bitter+citrusy",
        "prep_time_minutes": 3,
        "alcohol_level": "Suave",
        "glassware": "Vaso highball",
        "tags": ["italiano", "aperitivo", "citrico", "campari"],
        "steps": ["Llena un vaso alto con hielo.", "Agrega Campari.", "Completa con jugo de naranja bien frio.", "Remueve suavemente y sirve de inmediato."],
        "requirements": [
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de naranja", "category": "Jugos y nectares"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/garibaldi", "ingredients_text": ["Campari", "Jugo de naranja", "Hielo"]},
    },
    {
        "name": "Hugo Spritz",
        "description": "Spritz alpino-floral popular en el norte de Italia con St-Germain, prosecco y menta.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Hugo+Spritz&mood=chill&abv=7&method=Build&glass=Wine+Glass&spirit=aperitif-wine&desc=South+Tyrol%27s+floral+answer+to+the+Aperol+Spritz%2C+this+contemporary+classic+brings+Alpine+meadow+freshness+to+the+Italia&tags=floral+minty+refreshing",
        "prep_time_minutes": 4,
        "alcohol_level": "Suave",
        "glassware": "Copa de vino",
        "tags": ["italiano", "spritz", "floral", "refrescante"],
        "steps": ["Llena una copa grande con hielo.", "Agrega St-Germain y prosecco.", "Completa con agua con gas.", "Decora con menta y una rodaja de lima."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "St. Germain", "category": "Licores y aperitivos"}]},
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Prosecco", "category": "Vinos y espumantes"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Agua con gas", "category": "Bebidas y mixers"}, {"name": "Soda", "category": "Bebidas y mixers"}]},
            {"amount": "4", "unit": "hojas", "optional": True, "options": [{"name": "Menta", "category": "Hierbas"}]},
            {"amount": "1", "unit": "rodaja", "optional": True, "options": [{"name": "Lima", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/hugo-spritz", "ingredients_text": ["St-Germain", "Prosecco", "Soda", "Menta", "Lima"]},
    },
    {
        "name": "Rossini",
        "description": "Version con frutillas del Bellini, muy asociada al aperitivo italiano.",
        "image_url": "https://www.prosecco.wine/wp-content/uploads/2023/10/ROSSINI.jpg",
        "prep_time_minutes": 5,
        "alcohol_level": "Suave",
        "glassware": "Copa flauta",
        "tags": ["italiano", "frutal", "espumante", "aperitivo"],
        "steps": ["Licua o macera las frutillas hasta obtener un pure.", "Coloca el pure en una copa flauta.", "Completa lentamente con prosecco bien frio.", "Mezcla apenas y sirve de inmediato."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Frutillas", "category": "Frutas"}]},
            {"amount": "3", "unit": "oz", "optional": False, "options": [{"name": "Prosecco", "category": "Vinos y espumantes"}]},
        ],
        "source": {"provider": "Consorzio Tutela Prosecco DOC / Jigger & Joy", "source_url": "https://www.prosecco.wine/en/recipe/rossini/", "ingredients_text": ["Frutillas", "Prosecco"]},
    },
    {
        "name": "Gancia Batido",
        "description": "Clasico argentino sencillo de Gancia, limon y un toque de azucar.",
        "image_url": "https://i.ytimg.com/vi/7qjBRt31Q6c/hqdefault.jpg",
        "prep_time_minutes": 3,
        "alcohol_level": "Suave",
        "glassware": "Vaso bajo",
        "tags": ["argentino", "aperitivo", "citrico", "clasico"],
        "steps": ["Llena un vaso con hielo.", "Agrega Gancia.", "Suma jugo de limon y una cucharadita de azucar.", "Mezcla bien hasta integrar y sirve."],
        "requirements": [
            {"amount": "2 1/2", "unit": "oz", "optional": False, "options": [{"name": "Gancia", "category": "Licores y aperitivos"}]},
            {"amount": "1/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "cdita", "optional": False, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Colegio de Camareros (YouTube)", "source_url": "https://www.youtube.com/watch?v=7qjBRt31Q6c", "ingredients_text": ["Gancia", "Jugo de limon", "Azucar", "Hielo"]},
    },
    {
        "name": "Paper Plane",
        "description": "Clasico contemporaneo estadounidense de bourbon, Aperol, Amaro Nonino y limon.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Paper+Plane&mood=bold&abv=24&method=Shake&glass=Coupe&spirit=bourbon&desc=A+perfectly+balanced+equal-parts+cocktail+with+bourbon+and+bitter+Italian+liqueurs&tags=bittersweet+and+citrusy",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["estadounidense", "moderno", "amargo", "citrico"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve sin garnish o con una pequena piel de limon si deseas."],
        "requirements": [
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Whiskey Bourbon", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Aperol", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Amaro Nonino", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/paper-plane", "ingredients_text": ["Whiskey bourbon", "Aperol", "Amaro Nonino", "Jugo de limon"]},
    },
    {
        "name": "Boulevardier",
        "description": "Pariente del Negroni con bourbon en lugar de gin.",
        "image_url": "https://www.campariacademy.com/en-us/wp-content/uploads/sites/3/2022/07/Campari-Boulevardier-Cocktail-Image-1.jpg",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Vaso bajo",
        "tags": ["estadounidense", "clasico", "amargo", "whiskey"],
        "steps": ["Agrega bourbon, Campari y vermut dulce a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela sobre un vaso bajo con hielo grande.", "Decora con piel de naranja si deseas."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Whiskey Bourbon", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Campari", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Vermut dulce", "category": "Licores y aperitivos"}, {"name": "Vermut rojo", "category": "Licores y aperitivos"}]},
            {"amount": "1", "unit": "twist", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {"provider": "Campari Academy", "source_url": "https://www.campariacademy.com/en-us/training/recipes/boulevardier-2/", "ingredients_text": ["Whiskey bourbon", "Campari", "Vermut dulce"]},
    },
    {
        "name": "Between the Sheets",
        "description": "Coctel franco-estadounidense de cognac, ron blanco, triple sec y limon.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Between+the+Sheets&mood=cozy&abv=28&method=Shake&glass=Coupe&spirit=cognac&desc=A+bold+combination+of+cognac+and+rum+with+citrus&tags=citrusy+and+strong",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["frances", "clasico", "citrico", "fuerte"],
        "steps": ["Agrega todos los ingredientes a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en una copa coupe fria.", "Sirve sin garnish o con piel de naranja si deseas."],
        "requirements": [
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Cognac", "category": "Destilados"}, {"name": "Brandy", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Ron blanco", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Triple sec", "category": "Licores y aperitivos"}, {"name": "Cointreau", "category": "Licores y aperitivos"}]},
            {"amount": "1/2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/between-the-sheets", "ingredients_text": ["Cognac", "Ron blanco", "Triple sec", "Jugo de limon"]},
    },
    {
        "name": "Alsterwasser",
        "description": "Shandy aleman mitad cerveza y mitad limonada.",
        "image_url": "https://vintageamericancocktails.com/wp-content/uploads/2022/06/shandy_german.jpg",
        "prep_time_minutes": 2,
        "alcohol_level": "Suave",
        "glassware": "Vaso pinta",
        "tags": ["aleman", "cerveza", "refrescante", "verano"],
        "steps": ["Llena medio vaso con limonada bien fria.", "Completa el resto con cerveza lager.", "Mezcla suavemente sin perder gas.", "Sirve de inmediato."],
        "requirements": [
            {"amount": "8", "unit": "oz", "optional": False, "options": [{"name": "Cerveza lager", "category": "Cervezas y fermentados"}, {"name": "Cerveza", "category": "Cervezas y fermentados"}]},
            {"amount": "8", "unit": "oz", "optional": False, "options": [{"name": "Limonada", "category": "Bebidas y mixers"}]},
        ],
        "source": {"provider": "Vintage American Cocktails", "source_url": "https://vintageamericancocktails.com/alsterwasser-german-shandy/", "ingredients_text": ["Cerveza lager", "Limonada"]},
    },
    {
        "name": "Pimm's Cup",
        "description": "Copa inglesa veraniega con Pimm's y limonada, servida con frutas y pepino.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Pimm%27s+Cup&mood=chill&abv=7&method=Build&glass=Highball+Glass&spirit=fruit-liqueur&desc=A+refreshing+British+summer+drink+with+Pimm%27s+and+lemonade.&tags=herbal+refreshing",
        "prep_time_minutes": 4,
        "alcohol_level": "Suave",
        "glassware": "Vaso highball",
        "tags": ["ingles", "verano", "refrescante", "jardin"],
        "steps": ["Llena un vaso alto con hielo.", "Agrega Pimm's No. 1.", "Completa con limonada.", "Decora con pepino, menta y fruta fresca."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pimm's No. 1", "category": "Licores y aperitivos"}]},
            {"amount": "4", "unit": "oz", "optional": False, "options": [{"name": "Limonada", "category": "Bebidas y mixers"}]},
            {"amount": "2", "unit": "rodajas", "optional": True, "options": [{"name": "Pepino", "category": "Frutas"}]},
            {"amount": "4", "unit": "hojas", "optional": True, "options": [{"name": "Menta", "category": "Hierbas"}]},
            {"amount": "2", "unit": "unidades", "optional": True, "options": [{"name": "Frutillas", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/pimms-cup", "ingredients_text": ["Pimm's No. 1", "Limonada", "Pepino", "Menta", "Frutillas"]},
    },
    {
        "name": "Corpse Reviver #2",
        "description": "Clasico ingles del Savoy con gin, Lillet Blanc, Cointreau, limon y absenta.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Corpse+Reviver+%232&mood=crisp&abv=24&method=Shake&glass=Coupe&spirit=gin&desc=The+legendary+Savoy+hangover+cure+with+gin%2C+Lillet%2C+Cointreau%2C+lemon%2C+and+a+whisper+of+absinthe.&tags=citrus%2Cfloral%2Cherbal%2Cbright",
        "prep_time_minutes": 5,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["ingles", "clasico", "citrico", "savoy"],
        "steps": ["Enjuaga una copa coupe fria con una pequena cantidad de absenta y desecha el exceso.", "Agrega gin, Lillet Blanc, Cointreau y jugo de limon a una coctelera con hielo.", "Agita con fuerza hasta enfriar bien.", "Cuela en la copa preparada."],
        "requirements": [
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Gin", "category": "Destilados"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Lillet Blanc", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Cointreau", "category": "Licores y aperitivos"}]},
            {"amount": "3/4", "unit": "oz", "optional": False, "options": [{"name": "Jugo de limon", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "dash", "optional": True, "options": [{"name": "Absenta", "category": "Licores y aperitivos"}]},
        ],
        "source": {"provider": "Jigger & Joy / Cointreau", "source_url": "https://jiggerandjoy.com/drinks/corpse-reviver-2", "ingredients_text": ["Gin", "Lillet Blanc", "Cointreau", "Jugo de limon", "Absenta"]},
    },
    {
        "name": "Batida",
        "description": "Coctel brasileno cremoso, aqui en version de maracuya con cachaca y leche de coco.",
        "image_url": "https://www.garnishdrinks.com/cocktail/batida/opengraph-image",
        "prep_time_minutes": 5,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["brasileno", "tropical", "cremoso", "cachaca"],
        "steps": ["Agrega todos los ingredientes a una licuadora con hielo.", "Licua hasta obtener una textura cremosa.", "Sirve en un vaso bajo o copa fria.", "Decora con fruta tropical si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Cachaca", "category": "Destilados"}]},
            {"amount": "1 1/2", "unit": "oz", "optional": False, "options": [{"name": "Leche de coco", "category": "Cremas y lacteos"}]},
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Jugo de maracuya", "category": "Jugos y nectares"}]},
            {"amount": "1", "unit": "cda", "optional": True, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "al gusto", "unit": "", "optional": True, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Garnish", "source_url": "https://www.garnishdrinks.com/cocktail/batida", "ingredients_text": ["Cachaca", "Leche de coco", "Jugo de maracuya", "Azucar"]},
    },
    {
        "name": "Caipiroska",
        "description": "Version con vodka de la caipirinha, muy popular en cocteleria moderna.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=Caipiroska&mood=tropical&abv=18&method=Muddle&glass=Rocks+Glass&spirit=vodka&desc=The+vodka+sibling+of+Brazil%27s+national+cocktail%E2%80%94muddled+lime+and+sugar+with+vodka+creating+a+bracingly+fresh%2C+citrus-for&tags=citrus%2Crefreshing%2Clime%2Csweet-tart",
        "prep_time_minutes": 4,
        "alcohol_level": "Medio",
        "glassware": "Vaso bajo",
        "tags": ["brasileno", "vodka", "citrico", "refrescante"],
        "steps": ["Coloca los trozos de lima y el azucar en un vaso bajo.", "Machaca suavemente para liberar el jugo sin amargar demasiado.", "Agrega hielo y vodka.", "Mezcla bien y sirve."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Vodka", "category": "Destilados"}]},
            {"amount": "1", "unit": "unidad", "optional": False, "options": [{"name": "Lima", "category": "Frutas"}]},
            {"amount": "2", "unit": "cditas", "optional": False, "options": [{"name": "Azucar", "category": "Endulzantes"}]},
            {"amount": "al gusto", "unit": "", "optional": False, "options": [{"name": "Hielo", "category": "Basicos"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/caipiroska", "ingredients_text": ["Vodka", "Lima", "Azucar", "Hielo"]},
    },
    {
        "name": "El Capitan",
        "description": "Coctel peruano elegante de pisco, vermut dulce y bitters.",
        "image_url": "https://jiggerandjoy.com/api/og/drink?name=El+Capitan&mood=bold&abv=28&method=Stir&glass=Coupe&spirit=pisco&desc=Peru%27s+sophisticated+answer+to+the+Manhattan%2C+pairing+aromatic+pisco+with+sweet+vermouth+and+Angostura+bitters%2C+garnishe&tags=herbal%2Cbittersweet%2Cgrape%2Caromatic",
        "prep_time_minutes": 4,
        "alcohol_level": "Fuerte",
        "glassware": "Copa coupe",
        "tags": ["peruano", "clasico", "pisco", "aromatico"],
        "steps": ["Agrega pisco, vermut dulce y bitters a un vaso mezclador con hielo.", "Revuelve hasta enfriar bien.", "Cuela en una copa coupe fria.", "Decora con una piel de naranja si deseas."],
        "requirements": [
            {"amount": "2", "unit": "oz", "optional": False, "options": [{"name": "Pisco", "category": "Destilados"}]},
            {"amount": "1", "unit": "oz", "optional": False, "options": [{"name": "Vermut dulce", "category": "Licores y aperitivos"}, {"name": "Vermut rojo", "category": "Licores y aperitivos"}]},
            {"amount": "2", "unit": "gotas", "optional": True, "options": [{"name": "Amargo de angostura", "category": "Bitters"}]},
            {"amount": "1", "unit": "twist", "optional": True, "options": [{"name": "Naranja", "category": "Frutas"}]},
        ],
        "source": {"provider": "Jigger & Joy", "source_url": "https://jiggerandjoy.com/drinks/el-capitan", "ingredients_text": ["Pisco", "Vermut dulce", "Amargo de angostura"]},
    },
]


def normalized(value):
    ascii_value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.lower().split())


def next_id(items):
    return max((item["id"] for item in items), default=0) + 1


def backup_store():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"store-before-curated-round2-{time.strftime('%Y%m%d-%H%M%S')}.json"
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
                "instructions": "\\n".join(f"{index}. {instruction}" for index, instruction in enumerate(cocktail["steps"], start=1)),
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
