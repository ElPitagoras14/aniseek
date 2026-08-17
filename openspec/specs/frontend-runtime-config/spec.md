# frontend-runtime-config Specification

## Purpose

Define cómo se produce el archivo de configuración de runtime del frontend (`config.js`) y cómo la aplicación interpreta su contenido: el orden de precedencia entre capas de configuración, qué cuenta como valor configurado en cada clave, y las garantías de que la plantilla que declara esas claves nunca se versiona ni se publica como asset web. Complementa a `frontend-delivery`, que gobierna cómo llega `/config.js` al navegador (caching, ausencia de service worker); esta capacidad gobierna cómo se produce ese archivo y cómo se interpreta su contenido.

Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras clave de especificación, igual que los headers de sección.

## Requirements
### Requirement: La precedencia entre capas se aplica igual para toda clave

La aplicación SHALL resolver cada clave de configuración probando, en orden, la capa de runtime (`window.__APP_CONFIG__`), la capa de build-time (`define` de Vite alimentado por el `.env` de la raíz) y un default. El orden SHALL estar expresado una sola vez y aplicarse de forma idéntica a todas las claves, sin repetirse por variable.

#### Scenario: La capa de runtime gana sobre la de build-time

- **WHEN** una clave tiene un valor configurado en `window.__APP_CONFIG__` y también en la capa de build-time
- **THEN** la aplicación usa el valor de runtime

#### Scenario: Sin valor de runtime se usa el de build-time

- **WHEN** una clave no tiene un valor configurado en `window.__APP_CONFIG__` pero sí en la capa de build-time
- **THEN** la aplicación usa el valor de build-time

#### Scenario: Sin ninguna capa se usa el default

- **WHEN** una clave no tiene valor configurado en ninguna de las dos capas
- **THEN** la aplicación usa el default declarado para esa clave

#### Scenario: La ausencia del archivo de runtime no rompe la aplicación

- **WHEN** `/config.js` no se carga y `window.__APP_CONFIG__` queda indefinido
- **THEN** todas las claves se resuelven por las capas de build-time y default
- **AND** la aplicación arranca sin error

### Requirement: Qué cuenta como valor configurado se decide por clave

Cada clave SHALL declarar cómo se interpreta un valor crudo y qué cuenta como ausente. No SHALL existir una regla global de conversión aplicada por igual a todas las claves, porque la cadena vacía es un valor legítimo para unas y ausencia para otras.

#### Scenario: Para `API_URL` la cadena vacía es un valor

- **WHEN** `API_URL` se resuelve a la cadena vacía en la capa de runtime
- **THEN** la aplicación la trata como valor configurado y no desciende a las capas siguientes
- **AND** las peticiones a la API se emiten contra el mismo origen, que nginx proxea a `/api/`

#### Scenario: Para `AUTH_ENABLED` la cadena vacía es ausencia

- **WHEN** `AUTH_ENABLED` se resuelve a la cadena vacía en la capa de runtime
- **THEN** la aplicación la trata como no configurada y desciende a las capas siguientes

#### Scenario: `AUTH_ENABLED` se interpreta sin distinguir mayúsculas

- **WHEN** `AUTH_ENABLED` vale `"true"`, `"TRUE"` o `"True"`
- **THEN** la aplicación resuelve la autenticación como habilitada

#### Scenario: Un valor no reconocido cuenta como ausencia

- **WHEN** `AUTH_ENABLED` vale una cadena que no es `"true"` ni `"false"` en ninguna capitalización
- **THEN** la aplicación la trata como no configurada y desciende a las capas siguientes

### Requirement: La autenticación nunca se desactiva por omisión

El default final de la autenticación en el frontend SHALL ser habilitada. Desactivarla SHALL requerir un valor explícito y reconocido. Esto alinea al frontend con el backend, cuyo default también es habilitada, de modo que una configuración ausente falla cerrada en ambos lados.

#### Scenario: Sin configuración en ninguna capa se exige login

- **WHEN** `AUTH_ENABLED` no está configurada en ninguna de las capas
- **THEN** la aplicación muestra la pantalla de login
- **AND** el comportamiento coincide con el del backend, que exige token

#### Scenario: Desactivar la autenticación requiere declararlo

- **WHEN** `AUTH_ENABLED` vale explícitamente `"false"`
- **THEN** la aplicación omite la pantalla de login

#### Scenario: Una variable ausente en el despliegue no esconde el login

- **WHEN** se despliega sin definir `AUTH_ENABLED` y `envsubst` escribe una cadena vacía
- **THEN** la aplicación muestra la pantalla de login
- **AND** no se produce el estado en que el login está oculto mientras la API rechaza todos los requests

### Requirement: El archivo de runtime config siempre se genera y nunca se versiona

`config.js` SHALL producirse a partir de `config.template.js` en todos los modos de ejecución y SHALL NOT estar bajo control de versiones. La plantilla SHALL ser la única definición commiteada de qué claves existen.

#### Scenario: El archivo generado no está en el repositorio

- **WHEN** se inspecciona el repositorio
- **THEN** no existe ningún `config.js` versionado
- **AND** el patrón que lo ignora está declarado en el `.gitignore` de la raíz

#### Scenario: En Docker lo escribe el arranque del container

- **WHEN** el container arranca
- **THEN** se genera `config.js` sustituyendo las variables de la plantilla por los valores del entorno
- **AND** el archivo generado queda dentro del directorio que sirve nginx

#### Scenario: En desarrollo lo produce el servidor de desarrollo

- **WHEN** el servidor de desarrollo recibe una petición de `/config.js`
- **THEN** responde con el contenido generado a partir de la plantilla y del `.env` de la raíz
- **AND** no se escribe ningún `config.js` en disco

#### Scenario: Un cambio en el entorno de desarrollo surte efecto al recargar

- **WHEN** se modifica una variable en el `.env` de la raíz y se recarga la página en desarrollo
- **THEN** la aplicación refleja el nuevo valor

#### Scenario: Agregar una clave requiere editar un solo archivo

- **WHEN** se agrega una variable de configuración nueva
- **THEN** basta con declararla en `config.template.js` para que ambos modos la produzcan

### Requirement: La plantilla de configuración no se publica como asset web

`config.template.js` SHALL NOT formar parte de la salida del build ni ser alcanzable desde el navegador. Es un insumo para producir `config.js`, no un recurso del sitio.

#### Scenario: La plantilla no llega al build

- **WHEN** se construye el bundle de producción
- **THEN** el directorio de salida no contiene `config.template.js`

#### Scenario: La plantilla no se sirve

- **WHEN** un navegador solicita `/config.template.js`
- **THEN** el servidor no la entrega

#### Scenario: El container recibe la plantilla fuera del directorio servido

- **WHEN** se construye la imagen
- **THEN** la plantilla queda en una ruta que nginx no publica
- **AND** el arranque del container la lee desde ahí para generar `config.js`
