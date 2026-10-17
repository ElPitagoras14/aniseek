# app-navigation Specification

## Purpose

Define cómo se navega la aplicación autenticada según el ancho de pantalla: sidebar en tablet y escritorio, y barra inferior con menú de cuenta en teléfono, de modo que en el teléfono cada sección principal quede a un tap y al alcance del pulgar.

Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras clave de especificación.

## Requirements

### Requirement: Umbral entre layout móvil y de escritorio

La aplicación SHALL usar un umbral de 768px de ancho de viewport para decidir el layout de navegación: anchos menores a 768px usan el layout móvil y anchos de 768px o más usan el layout de escritorio (sidebar). Este umbral SHALL coincidir con el que ya usan las vistas que adaptan su comportamiento a "móvil".

#### Scenario: Teléfono usa layout móvil

- **WHEN** un usuario autenticado abre la app en un viewport de 390px de ancho
- **THEN** se muestra la barra de navegación inferior
- **AND** no se muestra el sidebar

#### Scenario: Tablet usa sidebar

- **WHEN** un usuario autenticado abre la app en un viewport de 820px de ancho
- **THEN** se muestra el sidebar
- **AND** no se muestran la barra inferior ni el header móvil

#### Scenario: Escritorio usa sidebar

- **WHEN** un usuario autenticado abre la app en un viewport de 1280px de ancho
- **THEN** se muestra el sidebar
- **AND** no se muestran la barra inferior ni el header móvil

#### Scenario: El cambio de ancho actualiza el layout

- **WHEN** el viewport cruza los 768px (por rotación o redimensionado)
- **THEN** el layout cambia al correspondiente sin recargar la página

### Requirement: Barra de navegación inferior

En el layout móvil, la aplicación SHALL mostrar una barra fija en el borde inferior con exactamente estas secciones, en este orden, cada una con ícono y etiqueta: Home, Search, Saved, Calendar y Downloads. Tocar una sección SHALL navegar a ella con un solo tap.

#### Scenario: Navegación con un tap

- **WHEN** el usuario toca "Saved" en la barra inferior
- **THEN** la app navega a la sección Saved sin abrir ningún menú intermedio

#### Scenario: La barra permanece visible

- **WHEN** el usuario hace scroll en cualquier página de la app autenticada, incluido el detalle de un anime
- **THEN** la barra inferior sigue visible en el borde inferior

#### Scenario: El contenido no queda tapado

- **WHEN** el usuario hace scroll hasta el final de una página
- **THEN** el último elemento del contenido queda visible por encima de la barra inferior

### Requirement: Indicación de sección activa

La navegación SHALL indicar visualmente la sección en la que se encuentra el usuario, tanto en la barra inferior como en el sidebar de escritorio. La indicación SHALL también exponerse a tecnologías de asistencia.

#### Scenario: Sección activa en la barra inferior

- **WHEN** el usuario está en Calendar en el layout móvil
- **THEN** el ítem Calendar de la barra inferior se ve resaltado y está marcado como página actual
- **AND** ningún otro ítem aparece resaltado

#### Scenario: Sección activa en el sidebar

- **WHEN** el usuario está en Downloads con el sidebar visible
- **THEN** el ítem Downloads del sidebar se ve resaltado

### Requirement: Menú de cuenta en el header móvil

En el layout móvil, el header superior SHALL mostrar la marca de la app a la izquierda y un botón de cuenta a la derecha, y SHALL NOT mostrar un botón para abrir el sidebar. El botón de cuenta SHALL abrir un menú con el nombre de usuario y su rol, y las opciones Instance Settings, Profile, Storage, User Management y Sign out. Instance Settings y User Management SHALL aparecer solo para usuarios con rol `admin` u `owner`. Las secciones deshabilitadas SHALL NOT aparecer en este menú.

#### Scenario: Acceso a una sección secundaria

- **WHEN** el usuario toca el botón de cuenta y elige "Storage"
- **THEN** la app navega a Storage y el menú se cierra

#### Scenario: Admin accede a Instance Settings desde el menú de cuenta

- **WHEN** un `admin` toca el botón de cuenta y elige "Instance Settings"
- **THEN** la app navega a Instance Settings y el menú se cierra

#### Scenario: Member no ve las opciones de administración

- **WHEN** un `member` abre el menú de cuenta
- **THEN** el menú no incluye Instance Settings ni User Management

#### Scenario: Cierre de sesión con confirmación

- **WHEN** el usuario elige "Sign out" en el menú de cuenta
- **THEN** se pide confirmación antes de cerrar la sesión
- **AND** cancelar mantiene la sesión abierta

#### Scenario: Sin acceso al sidebar en móvil

- **WHEN** el usuario está en el layout móvil
- **THEN** no existe ningún control que abra el sidebar como panel lateral

### Requirement: Respeto del área segura inferior

La barra inferior SHALL quedar por encima del área reservada por el sistema en dispositivos con indicador de inicio o esquinas redondeadas, de modo que sus ítems no se superpongan con los gestos del sistema.

#### Scenario: Dispositivo con indicador de inicio

- **WHEN** la app se abre en un dispositivo con área segura inferior distinta de cero
- **THEN** los ítems de la barra inferior quedan completamente por encima de esa área

### Requirement: Navegación consistente en la página no encontrada

Cuando un usuario autenticado llega a una ruta inexistente, la aplicación SHALL mostrar la misma navegación que en el resto de la app autenticada según el layout vigente.

#### Scenario: 404 autenticado en móvil

- **WHEN** un usuario autenticado abre una ruta inexistente en un viewport de 390px
- **THEN** se muestra el mensaje de página no encontrada junto con el header móvil y la barra inferior
