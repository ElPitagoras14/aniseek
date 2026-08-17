# frontend-delivery Specification

## Purpose

Define cómo se entrega la aplicación web al navegador: qué se permite ejecutar como service worker, y qué garantiza que el navegador reciba assets y configuración de runtime frescos una vez que no existe ninguna capa de caching propia entre el navegador y nginx.

Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras clave de especificación, igual que los headers de sección.

## Requirements
### Requirement: No se distribuye ningún service worker

El frontend SHALL NOT generar, publicar ni registrar un service worker, en ningún modo de ejecución. No SHALL existir ninguna capa de caching propia entre el navegador y nginx.

#### Scenario: El build de producción no produce service worker

- **WHEN** se construye el bundle de producción
- **THEN** el directorio de salida no contiene `sw.js`, `workbox-*.js` ni `registerSW.js`
- **AND** el `index.html` construido no incluye ningún script de registro de service worker

#### Scenario: El servidor de desarrollo no registra service worker

- **WHEN** se levanta el servidor de desarrollo
- **THEN** no se genera el directorio `dev-dist/`
- **AND** ninguna página intenta registrar un service worker

#### Scenario: Ninguna petición es respondida desde un cache propio

- **WHEN** el navegador solicita cualquier recurso de la aplicación
- **THEN** la petición llega a nginx
- **AND** la respuesta proviene de nginx o del cache HTTP del navegador, nunca de un service worker

### Requirement: La configuración de runtime llega fresca al navegador

`/config.js` SHALL ser servido con `Cache-Control: no-store`, de modo que el navegador obtenga en cada carga el archivo que `entrypoint.sh` escribió en el arranque del container.

#### Scenario: Un cambio de configuración surte efecto en la siguiente recarga

- **WHEN** se modifica una variable de configuración en `.env` y se reinicia el container
- **THEN** la siguiente recarga del navegador refleja el nuevo valor
- **AND** no se requiere publicar una imagen nueva ni limpiar el cache del navegador

#### Scenario: La respuesta declara que no debe almacenarse

- **WHEN** el navegador solicita `/config.js`
- **THEN** la respuesta incluye `Cache-Control: no-store`

### Requirement: El documento HTML se revalida en cada navegación

`index.html` SHALL ser servido con `Cache-Control: no-cache`, obligando al navegador a revalidarlo contra nginx antes de reutilizar su copia. Sin esta garantía el navegador puede aplicar freshness heurística y servir un documento que referencia assets versionados que ya no existen.

#### Scenario: Un despliegue nuevo llega al navegador sin intervención

- **WHEN** se publica una imagen nueva cuyos assets tienen hashes distintos
- **THEN** la siguiente navegación obtiene el `index.html` actualizado
- **AND** las referencias a assets que resuelve son las del build vigente

#### Scenario: Un documento sin cambios no se retransmite completo

- **WHEN** el navegador revalida `index.html` y el documento no cambió
- **THEN** nginx responde `304 Not Modified` en vez del cuerpo completo

### Requirement: Los assets versionados se cachean de forma inmutable

Los recursos servidos bajo `/assets/`, cuyo nombre incluye un hash de contenido, SHALL ser servidos con caching de larga duración e `immutable`. Esto sustituye por completo lo que antes aportaba el precache del service worker.

#### Scenario: Un asset ya conocido no se revalida

- **WHEN** el navegador necesita un asset de `/assets/` que ya tiene en su cache HTTP
- **THEN** lo sirve localmente sin emitir ninguna petición de revalidación

#### Scenario: Un asset nuevo se descarga por tener otro nombre

- **WHEN** un despliegue cambia el contenido de un asset
- **THEN** su nombre incluye un hash distinto
- **AND** el navegador lo descarga como recurso nuevo sin conflicto con la copia anterior

### Requirement: No se ofrecen capacidades que exijan un origen seguro

La aplicación SHALL NOT presentar interfaz de instalación ni publicar un web app manifest, porque la instalación de una aplicación web exige HTTPS y el despliegue soportado se sirve sobre HTTP plano. No SHALL quedar código de aplicación dedicado a la instalación.

#### Scenario: No se renderiza ninguna invitación a instalar

- **WHEN** un usuario abre la aplicación en cualquier navegador
- **THEN** no se muestra ningún banner ni control que ofrezca instalarla

#### Scenario: El build no publica manifest

- **WHEN** se construye el bundle de producción
- **THEN** el directorio de salida no contiene `manifest.json`
- **AND** el `index.html` construido no incluye `<link rel="manifest">`

#### Scenario: La aplicación no intercepta el evento de instalación

- **WHEN** un navegador Chromium emite `beforeinstallprompt`
- **THEN** la aplicación no registra ningún listener para ese evento
- **AND** el navegador conserva su comportamiento por defecto

### Requirement: Se conservan los metadatos de presentación móvil

`index.html` SHALL conservar las meta tags que mejoran la presentación en móvil y que no dependen de un origen seguro, de un manifest ni de un service worker: `theme-color`, `apple-touch-icon` y las meta de aplicación web de Apple.

#### Scenario: Las meta tags sobreviven al build

- **WHEN** se construye el bundle de producción
- **THEN** el `index.html` construido conserva `theme-color`
- **AND** conserva `apple-touch-icon`
- **AND** conserva `mobile-web-app-capable` y las meta `apple-mobile-web-app-*`

#### Scenario: El color de la barra del navegador se aplica sobre HTTP

- **WHEN** un usuario abre la aplicación sobre HTTP desde un navegador móvil que soporta `theme-color`
- **THEN** la barra del navegador adopta el color declarado

