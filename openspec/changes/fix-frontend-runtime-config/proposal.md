## Why

El frontend resuelve `API_URL` y `AUTH_ENABLED` en runtime a través de `/config.js`, un archivo que `entrypoint.sh` escribe al arrancar el container para que una sola imagen pre-construida en GHCR sirva cualquier despliegue. El mecanismo de entrega ya funciona —`remove-pwa` eliminó el service worker que lo anulaba, y `nginx.conf` sirve `/config.js` con `Cache-Control: no-store`—, pero la resolución de esos valores dentro de la aplicación tiene dos defectos:

1. **El placeholder commiteado tapa el fallback de build-time en desarrollo local.** `src/config.ts` apila runtime config sobre un `define` de Vite sobre un default, y el orden es correcto. Pero `frontend/public/config.js` está commiteado, así que en desarrollo Vite lo sirve y la capa 1 siempre resuelve (`API_URL: ""` no es `undefined`), dejando las capas 2 y 3 inalcanzables. `vite.config.ts` ya carga el `.env` de la raíz (`envDir: ".."`, `loadEnv(mode, "..", "")`), y aun así `AUTH_ENABLED=false` en `.env` no puede apagar la pantalla de login en desarrollo local — el placeholder fija `AUTH_ENABLED: true`.

2. **Un `AUTH_ENABLED` ausente falla abierto en el frontend y cerrado en el backend.** Si la variable falta en `.env`, `compose.yaml` pasa un valor vacío, `envsubst` escribe `AUTH_ENABLED: ""`, y `src/config.ts` acepta `""` como valor definido porque solo compara contra `undefined` — resolviendo a `false`. El backend, en cambio, tiene default `True` (`AuthSettings.AUTH_ENABLED`). La aplicación entonces esconde la pantalla de login mientras la API rechaza todos los requests.

Los dos comparten una misma raíz: un archivo que cumple dos roles incompatibles a la vez —placeholder de desarrollo y artefacto de runtime—, y "vacío" tratado como "definido". El defecto 2, además, pasó desapercibido porque la resolución de las tres capas está escrita como ternarios anidados que mezclan en una sola expresión la elección de capa con la coerción del valor.

## What Changes

- Dejar de commitear `frontend/public/config.js`. `config.template.js` pasa a ser la única fuente de la forma del archivo de configuración; el `config.js` concreto siempre se genera, nunca se guarda.
- Sacar `config.template.js` de `public/`. Hoy se sirve al navegador como cualquier otro asset —`GET /config.template.js` devuelve `200` con los `${VAR}` sin sustituir—, cuando es un insumo de build y no un recurso del sitio. Es el mismo error de categoría que el punto anterior corrige para `config.js`.
- Generar `config.js` en desarrollo local a partir del `.env` de la raíz, replicando lo que `entrypoint.sh` hace en Docker, para que ambos modos usen un solo mecanismo. La generación no debe depender de `envsubst`: no está disponible en Windows, una plataforma de desarrollo soportada en este repo.
- Tratar la cadena vacía como "no configurado" al resolver `AUTH_ENABLED`, para que una variable ausente caiga a las capas de build-time y default en vez de desactivar la autenticación en silencio. `API_URL` conserva su semántica actual: vacío es un valor legítimo allí, y significa "mismo origen, proxeado por nginx".
- Hacer legible la condicional de `src/config.ts`. Hoy la precedencia entre las tres capas se expresa con ternarios anidados que además incrustan la coerción a boolean (`config.AUTH_ENABLED === true || String(config.AUTH_ENABLED).toLowerCase() === "true"`), de modo que no se puede auditar de un vistazo qué cuenta como "configurado" ni en qué orden se eligen las capas. La precedencia runtime → build-time → default debe quedar explícita y escribirse una sola vez, con la coerción de cada valor separada de la selección de capa. Es un refactor sin cambio de comportamiento más allá del punto anterior, y es lo que vuelve auditable la regla de la cadena vacía.

Non-goals: el drift de `.env.example` detectado en paralelo (`POSTGRES_PORT`/`REDIS_PORT` sin consumidores, `DB_URL` apuntando al puerto 4003 mientras `compose.dev.yaml` publica el 5432, `compose.dev.yaml` ignorando `.env` por completo) es un asunto aparte y no se aborda acá.

## Capabilities

### New Capabilities

- `frontend-runtime-config`: cómo la aplicación web resuelve en el navegador la configuración definida al desplegar (`API_URL`, `AUTH_ENABLED`) — la precedencia entre las capas runtime, build-time y default; qué cuenta como valor configurado para cada clave; y cómo se produce el archivo de runtime config en cada modo de ejecución.

  Complementa a la capability existente `frontend-delivery` sin solaparse: aquella gobierna **cómo llega** `/config.js` al navegador (headers de caching, ausencia de service worker); esta gobierna **cómo se interpreta** su contenido una vez que llegó.

### Modified Capabilities

<!-- Ninguna. `frontend-delivery` no cambia: este change no toca la entrega ni el caching. -->

## Impact

Código afectado:

- `frontend/public/config.js` — se saca del control de versiones y se agrega a `.gitignore` de la raíz
- `frontend/public/config.template.js` → `frontend/config.template.js` — sale de `public/` para dejar de publicarse como asset web; queda como la única definición commiteada de la forma del config
- `frontend/vite.config.ts` — generación de `config.js` en tiempo de desarrollo
- `frontend/src/config.ts` — manejo de la cadena vacía para `AUTH_ENABLED`, y refactor de los ternarios anidados a una resolución de capas explícita
- `frontend/Dockerfile` — el `COPY` de la plantilla pasa a apuntar a una ruta fuera del directorio servido por nginx
- `frontend/entrypoint.sh` — lee la plantilla desde su nueva ruta; sigue escribiendo `config.js` dentro del directorio servido
- `frontend/nginx.conf` — sin cambios

Comportamiento afectado:

- Desarrollo local pasa a respetar el `.env` de la raíz para la configuración del frontend, lo que cambia el comportamiento implícito de hoy (auth siempre encendida, API siempre en el mismo origen).
- Un despliegue que nunca definió `AUTH_ENABLED` pasa de esconder el login a mostrarlo, alineándose con lo que el backend siempre exigió.

Sin cambios de API, base de datos ni worker. Sin cambios en `backend/` ni `worker/`.

Depende de `remove-pwa`, ya aplicado y archivado: sin esa remoción, este change habría necesitado además excluir `/config.js` del precache del service worker.
