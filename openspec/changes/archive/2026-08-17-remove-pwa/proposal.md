## Why

La PWA no puede funcionar en un despliegue real de AniSeek. Registrar un service worker fuera de `localhost`, y ofrecer instalabilidad, exige un origen seguro; servir la aplicación por HTTPS con un dominio público implica exponer el despliegue ante un proveedor global de DNS y TLS. Para este servicio esa exposición no es viable, y es una decisión de operación, no técnica. El resultado es que en producción el service worker nunca llega a activarse y el plugin solo aporta superficie: configuración de Workbox, un manifest, meta tags y una dependencia.

Mientras tanto, en los entornos donde sí se activa, hace daño. El service worker es la causa única del defecto de configuración obsoleta documentado en `fix-frontend-runtime-config`: precachea `/config.js` con un revision calculado en build-time y luego responde desde su propio cache, anulando el `Cache-Control: no-store` que `nginx.conf` ya define para ese archivo. Sin PWA, ese defecto desaparece por completo y el diseño original de configuración en runtime vuelve a ser correcto tal como está.

## What Changes

- Eliminar el plugin `VitePWA` de `vite.config.ts` y la dependencia `vite-plugin-pwa` de `package.json`.
- Eliminar `public/manifest.json` y el `<link rel="manifest">` de `index.html`. El criterio de corte es el secure context: la instalación de una aplicación web exige HTTPS igual que el service worker, así que el manifest tampoco es alcanzable en este despliegue. Notablemente, el service worker ya no es requisito de instalación en Chrome —lo retiró en la versión 108 en móvil y 112 en escritorio—, de modo que lo que impide instalar no es quitarlo, sino la falta de HTTPS.
- Conservar en `index.html` lo que funciona sobre HTTP plano y no depende de nada de lo anterior: `<meta name="theme-color">`, `<link rel="apple-touch-icon">` y las meta de aplicación móvil de Apple, que gobiernan una ruta de "Añadir a pantalla de inicio" propia de Safari, anterior tanto al manifest como a los service workers. Se conserva también `<script src="/config.js">`, que no tiene relación con la PWA.
- Quitar la entrada `dev-dist/` de `.gitignore`, que existía solo para la salida de `vite-plugin-pwa` en desarrollo.
- Agregar en `frontend/nginx.conf` una regla de `Cache-Control: no-cache` para `index.html`. Hoy ese documento no tiene ninguna directiva de caching y su frescura la garantizaba, de hecho, la entrada de precache versionada del service worker; al quitarlo hay que reponer esa garantía por HTTP o el navegador puede servir un `index.html` viejo que referencia assets con hash que ya no existen.
- No se toca `location = /config.js` con `Cache-Control: no-store` en `frontend/nginx.conf`. Hoy parece inoperante precisamente porque el service worker lo anula; al quitar la PWA pasa a ser la única pieza que garantiza que el navegador reciba la configuración fresca del container.

Se hace en un solo paso, sin fase de desinstalación previa. Un service worker ya instalado no se desregistra porque se deje de publicar `sw.js` —los navegadores cachean ese script hasta 24 horas y seguirían sirviendo la aplicación vieja desde su propio precache—, de modo que un despliegue con usuarios existentes requeriría publicar antes una versión con `selfDestroying: true`. **Este change asume que no existen instalaciones con service worker activo**, por tratarse de un proyecto personal sin base de usuarios desplegada.

El supuesto tiene un límite conocido y aceptado: el proyecto publica imágenes en GHCR y documenta self-hosting en el README, así que un tercero que lo haya montado detrás de su propio TLS sí tendría un service worker registrado. Para esos casos la vía de recuperación es manual (desregistrar desde las herramientas de desarrollo del navegador) y no justifica una fase de migración en este repo. Si en el futuro se confirma la existencia de tales despliegues, la desinstalación ordenada requeriría reintroducir `selfDestroying: true` durante una versión antes de retirar el plugin.

Pérdida de capacidad deliberada: la aplicación deja de ser instalable y deja de funcionar offline. Ambas cosas exigen un origen seguro, así que solo eran alcanzables en desarrollo local o detrás de un proxy con TLS propio, nunca en el despliegue que el README describe.

Non-goals: los defectos de resolución de configuración en `src/config.ts` (el placeholder commiteado que tapa el fallback en desarrollo local, y la cadena vacía que resuelve `AUTH_ENABLED` a `false`) sobreviven a este change y siguen siendo responsabilidad de `fix-frontend-runtime-config`.

## Capabilities

### New Capabilities

- `frontend-delivery`: cómo se entrega la aplicación web al navegador — qué se permite ejecutar como service worker, y qué garantiza que el navegador reciba assets y configuración de runtime frescos una vez que no hay ninguna capa de caching propia entre el navegador y nginx.

### Modified Capabilities

<!-- Ninguna. openspec/specs/ está vacío. -->

## Impact

Código afectado:

- `frontend/vite.config.ts` — se elimina el plugin `VitePWA` y su bloque de configuración
- `frontend/package.json` — se quita la dependencia `vite-plugin-pwa`
- `frontend/index.html` — se quita `<link rel="manifest">`; se conservan `theme-color`, `apple-touch-icon` y las meta de aplicación móvil de Apple
- `frontend/public/manifest.json` — se elimina
- `frontend/public/logo512.png` — se elimina; tras quitar el manifest queda sin ninguna referencia
- `frontend/src/hooks/use-pwa-install.ts` y `frontend/src/components/install-banner.tsx` — se eliminan; el banner de instalación depende de `beforeinstallprompt`, que exige HTTPS y por lo tanto nunca llegó a mostrarse en el despliegue real
- `frontend/src/routes/__root.tsx` — se quitan el import y el render de `<InstallBanner />`
- `.gitignore` — se quita la entrada `dev-dist/`
- `frontend/nginx.conf` — se agrega una regla de caching para `index.html`; su regla existente para `/config.js` pasa a ser load-bearing

Relación con otros changes:

- `fix-frontend-runtime-config` debe re-scopearse **después** de aplicar este change. Su defecto 1 y sus decisiones D2 (`globIgnores`) y D3 (`runtimeCaching` network-first) dejan de tener objeto sin service worker; el resto de ese change sigue vigente.

Sin cambios en `backend/`, `worker/`, la API, la base de datos ni los archivos de compose.

La registración del service worker no vive en `src/` sino en el `index.html` que genera el plugin, pero la instalación sí tiene código de aplicación propio —el hook y el banner listados arriba— que se elimina como parte de este change.
