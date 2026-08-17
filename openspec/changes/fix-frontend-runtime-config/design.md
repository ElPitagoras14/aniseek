## Context

El frontend se distribuye como una imagen pre-construida en GHCR: el `dist/` que sirve nginx se compiló en CI, mucho antes de que alguien decida el valor de `API_URL` o `AUTH_ENABLED`. Por eso existe `/config.js`, un archivo que `entrypoint.sh` escribe con `envsubst` a partir de `config.template.js` en cada arranque del container, y que `index.html` carga de forma síncrona en el `<head>` antes del bundle.

`src/config.ts` consume ese archivo como la primera de tres capas: runtime (`window.__APP_CONFIG__`), build-time (`define` de Vite alimentado por `loadEnv`) y un default literal.

El estado actual y sus tres defectos están documentados en `proposal.md`. Para el diseño interesan sobre todo las restricciones que los rodean:

- **La imagen es inmutable, el container no.** Cualquier cosa calculada durante `pnpm run build` —incluido el precache manifest de Workbox— queda congelada; cualquier cosa escrita por `entrypoint.sh` cambia en cada arranque. Estas dos líneas de tiempo no pueden cruzarse.
- **El service worker es agresivo.** `registerType: "autoUpdate"` con `skipWaiting` y `clientsClaim` significa que toma control en la primera recarga, y que lo que esté en su precache gana sobre nginx sin negociación.
- **Windows es plataforma de desarrollo soportada.** `envsubst` viene de gettext y no está disponible en Git for Windows, así que el mecanismo del container no se puede reutilizar tal cual en desarrollo local.
- **`nginx.conf` ya proxea `/api/` al backend.** Por eso `API_URL` vacío es un valor legítimo y no un error: significa mismo origen.

## Goals / Non-Goals

**Goals:**

- Que `/config.js` refleje siempre el entorno actual del container en la siguiente recarga del navegador, con service worker instalado o sin él.
- Que `config.js` se produzca por un solo mecanismo conceptual en Docker y en desarrollo local, con la forma del archivo definida en un único lugar.
- Que la exclusión de `config.js` del precache esté declarada en el código y no dependa de que el archivo no exista.
- Que un `AUTH_ENABLED` ausente o vacío nunca resulte en autenticación desactivada.
- Que la precedencia entre capas sea legible y esté escrita una sola vez.

**Non-Goals:**

- El drift de `.env.example` (`POSTGRES_PORT`/`REDIS_PORT` sin consumidores, `DB_URL` al puerto 4003, `compose.dev.yaml` ignorando `.env`). Es un change aparte.
- Cambiar la semántica de `API_URL` o el proxy `/api/` de nginx.
- Revisar la estrategia de PWA más allá de `/config.js`. El resto del precache de assets con hash en el nombre está bien como está.
- Cualquier cambio en `backend/` o `worker/`.

## Decisions

### D1 — `public/config.js` sale del control de versiones

El archivo cumple dos roles incompatibles: placeholder para que `pnpm dev` no dé 404, y artefacto de runtime servido en producción. Mientras esté commiteado, Vite lo copia a `dist/`, Workbox lo mete en el precache manifest, y en desarrollo tapa las capas 2 y 3 de `src/config.ts`.

Se elimina del repo y se agrega a `frontend/.gitignore`.

*Alternativas consideradas:* dejarlo commiteado y arreglar solo el precache con `globIgnores` resuelve producción pero deja intacto el problema de desarrollo local, donde `AUTH_ENABLED=false` en `.env` sigue sin efecto. Tratar `""` como no configurado en `config.ts` sin tocar el archivo tampoco sirve: `API_URL: ""` es un valor legítimo y no se puede distinguir del placeholder.

### D2 — La exclusión del precache se declara igual, aunque D1 ya la consiga

Con `public/config.js` fuera del repo, `config.js` deja de existir en `dist/` y por lo tanto sale del precache manifest por sí solo. Eso es un arreglo por ausencia: nada en el código dice que ese archivo no debe cachearse, y el día que alguien vuelva a agregar un placeholder para quitarse el 404 de la consola, el bug reaparece sin relación aparente con el commit que lo causó.

Se agrega `globIgnores: ["config.js", "config.template.js"]` a la configuración de Workbox como declaración explícita e independiente de D1.

`config.template.js` entra en la lista porque hoy también está precacheado —se puede verificar en `dist/sw.js`— sin que nadie lo pida desde el HTML. Es peso muerto en el cache del navegador y una copia del template con los `${VAR}` sin sustituir.

### D3 — `/config.js` se sirve con `runtimeCaching` network-first

Sacarlo del precache sin más lo dejaría sin ninguna copia local, y la PWA abierta sin red no tendría configuración: `window.__APP_CONFIG__` quedaría `undefined` y todo caería a las capas de build-time, que en la imagen de GHCR vienen vacías.

Se agrega una regla de `runtimeCaching` con handler `NetworkFirst` para `/config.js`, con `networkTimeoutSeconds` acotado. La red manda siempre —que es justo lo que el bug rompía— y queda una copia para el caso offline.

*Alternativas consideradas:* `StaleWhileRevalidate` sirve la copia vieja en la primera carga después de un cambio y recién actualiza para la siguiente, o sea reproduce el síntoma original con una recarga de retraso. Dejarlo sin regla alguna es aceptable si se asume que la PWA offline no necesita configuración, pero degrada el comportamiento de auth offline de forma poco obvia.

### D4 — En desarrollo, `/config.js` lo sirve un middleware de Vite, no un archivo

Se agrega un plugin local que, vía `configureServer`, intercepta `/config.js` y responde con el contenido generado a partir de `config.template.js`, sustituyendo los `${VAR}` con las variables que Vite ya carga del `.env` de la raíz.

Dos consecuencias buscadas: en desarrollo no existe ningún `config.js` en disco que pueda volver a colarse al repo o al build, y el archivo se regenera en cada request, así que cambiar el `.env` y recargar alcanza.

*Alternativas consideradas:* escribir físicamente `public/config.js` desde un script `predev` obliga a mantenerlo gitignoreado y a recordar regenerarlo al cambiar el `.env`. Reutilizar `envsubst` mediante una dependencia npm agrega una dependencia para algo que son tres líneas de Node, y fue lo primero que se descartó por el requisito de Windows.

### D5 — La forma del config se define una sola vez, en `config.template.js`

Tanto `entrypoint.sh` como el plugin de D4 leen el mismo `config.template.js` y sustituyen `${VAR}`. En el container lo hace `envsubst`; en desarrollo lo hace Node. El mecanismo de sustitución difiere por plataforma, pero la plantilla —qué claves existen y cómo se llaman— vive en un único archivo commiteado.

Agregar una variable de configuración en el futuro debe requerir editar `config.template.js` y nada más del lado del frontend.

### D6 — `""` es "no configurado" para `AUTH_ENABLED`, pero sí es valor para `API_URL`

No hay una regla global correcta: para `API_URL`, `""` significa "mismo origen" y es el valor por defecto esperado en Docker; para un flag booleano, `""` no es un booleano.

La decisión es no buscar una regla única sino **un parser por clave**: cada variable declara cómo se interpreta un valor crudo y qué cuenta como ausente. `API_URL` acepta cualquier string, incluido el vacío. `AUTH_ENABLED` acepta `"true"`/`"false"` (case-insensitive) y trata cualquier otra cosa, incluido `""`, como ausente.

*Alternativa considerada:* normalizar `""` a `undefined` de forma global es más simple de escribir pero rompe el default de `API_URL`, que pasaría a resolverse por la capa de build-time en vez de quedar en mismo origen.

### D7 — El default final de `isAuthEnabled` pasa de `false` a `true`

Hoy, cuando ninguna capa aporta un valor, `isAuthEnabled` resuelve a `false`. Eso hace que D6 sea insuficiente por sí solo: tratar `""` como ausente solo mueve el problema una capa más abajo, donde el resultado sigue siendo "sin login".

El backend ya default-ea a `True` (`AuthSettings.AUTH_ENABLED`). Alinear el frontend elimina el modo roto en que la pantalla de login desaparece mientras la API rechaza todos los requests, y hace que la ausencia de configuración falle cerrado en ambos lados.

Desactivar la autenticación pasa a requerir un `AUTH_ENABLED=false` explícito, que es el contrato que el README ya describe.

### D8 — El refactor de `config.ts` separa selección de capa y parseo

La precedencia se escribe una vez, como una lista ordenada de valores candidatos, y el parseo de cada clave se aplica al resultado. Hoy la misma decisión está escrita dos veces con dos formas distintas (`!== undefined` en una rama, `typeof !== "undefined"` en la otra) y cada rama coerciona a su manera.

Forma esperada, sin comprometer la implementación exacta:

```
resolve(clave) = primer valor "presente" entre [ runtime, build-time ]  →  parser(clave)
                 si ninguno está presente                                →  default(clave)
```

*Alternativa considerada:* aplanar los ternarios anidados sin introducir el helper deja el código más corto pero sigue repitiendo la precedencia por cada variable, que es exactamente donde se escondió el defecto de `""`.

## Risks / Trade-offs

- **Los usuarios con el service worker viejo ya instalado no ven el arreglo hasta que el SW se actualice.** → El deploy que trae este change modifica `vite.config.ts`, así que `sw.js` cambia y el SW se actualiza en la siguiente carga; `cleanupOutdatedCaches()` ya está activo y descarta la entrada de precache obsoleta de `config.js`. El arreglo se auto-aplica en el mismo deploy que lo introduce, sin intervención manual.

- **Offline sin ninguna visita previa con red, no hay config alguna.** → Cae a las capas de build-time y default. Con D7 eso significa login visible y `apiUrl` relativo, que es el estado seguro. La app igual no puede hablar con la API sin red, así que el impacto real es cosmético.

- **El plugin de desarrollo y `entrypoint.sh` pueden divergir con el tiempo.** → Mitigado por D5: ambos derivan de `config.template.js`. El riesgo residual es que difieran en el manejo de una variable ausente (`envsubst` la sustituye por `""`; el plugin debe hacer lo mismo para que los dos modos coincidan).

- **`vite preview` sirve `dist/`, donde no habrá `config.js` ni middleware.** → Dará 404 y la app caerá a las capas de build-time. Es coherente y no rompe nada, pero conviene saberlo antes de usar `preview` para reproducir un bug de configuración.

- **D7 cambia el comportamiento observable de un despliegue mal configurado.** → Una instalación que hoy funciona sin login porque nunca definió `AUTH_ENABLED` empezará a pedir credenciales tras actualizar. Es el comportamiento correcto y coincide con lo que el backend siempre exigió, pero debe anunciarse en las notas de versión.

## Migration Plan

1. Aplicar los cambios de `vite.config.ts` (D2, D3, D4) y `src/config.ts` (D6, D7, D8) juntos. Separarlos deja ventanas donde el precache está arreglado pero la resolución no, o al revés.
2. Sacar `public/config.js` con `git rm --cached` y agregarlo a `frontend/.gitignore` en el mismo commit.
3. Verificar en el `dist/` resultante que `config.js` y `config.template.js` ya **no** aparecen en el precache manifest de `sw.js`, que es la comprobación directa del defecto original.
4. Publicar imagen nueva. La actualización del service worker ocurre sola en la siguiente carga de cada usuario.

**Rollback:** revertir el commit y republicar. Como el service worker se actualiza junto con la imagen, volver atrás restaura el comportamiento anterior sin dejar clientes en un estado intermedio. Lo único que no se revierte solo es un `.env` que se haya empezado a apoyar en el default de D7; conviene definir `AUTH_ENABLED` explícitamente al desplegar este change para que el rollback sea neutral.

## Open Questions

- El `Dockerfile` copia `config.template.js` explícitamente además de recibirlo dentro de `dist/`. Con `public/config.js` fuera, ¿ese `COPY` sigue haciendo falta o quedó como residuo?
- ¿Conviene además excluir `config.template.js` del `dist/` por completo, en vez de solo del precache? Serviría de poco a un atacante, pero tampoco tiene razón de estar en el bundle público.
- ¿El plugin de D4 debería cubrir también `vite preview`, o se acepta el 404 documentado en Risks?
- `vite-plugin-pwa` tiene `devOptions.enabled: true`. Se verificó que en desarrollo el precache manifest sale vacío, pero falta confirmar si la regla de `runtimeCaching` de D3 se registra igual en ese modo y si eso interfiere con el middleware de D4.
