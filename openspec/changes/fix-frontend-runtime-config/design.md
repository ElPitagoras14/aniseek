## Context

El frontend se distribuye como una imagen pre-construida en GHCR: el `dist/` que sirve nginx se compiló en CI, mucho antes de que alguien decida el valor de `API_URL` o `AUTH_ENABLED`. Por eso existe `/config.js`, un archivo que `entrypoint.sh` escribe con `envsubst` a partir de `config.template.js` en cada arranque del container, y que `index.html` carga de forma síncrona en el `<head>` antes del bundle.

`src/config.ts` consume ese archivo como la primera de tres capas: runtime (`window.__APP_CONFIG__`), build-time (`define` de Vite alimentado por `loadEnv`) y un default literal.

El estado actual y sus dos defectos están documentados en `proposal.md`. Para el diseño interesan sobre todo las restricciones que los rodean:

- **La entrega ya está resuelta.** `remove-pwa` eliminó el service worker que precacheaba `/config.js` y anulaba el `Cache-Control: no-store` de `nginx.conf`. La capability `frontend-delivery` ya especifica que ese archivo llega fresco en cada carga. Este diseño puede darlo por sentado y ocuparse solo de cómo se interpreta su contenido.
- **Windows es plataforma de desarrollo soportada.** `envsubst` viene de gettext y no está disponible en Git for Windows, así que el mecanismo del container no se puede reutilizar tal cual en desarrollo local.
- **`nginx.conf` ya proxea `/api/` al backend.** Por eso `API_URL` vacío es un valor legítimo y no un error: significa mismo origen.

## Goals / Non-Goals

**Goals:**

- Que `config.js` se produzca por un solo mecanismo conceptual en Docker y en desarrollo local, con la forma del archivo definida en un único lugar.
- Que desarrollo local respete el `.env` de la raíz, que hoy carga pero no llega a usar.
- Que un `AUTH_ENABLED` ausente o vacío nunca resulte en autenticación desactivada.
- Que la precedencia entre capas sea legible y esté escrita una sola vez.

**Non-Goals:**

- El drift de `.env.example` (`POSTGRES_PORT`/`REDIS_PORT` sin consumidores, `DB_URL` al puerto 4003, `compose.dev.yaml` ignorando `.env`). Es un change aparte.
- Cambiar la semántica de `API_URL` o el proxy `/api/` de nginx.
- Cualquier cosa relativa a caching o entrega de `/config.js`: es responsabilidad de `frontend-delivery` y ya está resuelto.

## Decisions

### D1 — `public/config.js` sale del control de versiones

El archivo cumple dos roles incompatibles: placeholder para que `pnpm dev` no dé 404, y artefacto de runtime servido en producción. Mientras esté commiteado, en desarrollo tapa las capas 2 y 3 de `src/config.ts`.

Se elimina del repo y se agrega a `.gitignore` de la raíz.

*Alcance real de esta decisión, ahora que no hay service worker:* el único daño que quedaba era el de desarrollo local. En producción `entrypoint.sh` sobreescribe el archivo en cada arranque, así que el placeholder nunca se sirve. Antes de `remove-pwa` esta decisión además sacaba `config.js` del precache manifest de Workbox; ese motivo ya no aplica.

*Alternativa considerada:* tratar `""` como no configurado de forma global en `config.ts` sin tocar el archivo. No sirve: `API_URL: ""` es un valor legítimo y no se puede distinguir del placeholder.

### D2 — En desarrollo, `/config.js` lo sirve un middleware de Vite, no un archivo

Se agrega un plugin local que, vía `configureServer`, intercepta `/config.js` y responde con el contenido generado a partir de `config.template.js`, sustituyendo los `${VAR}` con las variables que Vite ya carga del `.env` de la raíz.

Dos consecuencias buscadas: en desarrollo no existe ningún `config.js` en disco que pueda volver a colarse al repo o al build, y el archivo se regenera en cada request, así que cambiar el `.env` y recargar alcanza.

*Alternativas consideradas:* escribir físicamente `public/config.js` desde un script `predev` obliga a mantenerlo gitignoreado y a recordar regenerarlo al cambiar el `.env`. Reutilizar `envsubst` mediante una dependencia npm agrega una dependencia para algo que son tres líneas de Node, y fue lo primero que se descartó por el requisito de Windows.

### D3 — La forma del config se define una sola vez, en `config.template.js`

Tanto `entrypoint.sh` como el plugin de D2 leen el mismo `config.template.js` y sustituyen `${VAR}`. En el container lo hace `envsubst`; en desarrollo lo hace Node. El mecanismo de sustitución difiere por plataforma, pero la plantilla —qué claves existen y cómo se llaman— vive en un único archivo commiteado.

Agregar una variable de configuración en el futuro debe requerir editar `config.template.js` y nada más del lado del frontend.

### D4 — `""` es "no configurado" para `AUTH_ENABLED`, pero sí es valor para `API_URL`

No hay una regla global correcta: para `API_URL`, `""` significa "mismo origen" y es el valor por defecto esperado en Docker; para un flag booleano, `""` no es un booleano.

La decisión es no buscar una regla única sino **un parser por clave**: cada variable declara cómo se interpreta un valor crudo y qué cuenta como ausente. `API_URL` acepta cualquier string, incluido el vacío. `AUTH_ENABLED` acepta `"true"`/`"false"` (case-insensitive) y trata cualquier otra cosa, incluido `""`, como ausente.

*Alternativa considerada:* normalizar `""` a `undefined` de forma global es más simple de escribir pero rompe el default de `API_URL`, que pasaría a resolverse por la capa de build-time en vez de quedar en mismo origen.

### D5 — El default final de `isAuthEnabled` pasa de `false` a `true`

Hoy, cuando ninguna capa aporta un valor, `isAuthEnabled` resuelve a `false`. Eso hace que D4 sea insuficiente por sí solo: tratar `""` como ausente solo mueve el problema una capa más abajo, donde el resultado sigue siendo "sin login".

El backend ya default-ea a `True` (`AuthSettings.AUTH_ENABLED`). Alinear el frontend elimina el modo roto en que la pantalla de login desaparece mientras la API rechaza todos los requests, y hace que la ausencia de configuración falle cerrado en ambos lados.

Desactivar la autenticación pasa a requerir un `AUTH_ENABLED=false` explícito, que es el contrato que el README ya describe.

### D6 — El refactor de `config.ts` separa selección de capa y parseo

La precedencia se escribe una vez, como una lista ordenada de valores candidatos, y el parseo de cada clave se aplica al resultado. Hoy la misma decisión está escrita dos veces con dos formas distintas (`!== undefined` en una rama, `typeof !== "undefined"` en la otra) y cada rama coerciona a su manera.

Forma esperada, sin comprometer la implementación exacta:

```
resolve(clave) = primer valor "presente" entre [ runtime, build-time ]  →  parser(clave)
                 si ninguno está presente                                →  default(clave)
```

*Alternativa considerada:* aplanar los ternarios anidados sin introducir el helper deja el código más corto pero sigue repitiendo la precedencia por cada variable, que es exactamente donde se escondió el defecto de `""`.

### D7 — `config.template.js` sale de `public/` y deja de servirse

Hoy la plantilla vive en `frontend/public/`, así que Vite la copia a `dist/` y nginx la publica: `GET /config.template.js` devuelve `200` con los `${API_URL}` sin sustituir. No expone secretos —solo nombres de variables— pero es un insumo de build servido como asset web.

Es el mismo error de categoría que D1 corrige para `config.js`: un archivo que no es un asset del sitio viviendo en el directorio de assets del sitio. Corregir uno y dejar el otro sería incoherente, y mientras la plantilla siga en `public/` cualquier clave de configuración que se agregue en el futuro se publica sola.

Se mueve a `frontend/config.template.js`, fuera de `public/`, y el `COPY` del `Dockerfile` la deposita en una ruta **fuera del directorio servido** por nginx. `entrypoint.sh` la lee desde ahí y sigue escribiendo `config.js` dentro del directorio servido. El plugin de D2 la lee desde la raíz de `frontend/`.

Esta decisión resuelve de una sola vez las dos preguntas que estaban abiertas. El `COPY` explícito del `Dockerfile` es redundante hoy —Vite ya deposita la plantilla en `dist/`, y la línea anterior copia todo `dist/` al mismo destino— pero deja de serlo al sacarla de `public/`: pasa a ser la única vía por la que la plantilla llega al container. Resulta ser el mecanismo correcto apuntando al destino equivocado, no un residuo.

Tras este cambio, `public/` vuelve a contener únicamente assets reales del sitio.

*Alternativa considerada:* dejar la plantilla en `public/` y borrar el `COPY` redundante. Es una línea menos en vez de un archivo movido, pero conserva la publicación de la plantilla y el error de categoría. La simplicidad aparente sale de no arreglar el problema.

## Risks / Trade-offs

- **El plugin de desarrollo y `entrypoint.sh` pueden divergir con el tiempo.** → Mitigado por D3: ambos derivan de `config.template.js`. El riesgo residual es que difieran en el manejo de una variable ausente (`envsubst` la sustituye por `""`; el plugin debe hacer lo mismo para que los dos modos coincidan).

- **`vite preview` sirve `dist/`, donde no habrá `config.js` ni middleware.** → Dará 404 y la app caerá a las capas de build-time. Es coherente y no rompe nada, pero conviene saberlo antes de usar `preview` para reproducir un bug de configuración.

- **D5 cambia el comportamiento observable de un despliegue mal configurado.** → Una instalación que hoy funciona sin login porque nunca definió `AUTH_ENABLED` empezará a pedir credenciales tras actualizar. Es el comportamiento correcto y coincide con lo que el backend siempre exigió, pero debe anunciarse en las notas de versión.

- **Quitar `public/config.js` deja un 404 en desarrollo si el plugin de D2 falla o no se registra.** → El fallo es silencioso y benigno en apariencia: la app cae a las capas de build-time y sigue funcionando, lo que puede enmascarar que el middleware no está corriendo. Conviene que el plugin falle ruidosamente al arrancar si no puede leer `config.template.js`.

## Migration Plan

1. Aplicar los cambios de `vite.config.ts` (D2) y `src/config.ts` (D4, D5, D6) juntos. Separarlos deja ventanas donde la generación está arreglada pero la resolución no, o al revés.
2. Sacar `public/config.js` con `git rm --cached` y agregarlo a `.gitignore` de la raíz en el mismo commit.
3. Verificar en desarrollo que `AUTH_ENABLED=false` en el `.env` de la raíz apaga la pantalla de login, que es la comprobación directa del defecto 1.
4. Verificar que el `dist/` construido no contiene `config.js` y que el container lo sigue generando en el arranque.

**Rollback:** revertir el commit y reconstruir. No hay estado persistido ni migración de datos. Lo único que no se revierte solo es un `.env` que se haya empezado a apoyar en el default de D5; conviene definir `AUTH_ENABLED` explícitamente al desplegar este change para que el rollback sea neutral.

## Open Questions

Ninguna abierta. Las dos que había se resolvieron juntas en D7, porque estaban acopladas:

- **¿El `COPY` de `config.template.js` en el `Dockerfile` es un residuo?** Resuelto: es redundante hoy —se verificó que Vite ya copia la plantilla a `dist/`, y la línea anterior lleva todo `dist/` al mismo destino— pero deja de serlo al sacar la plantilla de `public/`. Se conserva, apuntando a una ruta fuera del directorio servido.
- **¿Conviene excluir `config.template.js` del `dist/`?** Resuelto: sí. Se verificó que hoy es alcanzable desde el navegador (`GET /config.template.js` → `200`). Sacarla de `public/` la excluye del `dist/` sin necesidad de configurar exclusiones en el build.
