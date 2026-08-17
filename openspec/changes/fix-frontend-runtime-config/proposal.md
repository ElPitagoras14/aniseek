## Why

El frontend resuelve `API_URL` y `AUTH_ENABLED` en runtime a través de `/config.js`, un archivo que `entrypoint.sh` escribe al arrancar el container para que una sola imagen pre-construida en GHCR sirva cualquier despliegue. El mecanismo es correcto, pero tres defectos hacen que la configuración resuelta no sea confiable:

1. **El service worker sirve un `/config.js` obsoleto en producción.** `frontend/public/config.js` está commiteado, así que Vite lo copia a `dist/` y Workbox lo incluye en el precache manifest con un revision de build-time (`802743d1…`, el MD5 del placeholder commiteado). Ese revision queda congelado dentro de la imagen, mientras el contenido del archivo se reescribe en cada arranque del container. Después de la primera instalación, el service worker responde `/config.js` desde su propio cache y nunca lo vuelve a pedir, porque el revision no cambia dentro de una misma versión de imagen. El header `Cache-Control: no-store` sobre `location = /config.js` (`frontend/nginx.conf`) queda sin efecto: el request nunca llega a nginx. Síntoma: cambiar `AUTH_ENABLED` en `.env` y reiniciar no surte efecto hasta que cambia la versión de la imagen.

2. **El placeholder commiteado tapa el fallback de build-time en desarrollo local.** `src/config.ts` apila runtime config sobre un `define` de Vite sobre un default, y el orden es correcto. Pero el placeholder siempre resuelve la capa 1 (`API_URL: ""` no es `undefined`), dejando las capas 2 y 3 inalcanzables. `vite.config.ts` ya carga el `.env` de la raíz (`envDir: ".."`, `loadEnv(mode, "..", "")`), y aun así `AUTH_ENABLED=false` en `.env` no puede apagar la pantalla de login en desarrollo local — el placeholder fija `AUTH_ENABLED: true`.

3. **Un `AUTH_ENABLED` ausente falla abierto en el frontend y cerrado en el backend.** Si la variable falta en `.env`, `compose.yaml` pasa un valor vacío, `envsubst` escribe `AUTH_ENABLED: ""`, y `src/config.ts` acepta `""` como valor definido porque solo compara contra `undefined` — resolviendo a `false`. El backend, en cambio, tiene default `True` (`AuthSettings.AUTH_ENABLED`). La aplicación entonces esconde la pantalla de login mientras la API rechaza todos los requests.

Los tres comparten una misma raíz: un artefacto de runtime tratado como un asset de build, y "vacío" tratado como "definido". El defecto 3, además, pasó desapercibido porque la resolución de las tres capas está escrita como ternarios anidados que mezclan en una sola expresión la elección de capa con la coerción del valor.

## What Changes

- Dejar de commitear `frontend/public/config.js`. `config.template.js` pasa a ser la única fuente de la forma del archivo de configuración; el `config.js` concreto siempre se genera, nunca se guarda.
- Generar `config.js` en desarrollo local a partir del `.env` de la raíz, replicando lo que `entrypoint.sh` hace en Docker, para que ambos modos usen un solo mecanismo. La generación no debe depender de `envsubst`: no está disponible en Windows, una plataforma de desarrollo soportada en este repo.
- Declarar `config.js` y `config.template.js` como nunca precacheados en la configuración de Workbox, para que la exclusión sobreviva a que alguien vuelva a agregar un archivo placeholder. Servir `/config.js` mediante una regla de runtime caching network-first, de modo que quede fresco en cada carga y siga disponible offline.
- Tratar la cadena vacía como "no configurado" al resolver `AUTH_ENABLED`, para que una variable ausente caiga a las capas de build-time y default en vez de desactivar la autenticación en silencio. `API_URL` conserva su semántica actual: vacío es un valor legítimo allí, y significa "mismo origen, proxeado por nginx".
- Hacer legible la condicional de `src/config.ts`. Hoy la precedencia entre las tres capas se expresa con ternarios anidados que además incrustan la coerción a boolean (`config.AUTH_ENABLED === true || String(config.AUTH_ENABLED).toLowerCase() === "true"`), de modo que no se puede auditar de un vistazo qué cuenta como "configurado" ni en qué orden se eligen las capas. La precedencia runtime → build-time → default debe quedar explícita y escribirse una sola vez, con la coerción de cada valor separada de la selección de capa. Es un refactor sin cambio de comportamiento más allá del punto anterior, y es lo que vuelve auditable la regla de la cadena vacía.

Non-goals: el drift de `.env.example` detectado en paralelo (`POSTGRES_PORT`/`REDIS_PORT` sin consumidores, `DB_URL` apuntando al puerto 4003 mientras `compose.dev.yaml` publica el 5432, `compose.dev.yaml` ignorando `.env` por completo) es un asunto aparte y no se aborda acá.

## Capabilities

### New Capabilities

- `frontend-runtime-config`: cómo la aplicación web resuelve en el navegador la configuración definida al desplegar (`API_URL`, `AUTH_ENABLED`) — la precedencia entre las capas runtime, build-time y default; cómo se produce el archivo de runtime config en cada modo de ejecución; y cómo se exige que el service worker lo trate.

### Modified Capabilities

<!-- Ninguna. openspec/specs/ está vacío; esta es la primera capability capturada. -->

## Impact

Código afectado:

- `frontend/public/config.js` — se saca del control de versiones y se agrega a `frontend/.gitignore`
- `frontend/public/config.template.js` — queda como la única definición commiteada de la forma del config
- `frontend/vite.config.ts` — `globIgnores` + `runtimeCaching` de Workbox; generación de `config.js` en tiempo de desarrollo
- `frontend/src/config.ts` — manejo de la cadena vacía para `AUTH_ENABLED`, y refactor de los ternarios anidados a una resolución de capas explícita
- `frontend/entrypoint.sh`, `frontend/Dockerfile`, `frontend/nginx.conf` — se espera que queden como están; verificar si el `COPY` redundante de `config.template.js` sigue haciendo falta una vez que `public/config.js` desaparezca

Comportamiento afectado:

- Los usuarios con un service worker ya instalado recibirán los cambios de configuración al recargar, en lugar de esperar al próximo upgrade de imagen.
- Desarrollo local pasa a respetar el `.env` de la raíz para la configuración del frontend, lo que cambia el comportamiento implícito de hoy (auth siempre encendida, API siempre en el mismo origen).

Sin cambios de API, base de datos ni worker. Sin cambios en `backend/` ni `worker/`.
