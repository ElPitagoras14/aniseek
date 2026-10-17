## MODIFIED Requirements

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
