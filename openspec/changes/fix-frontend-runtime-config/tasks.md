## 1. Sacar la plantilla del directorio servido

- [ ] 1.1 Mover `frontend/public/config.template.js` a `frontend/config.template.js` con `git mv`, sin cambiar su contenido
- [ ] 1.2 En `frontend/Dockerfile`, cambiar el `COPY --from=builder` de la plantilla para que tome `/app/config.template.js` y la deposite en una ruta fuera de `/usr/share/nginx/html`
- [ ] 1.3 En `frontend/entrypoint.sh`, leer la plantilla desde la ruta nueva; el destino de `envsubst` sigue siendo `/usr/share/nginx/html/config.js`
- [ ] 1.4 Confirmar que `frontend/.dockerignore` no excluye `config.template.js` de la etapa builder

## 2. Sacar `public/config.js` del control de versiones

- [ ] 2.1 Ejecutar `git rm --cached frontend/public/config.js` sin borrar el archivo del disco todavía
- [ ] 2.2 Agregar el patrón `frontend/public/config.js` al `.gitignore` de la raíz — específico, no un `config.js` genérico que ignoraría archivos no relacionados
- [ ] 2.3 Borrar `frontend/public/config.js` del disco y confirmar que `git status` no lo reporta
- [ ] 2.4 Confirmar que `frontend/public/` queda conteniendo únicamente assets reales del sitio

## 3. Generar `config.js` en desarrollo

- [ ] 3.1 Escribir un plugin local de Vite que, vía `configureServer`, intercepte `/config.js` y responda con el contenido generado desde `frontend/config.template.js`
- [ ] 3.2 Sustituir los `${VAR}` de la plantilla usando las variables que Vite ya carga del `.env` de la raíz (`envDir: ".."`, `loadEnv(mode, "..", "")`), en Node y sin depender de `envsubst`
- [ ] 3.3 Igualar el comportamiento de `envsubst` para variables ausentes: sustituirlas por cadena vacía, no dejar el `${VAR}` literal ni omitir la clave
- [ ] 3.4 Hacer que el plugin falle ruidosamente al arrancar si no puede leer la plantilla, en vez de dejar que la app caiga en silencio a las capas de build-time
- [ ] 3.5 Registrar el plugin en `frontend/vite.config.ts` conservando el resto de la configuración

## 4. Reescribir la resolución de configuración

- [ ] 4.1 En `frontend/src/config.ts`, expresar la precedencia runtime → build-time → default una sola vez, como una lista ordenada de candidatos, en vez de repetirla por variable
- [ ] 4.2 Separar el parseo de la selección de capa: cada clave declara cómo interpreta un valor crudo y qué cuenta como ausente
- [ ] 4.3 `API_URL`: aceptar cualquier string como valor configurado, incluida la cadena vacía, que significa mismo origen
- [ ] 4.4 `AUTH_ENABLED`: aceptar solo `true`/`false` sin distinguir mayúsculas; tratar cualquier otro valor, incluida la cadena vacía, como ausente
- [ ] 4.5 Cambiar el default final de `isAuthEnabled` de `false` a `true`
- [ ] 4.6 Confirmar que la app no falla cuando `window.__APP_CONFIG__` está indefinido y todo se resuelve por build-time y default

## 5. Verificar en desarrollo

- [ ] 5.1 Con `AUTH_ENABLED=false` en el `.env` de la raíz, confirmar que la pantalla de login no aparece — es la comprobación directa del defecto que motivó el change
- [ ] 5.2 Quitar `AUTH_ENABLED` del `.env` y confirmar que la pantalla de login sí aparece
- [ ] 5.3 Poner `AUTH_ENABLED=TRUE` en mayúsculas y confirmar que se interpreta como habilitada
- [ ] 5.4 Cambiar `API_URL` en el `.env`, recargar y confirmar que el valor nuevo se refleja sin reiniciar el servidor de desarrollo
- [ ] 5.5 Confirmar que no se escribió ningún `config.js` en `frontend/public/` ni en ningún otro lado del working tree
- [ ] 5.6 Confirmar que `curl` a `/config.js` en el servidor de desarrollo devuelve JavaScript con los valores sustituidos, no el fallback SPA en HTML

## 6. Verificar el build y el container

- [ ] 6.1 Ejecutar `pnpm run build` y confirmar que `frontend/dist/` no contiene `config.template.js` ni `config.js`
- [ ] 6.2 Confirmar que `frontend/dist/index.html` conserva `<script src="/config.js">`
- [ ] 6.3 Construir la imagen y confirmar que el container genera `/config.js` en el arranque con los valores del entorno
- [ ] 6.4 Confirmar que `GET /config.template.js` contra el container ya no entrega la plantilla
- [ ] 6.5 Arrancar el container **sin** definir `AUTH_ENABLED` y confirmar que la aplicación muestra la pantalla de login, en vez de esconderla mientras la API rechaza los requests
- [ ] 6.6 Reiniciar el container con `AUTH_ENABLED=false` y confirmar que la siguiente recarga apaga el login

## 7. Cerrar

- [ ] 7.1 Anotar en las notas de la versión que un despliegue que nunca definió `AUTH_ENABLED` pasa a exigir login, y que desactivarlo ahora requiere `AUTH_ENABLED=false` explícito
- [ ] 7.2 Subir la versión del frontend siguiendo la convención del repositorio de versionar los servicios en conjunto
