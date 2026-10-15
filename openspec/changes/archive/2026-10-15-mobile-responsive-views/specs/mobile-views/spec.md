## Purpose

Define cómo se comportan las vistas de contenido de la app autenticada (detalle de anime, episodios, descargas y almacenamiento) en el layout móvil, para que toda la información y acciones sean alcanzables sin scroll horizontal y con un único scroll de página.

Los términos normativos SHALL / SHALL NOT / MUST se mantienen en inglés por ser palabras clave de especificación. "Layout móvil" y "layout de escritorio" se refieren al umbral de 768px definido en `app-navigation`.

## ADDED Requirements

### Requirement: Sin scroll horizontal en vistas de contenido

En el layout móvil, las vistas de episodios, descargas y almacenamiento SHALL NOT requerir scroll horizontal, ni de la página ni de ningún contenedor interno, para ver su información o usar sus acciones.

#### Scenario: Vistas en un teléfono

- **WHEN** el usuario abre Downloads, Storage o la pestaña Episodes de un anime en un viewport de 390px
- **THEN** ningún elemento de esas vistas tiene contenido desbordado horizontalmente
- **AND** todas las acciones de cada elemento están dentro del ancho visible

### Requirement: Lista de episodios en móvil

En el layout móvil, cada episodio SHALL mostrar su identificador (`#`), su nombre, su estado de descarga y las acciones de descargar y reproducir dentro del ancho visible. El identificador SHALL mostrarse siempre, porque no necesariamente coincide con la posición del episodio en la lista (p. ej. animes con episodio 0). La lista SHALL desplazarse con el scroll de la página, sin un contenedor con scroll vertical propio. En el layout de escritorio la lista SHALL conservar su presentación actual.

#### Scenario: Descargar un episodio desde el teléfono

- **WHEN** el usuario abre la pestaña Episodes en un viewport de 390px
- **THEN** el botón de descargar de cada episodio visible está dentro de la pantalla
- **AND** tocarlo encola la descarga de ese episodio

#### Scenario: Scroll único

- **WHEN** el usuario desliza hacia abajo sobre la lista de episodios en el layout móvil
- **THEN** se desplaza la página completa y no un contenedor interno

#### Scenario: Listas largas

- **WHEN** un anime tiene cientos de episodios y el usuario llega al final de la página en el layout móvil
- **THEN** el último episodio es visible y queda por encima de la barra de navegación inferior

### Requirement: Descargas como tarjetas en móvil

En el layout móvil, cada descarga SHALL mostrarse como una tarjeta con póster, título, número de episodio, tamaño, estado o progreso en vivo, y acceso a sus acciones (reintentar, borrar, ver anime). El estado SHALL actualizarse en vivo igual que en el layout de escritorio.

#### Scenario: Descarga en curso en el teléfono

- **WHEN** una descarga está en progreso y el usuario abre Downloads en un viewport de 390px
- **THEN** la tarjeta de esa descarga muestra el porcentaje de progreso actualizándose
- **AND** el menú de acciones de la tarjeta está visible

#### Scenario: Descarga completada en el teléfono

- **WHEN** una descarga está completada en el layout móvil
- **THEN** su tarjeta ofrece la acción de bajar el archivo

### Requirement: Almacenamiento en móvil

En el layout móvil, cada fila de almacenamiento SHALL mostrar el título del anime (truncado si no entra), su tamaño y la acción de borrar dentro del ancho visible.

#### Scenario: Borrar desde el teléfono

- **WHEN** el usuario abre Storage en un viewport de 390px
- **THEN** el botón de borrar de cada anime está dentro de la pantalla

### Requirement: Póster compacto en el detalle de anime

En el layout móvil, el detalle de anime SHALL mostrar el póster en tamaño reducido junto al estado de emisión y las estadísticas de episodios, de modo que el título del anime sea visible sin desplazar la página en un viewport de 390x844. El botón de guardar SHALL seguir disponible sobre el póster.

#### Scenario: Detalle en el teléfono

- **WHEN** el usuario abre el detalle de un anime en un viewport de 390x844
- **THEN** el título del anime está visible sin hacer scroll
- **AND** el póster no ocupa todo el ancho de la pantalla

#### Scenario: Detalle en escritorio sin cambios

- **WHEN** el usuario abre el detalle de un anime en un viewport de 1280px
- **THEN** el póster se muestra a ancho completo de su columna, como antes
