## 1. Eliminar el service worker del build

- [x] 1.1 Quitar el import de `VitePWA` y su bloque de configuración completo de `frontend/vite.config.ts`, conservando el resto de plugins (`devtools`, `tailwindcss`, `tanstackRouter`, `viteReact`) y la sección `build` intactos
- [x] 1.2 Quitar la dependencia `vite-plugin-pwa` de `frontend/package.json`
- [x] 1.3 Ejecutar `pnpm install` en `frontend/` para regenerar `pnpm-lock.yaml` y dejarlo sincronizado con `package.json`
- [x] 1.4 Quitar la entrada `dev-dist/` de `.gitignore`

## 2. Eliminar el manifest y la interfaz de instalación

- [x] 2.1 Eliminar `frontend/public/manifest.json`
- [x] 2.2 Quitar `<link rel="manifest" href="/manifest.json" />` de `frontend/index.html`, conservando `theme-color`, `apple-touch-icon`, `mobile-web-app-capable` y las meta `apple-mobile-web-app-*`
- [x] 2.3 Eliminar `frontend/src/hooks/use-pwa-install.ts`
- [x] 2.4 Eliminar `frontend/src/components/install-banner.tsx`
- [x] 2.5 Quitar el import de `InstallBanner` y su render de `frontend/src/routes/__root.tsx`
- [x] 2.6 Eliminar `frontend/public/logo512.png`, que queda sin referencias al desaparecer el manifest
- [x] 2.7 Confirmar por búsqueda que no quedan referencias a `logo512`, `InstallBanner`, `usePWAInstall` ni `beforeinstallprompt` en `frontend/src/` ni en `frontend/index.html`

## 3. Reponer la garantía de frescura del documento en nginx

- [x] 3.1 Agregar en `frontend/nginx.conf` una regla `location = /index.html` con `add_header Cache-Control "no-cache"`, ubicada antes del `location /` existente
- [x] 3.2 Verificar que la regla también aplica a las navegaciones que resuelve `try_files`: `curl -I http://localhost:3000/` debe devolver `Cache-Control: no-cache`, no solo `curl -I http://localhost:3000/index.html`
- [x] 3.3 Confirmar que `location = /config.js` con `no-store` y `location /assets/` con `expires 1y` e `immutable` siguen presentes y sin modificar

## 4. Limpiar artefactos locales antes de verificar

- [x] 4.1 Borrar los directorios `frontend/dist/` y `frontend/dev-dist/` locales, para que la verificación del build no lea residuos de builds anteriores
- [x] 4.2 Ejecutar `pnpm run build` en `frontend/`

## 5. Verificar el build

- [x] 5.1 Confirmar que `frontend/dist/` no contiene `sw.js`, `workbox-*.js` ni `registerSW.js`
- [x] 5.2 Confirmar que `frontend/dist/` no contiene `manifest.json` ni `logo512.png`
- [x] 5.3 Confirmar que `frontend/dist/index.html` no incluye `<script id="vite-plugin-pwa:register-sw">` ni `<link rel="manifest">`
- [x] 5.4 Confirmar que `frontend/dist/index.html` conserva `theme-color`, `apple-touch-icon`, `mobile-web-app-capable` y las meta `apple-mobile-web-app-*`
- [x] 5.5 Confirmar que `frontend/dist/index.html` conserva `<script src="/config.js">` y que `dist/config.template.js` sigue presente
- [x] 5.6 Levantar el servidor de desarrollo y confirmar que no se genera `frontend/dev-dist/`

## 6. Verificar en runtime

- [x] 6.1 Levantar la aplicación con `docker compose -f compose.dev.yaml up -d --build` y confirmar que carga correctamente
- [x] 6.2 Confirmar en las herramientas de desarrollo, pestaña Network, que ninguna respuesta figura como servida por un service worker
- [x] 6.3 Confirmar que no aparece ningún banner ofreciendo instalar la aplicación
- [x] 6.4 Cambiar una variable de configuración, reiniciar el container y confirmar que la siguiente recarga refleja el nuevo valor sin limpiar el cache del navegador
- [x] 6.5 Recargar dos veces y confirmar en Network que `index.html` se revalida (`304`) mientras los recursos de `/assets/` se sirven desde el cache HTTP sin petición

## 7. Desmantelar los service workers ya registrados

- [x] 7.1 Desregistrar el service worker en el navegador propio para `localhost:3000`, desde *Application → Service Workers → Unregister*
- [x] 7.2 Repetir para cualquier otro origen donde se haya abierto la aplicación (instancia en la red local, cualquier host propio)
- [x] 7.3 Confirmar tras desregistrar que una recarga forzada sirve la versión nueva de la aplicación

## 8. Publicar y verificar en dispositivo

- [x] 8.1 Subir la versión del frontend siguiendo la convención del repositorio de versionar los servicios en conjunto, y publicar imagen nueva
- [x] 8.2 Verificar en un iPhone real, contra la instancia sobre HTTP, si "Añadir a pantalla de inicio" funciona y abre en modo standalone
- [x] 8.3 Si la verificación 8.2 falla, quitar `apple-touch-icon` y las meta `apple-mobile-web-app-*` de `frontend/index.html` en un commit posterior, conservando `theme-color`
