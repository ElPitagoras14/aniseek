## Context

La maquinaria de PWA del frontend consiste en el plugin `VitePWA` de `vite.config.ts`, que genera `sw.js` con un precache manifest de Workbox, `workbox-*.js` y `registerSW.js`; más `public/manifest.json`, un `<link rel="manifest">` y varias meta tags de aplicación móvil en `index.html`; más la entrada `dev-dist/` en `.gitignore`.

La registración del service worker no está en el código de la aplicación: la inyecta el plugin en `index.html` durante el build, y ningún módulo de `src/` importa `virtual:pwa-register` ni `workbox`. Pero sí hay código de aplicación dedicado a la instalación: `src/hooks/use-pwa-install.ts` escucha `beforeinstallprompt`, `src/components/install-banner.tsx` dibuja un banner ofreciendo instalar la app, y `src/routes/__root.tsx` lo renderiza en todas las páginas.

Tres restricciones enmarcan el diseño:

- **El secure context es la restricción real, y alcanza a más de una cosa.** Servir la aplicación por HTTPS con dominio público implica exponer el despliegue ante un proveedor global de DNS y TLS, lo que no es viable para este servicio. Sin HTTPS no se registra un service worker, y tampoco se puede instalar la aplicación: MDN lo declara requisito de instalabilidad, no solo de service workers. Ambas capacidades caen por el mismo motivo.
- **No hay base instalada que migrar.** El proposal fija ese supuesto y sus límites. Sin él, la remoción exigiría publicar antes una versión con `selfDestroying: true`.
- **nginx ya hace caching por HTTP.** `nginx.conf` define `expires 1y` con `immutable` para `/assets/` y `no-store` para `/config.js`. Parte de lo que Workbox hacía ya está cubierto por headers.

## Goals / Non-Goals

**Goals:**

- Eliminar el service worker y toda la cadena de Workbox del build.
- Eliminar también lo que solo tiene sentido bajo HTTPS y por lo tanto nunca es alcanzable en el despliegue real.
- Devolver a nginx la autoridad exclusiva sobre el caching, sin ninguna capa propia entre el navegador y el servidor.
- Conservar lo que sí funciona sobre HTTP plano y no cuesta mantenimiento.
- No dejar detrás artefactos huérfanos: entradas de `.gitignore`, carpetas locales ni registraciones activas en los navegadores donde sí se instaló.

**Non-Goals:**

- Los defectos de resolución de configuración en `src/config.ts`. Son de `fix-frontend-runtime-config`.
- Reintroducir HTTPS o replantear la estrategia de despliegue.
- Cualquier forma de caching offline sustituto.

## Decisions

### D1 — El criterio de corte es el secure context, no la etiqueta "PWA"

La pregunta útil no es qué cosas se llaman PWA, sino qué cosas exigen HTTPS. Todo lo que lo exija es inalcanzable en este despliegue y debe irse; lo que funcione sobre HTTP plano puede quedarse si no cuesta nada.

**Se elimina** `public/manifest.json` junto con su `<link rel="manifest">`. Su único propósito es la instalación, y MDN es explícito al respecto:

> "For a PWA to be installable it must be served using the `https` protocol, or from a local development environment using `localhost` or `127.0.0.1`."

Conviene registrar por qué esto no es obvio: el service worker **ya no** es requisito de instalación —Chrome lo retiró en la versión 108 en móvil y 112 en escritorio, porque lo usaba como proxy de "tiene experiencia offline" y los sitios lo burlaban con fetch handlers vacíos—, así que quitar el service worker por sí solo no habría quitado la instalabilidad. Lo que la quita es la falta de HTTPS, que es una restricción independiente y anterior. Manifest y service worker mueren por la misma causa, no uno por el otro.

**Se conserva** `<meta name="theme-color">`, que colorea la barra del navegador en móvil sin requerir HTTPS, manifest ni service worker.

**Se conservan** `<link rel="apple-touch-icon">` y las meta `mobile-web-app-capable` / `apple-mobile-web-app-capable` / `apple-mobile-web-app-status-bar-style` / `apple-mobile-web-app-title`. Estas gobiernan el "Añadir a pantalla de inicio" de Safari en iOS, que es una ruta propia de Apple anterior tanto al manifest como a los service workers y que no pasa por ninguno de los dos: seguirá o dejará de funcionar con independencia de este change.

*Incertidumbre asumida:* no se encontró fuente autoritativa sobre si esa ruta de Safari exige HTTPS. Se conservan porque son seis líneas de HTML estático sin build ni dependencia asociada, y porque si resultan inoperantes sobre HTTP el costo de quitarlas después es trivial. Verificarlo en un dispositivo real queda como Open Question.

*Alternativa considerada:* eliminar también las meta de Apple por consistencia con "ya no somos una PWA". Se descarta porque la consistencia nominal no es un objetivo: el objetivo es que no quede código inalcanzable ni maquinaria de build sin uso, y estas etiquetas no son ninguna de las dos cosas.

### D2 — Una sola fase, sin `selfDestroying`

Se aplica el supuesto del proposal: no hay instalaciones activas que desmantelar. La fase previa con `selfDestroying: true` se omite.

*Alternativa considerada:* publicar igual una versión auto-destructiva por precaución cuesta un release completo y una versión intermedia en el historial para desinstalar service workers que no existen. El caso residual —un tercero que haya montado el proyecto desde GHCR detrás de su propio TLS— se resuelve manualmente desde las herramientas de desarrollo del navegador y no justifica el ciclo.

### D3 — No se compensa el caching que se pierde

Workbox precacheaba los assets con hash en el nombre. Eso ya lo cubre `location /assets/` en `nginx.conf` con `expires 1y` e `immutable`: mismo efecto, mismo alcance, sin service worker de por medio. No hace falta agregar nada para los assets.

Lo que sí se pierde es el funcionamiento offline, y se acepta: sin red la aplicación no puede hablar con la API, así que un shell cacheado solo serviría para mostrar una pantalla vacía.

### D4 — Se agrega una regla de cache para `index.html`

Esta es la única pérdida real que sí hay que compensar, y contradice el "nginx sin cambios" del proposal.

Hoy `nginx.conf` no define ninguna regla de caching para `index.html`: cae en `location /` con `try_files`, y nginx responde solo con `Last-Modified` y `ETag`, sin `Cache-Control`. Sin directiva explícita, el navegador puede aplicar freshness heurística y servir un `index.html` viejo sin revalidar. Ese `index.html` referencia nombres de assets con hash de un build anterior, que tras un despliegue nuevo ya no existen.

Hasta ahora eso no se notaba porque el service worker manejaba la navegación con su propia entrada de precache versionada. Al quitarlo, la garantía de frescura del documento desaparece y no queda nada en su lugar.

Se agrega una regla explícita para `index.html` con `Cache-Control: no-cache`, que permite al navegador conservar la copia pero lo obliga a revalidar contra nginx en cada carga. Es el mismo patrón que ya se usa para `/config.js`, un escalón más permisivo.

*Alternativa considerada:* `no-store` es innecesariamente estricto para un documento que sí puede revalidarse con `ETag`; obligaría a re-descargar el HTML completo en cada navegación sin ganancia.

### D5 — Se elimina también la UI de instalación

`use-pwa-install.ts`, `install-banner.tsx` y su render en `__root.tsx` se eliminan junto con el manifest.

El hook depende de `beforeinstallprompt`, un evento exclusivo de Chromium que solo se dispara cuando el navegador considera la aplicación instalable. Como eso exige HTTPS (D1), el evento nunca llegó a dispararse en el despliegue real: `isInstallable` es permanentemente `false` y el banner nunca se renderizó en producción. Safari no implementa ese evento en absoluto, así que en iOS tampoco apareció nunca. Al eliminar el manifest deja de tener sentido incluso bajo HTTPS.

Se elimina también el ícono `public/logo512.png`, que tras quitar `manifest.json` queda sin ninguna referencia en el repositorio. `logo192.png` se conserva: sigue en uso como `<link rel="icon">` y como `apple-touch-icon`. `favicon.ico` se conserva pese a que su única referencia textual estaba en el manifest, porque los navegadores lo solicitan por convención en `/favicon.ico` sin necesidad de que ningún documento lo declare.

*Efecto residual:* el hook escribe una clave `pwa-install-dismissed` en `localStorage` de quien haya descartado el banner. Queda huérfana en esos navegadores. Es inocua y no justifica código de limpieza.

### D6 — Los artefactos locales se limpian en el mismo commit

`dev-dist/` sale de `.gitignore` porque era exclusivamente la salida del plugin en desarrollo. Las carpetas `dev-dist/` y los `sw.js`, `workbox-*.js` y `registerSW.js` que hoy existen en el `dist/` local son residuos de builds previos: no están versionados, pero conviene borrarlos para que una verificación posterior del `dist/` no encuentre un service worker viejo y dé un falso negativo.

## Risks / Trade-offs

- **Tu propio navegador sí tiene un service worker registrado.** `devOptions.enabled: true` lo activa en `localhost`, que es justamente donde más se usó la aplicación durante el desarrollo. Quitar el plugin no lo desregistra. → Desregistrarlo a mano en *Application → Service Workers → Unregister* para cada origen donde se haya abierto la app, incluido `localhost:3000` y cualquier instancia propia. Es una acción única y manual, no parte del despliegue.

- **Un tercero que haya desplegado desde GHCR detrás de TLS queda con el service worker viejo, y además pierde la instalabilidad que sí tenía.** → Asumido en el proposal. Es el único escenario donde este change quita algo que funcionaba. No hay canal para comunicarlo y la recuperación del service worker es manual.

- **Las meta tags de Apple podrían no hacer nada sobre HTTP.** → No se pudo confirmar. Si es así, quedan seis líneas inertes en `index.html`, sin costo funcional ni de build. Se resuelve con una prueba en dispositivo, no con una decisión de diseño.

- **Si en el futuro se decide exponer el servicio por HTTPS, hay que rehacer el trabajo.** → El costo de reintroducir `vite-plugin-pwa` y el manifest es bajo y la configuración queda en el historial de git. No justifica conservar código inalcanzable mientras tanto.

## Migration Plan

1. Quitar el plugin `VitePWA` de `vite.config.ts` y la dependencia `vite-plugin-pwa` de `package.json`, en un solo commit junto con la entrada `dev-dist/` de `.gitignore`.
2. Eliminar `public/manifest.json` y el `<link rel="manifest">` de `index.html` (D1).
3. Eliminar `src/hooks/use-pwa-install.ts`, `src/components/install-banner.tsx`, su import y su render en `src/routes/__root.tsx`, y el ícono huérfano `public/logo512.png` (D5).
4. Agregar la regla de `Cache-Control: no-cache` para `index.html` en `nginx.conf` (D4).
5. Borrar las carpetas `dev-dist/` y `dist/` locales antes de reconstruir, para que la verificación no lea residuos.
6. Reconstruir y verificar que el `dist/` resultante **no** contiene `sw.js`, `workbox-*.js`, `registerSW.js` ni `manifest.json`, y que `index.html` ya no incluye el `<script id="vite-plugin-pwa:register-sw">` ni el `<link rel="manifest">`.
7. Confirmar que `theme-color`, `apple-touch-icon` y las meta de aplicación móvil de Apple siguen presentes en el `index.html` construido (D1).
8. Desregistrar manualmente el service worker en los navegadores propios.
9. Verificar en un iPhone real, contra la instancia sobre HTTP, si "Añadir a pantalla de inicio" funciona y abre en modo standalone. Si no lo hace, quitar las meta tags de Apple en un commit posterior.

**Rollback:** revertir el commit y reconstruir. Sin base instalada y sin estado persistido fuera del navegador, no hay migración de datos que deshacer. El único efecto residual sería un service worker que se alcanzó a registrar entre el despliegue y el rollback, resoluble por la misma vía manual.

## Open Questions

Ninguna bloquea la implementación. Las tres que estaban abiertas se resolvieron así:

- **Iconos huérfanos — resuelto.** Se verificó por búsqueda en el repositorio que `logo512.png` solo aparece referenciado en `manifest.json`, de modo que queda huérfano y se elimina (D5). `logo192.png` tiene tres referencias, de las cuales dos sobreviven al change. `favicon.ico` se conserva por convención del navegador pese a no quedar declarado en ningún documento.
- **Headers de caching de los estáticos de la raíz — resuelto como fuera de alcance.** `logo192.png` y `favicon.ico` caen en `location /` sin `Cache-Control` explícito, igual que `index.html`. La diferencia es la consecuencia: un `index.html` obsoleto referencia assets con hash que ya no existen y rompe la aplicación (D4), mientras que un ícono obsoleto no tiene ningún efecto funcional. Se deja como mejora opcional independiente de este change.
- **`apple-mobile-web-app-capable` sobre HTTP — reclasificado como verificación, no como decisión.** No se encontró fuente autoritativa sobre si el "Añadir a pantalla de inicio" de Safari exige HTTPS. Deja de ser una pregunta de diseño porque ninguna otra decisión depende de la respuesta: las meta tags son seis líneas de HTML estático sin build ni dependencia, y si resultan inertes se quitan después sin tocar nada más. Pasa a ser un paso de verificación en dispositivo real dentro de `tasks.md`.
