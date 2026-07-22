# Cocktail Bar Manager

Aplicacion web local para administrar ingredientes, cocteles y una carta publica para invitados.

## Incluye

- Inventario de ingredientes disponibles y por comprar
- Catalogo de cocteles con foto, pasos, tags, rating y favorito
- Reglas de ingredientes obligatorios, opcionales y reemplazables
- Listas especiales para mostrar en la carta publica
- Vista administrador protegida por clave
- Vista publica pensada para abrir desde un QR fijo

## Ejecutar

```powershell
python server.py
```

Tambien puedes usar:

```powershell
.\start-local.ps1
```

Luego abre:

- Carta publica: `http://127.0.0.1:8000/`
- Administracion: `http://127.0.0.1:8000/a`

## Publicarlo en internet

La forma mas simple para dejar la carta accesible desde fuera de tu red es desplegar esta app en un hosting publico.

### Opcion recomendada: Render

1. Sube esta carpeta a un repositorio en GitHub.
2. En Render crea un nuevo servicio web desde ese repo.
3. Render detectara `render.yaml` y levantara la app con `python main.py`.
4. La carta quedara disponible en una URL publica tipo `https://tu-app.onrender.com/`
5. Si quieres un QR mas pequeno, despues puedes conectar un dominio corto y usar algo como `https://bar.tudominio.cl/`

### Endpoints utiles para produccion

- Carta publica corta: `/m`
- Administracion corta: `/a`
- Healthcheck: `/healthz`

## Persistencia en produccion (obligatorio en Render plan free)

El plan free de Render **no tiene disco persistente**: cuando el servicio queda inactivo unos minutos,
Render lo duerme y al despertar levanta un contenedor nuevo desde el ultimo deploy, perdiendo cualquier
cambio hecho en `data/store.json` en tiempo real (favoritos, ratings, inventario, cocteles nuevos desde el
admin, etc.). Por eso los cambios "se deshacian" despues de un rato.

La app soporta guardar el estado en **Upstash Redis** (capa gratuita permanente) en vez del disco local.
Si las variables de entorno de Upstash no estan configuradas, sigue funcionando exactamente igual que antes
(solo `data/store.json` local) — asi que esto no rompe el uso local para desarrollo.

### Configurarlo (una sola vez)

1. Crea una cuenta gratis en [upstash.com](https://upstash.com) (no pide tarjeta).
2. Crea una base de datos Redis nueva (cualquier region cercana a donde este tu servicio de Render).
3. En el dashboard de esa base, entra a la pestaña **REST API** y copia dos valores:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
4. En Render, entra a tu servicio &rarr; pestaña **Environment** &rarr; agrega esas dos variables con esos valores.
5. Guarda: Render va a redesplegar solo. En el primer arranque con esas variables presentes, la app copia
   automaticamente todo lo que hoy esta en `data/store.json` (el catalogo completo) hacia Upstash, asi que
   no se pierde nada en la migracion. De ahi en adelante, todo cambio hecho desde el admin queda guardado
   en Upstash y sobrevive a que Render duerma y despierte el servicio.

## Prueba publica con Cloudflare

Para probar la carta desde fuera de tu red sin desplegarla aun:

1. Instala `cloudflared` en Windows desde la documentacion oficial de Cloudflare:
   [Cloudflare Tunnel downloads](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/)
2. Guarda el ejecutable como `tools/cloudflared.exe`
3. Levanta la app local:

```powershell
.\start-local.ps1
```

4. En otra terminal, crea un Quick Tunnel:

```powershell
.\start-cloudflare-quick.ps1
```

5. Cloudflare te devolvera una URL publica temporal tipo `https://algo.trycloudflare.com`
6. Tu carta publica sera esa URL raiz.

Ejemplo:

```text
https://algo.trycloudflare.com/
```

Notas:

- Esta URL es temporal, ideal para pruebas.
- Tu computador debe quedar encendido mientras uses el tunel.
- Cuando demos el paso a produccion, convendra usar un tunel nombrado con dominio propio.

## Importacion automatica de cocteles

Deje un importador inicial desde TheCocktailDB en:

- [import_thecocktaildb.py](C:/Users/cristian.diazc/OneDrive%20-%20Enex/Escritorio/Entra%C3%B1a/Cocktail/import_thecocktaildb.py)

Uso:

```powershell
python .\import_thecocktaildb.py
```

Si quieres reemplazar por completo el catalogo de cocteles antes de importar:

```powershell
python .\import_thecocktaildb.py --replace-catalog
```

Notas de esta importacion:

- Importa nombre, foto, instrucciones y lista de ingredientes desde TheCocktailDB.
- Convierte las instrucciones en pasos automaticamente.
- Agrega ingredientes nuevos al catalogo local si no existen.
- Hace backup de `data/store.json` antes de escribir.
- Conserva inventario y lista de compras.
- Marca estos cocteles con el tag `thecocktaildb`.
- Los ingredientes quedan importados como obligatorios por defecto.

Limitaciones actuales:

- No existe una fuente unica y perfecta con "todos los cocteles del mundo".
- TheCocktailDB publica una base crowd-sourced y su API gratuita documenta busqueda por letra y detalle por id.
- La API gratuita no expone toda la semantica que tu app quiere, como ingredientes opcionales o reemplazables; eso todavia requiere curacion manual o reglas propias.

## Acceso administrador

- Clave inicial: `admin123`

## Notas

- La base se crea automaticamente en `data/store.json`
- Las fotos se manejan por URL en esta primera version
- El catalogo parte con datos semilla para probar la logica de disponibilidad
- La alta rapida del panel crea la ficha inicial del coctel; el detalle completo de ingredientes, reemplazos, pasos y tags hoy se edita en `data/store.json`
- El servidor escucha en toda la red local, asi que otros celulares en el mismo Wi-Fi pueden entrar usando `http://TU-IP-LOCAL:8000/m`
- Para un QR mas pequeno conviene usar la ruta raiz `/`; si despues publicas esto en un dominio corto, el QR quedara aun mas simple
- Si despliegas en Render con el plan free, configura Upstash Redis (ver seccion "Persistencia en produccion" arriba) o los cambios del admin se perderan cuando el servicio duerma
