## Why

Con la navegación móvil resuelta (`app-navigation`), el problema que queda en el teléfono está dentro de las vistas: las tablas de Episodes, Downloads y Storage tienen anchos mínimos mayores que la pantalla, así que acciones esenciales (descargar un episodio, ver el estado de una descarga, borrar un anime del almacenamiento) quedan fuera de la vista y solo se alcanzan deslizando de costado. Además, la lista de episodios tiene su propio scroll anidado y el póster del detalle ocupa casi una pantalla entera antes del contenido.

## What Changes

- **Episodes** (detalle de anime): bajo 768px las filas muestran `#`, nombre, estado de descarga y acciones (descargar, reproducir) dentro del ancho de pantalla, con columnas más angostas; la lista usa el scroll de la página en lugar de un contenedor con scroll propio. Desde 768px se mantiene el comportamiento actual.
- **Downloads**: bajo 768px cada descarga se muestra como tarjeta (póster chico, título, episodio, tamaño, estado/progreso y menú de acciones) en lugar de una fila de tabla con scroll horizontal.
- **Storage**: bajo 768px la tabla oculta la columna `#` y trunca el título para que tamaño y borrar queden visibles.
- **Detalle de anime**: bajo 768px el póster se muestra compacto junto al estado y las estadísticas, en lugar de ocupar todo el ancho.
- Sin cambios desde 768px en ninguna vista.

## Capabilities

### New Capabilities
- `mobile-views`: comportamiento de las vistas de contenido (detalle de anime, episodios, descargas, almacenamiento) bajo el umbral móvil: sin scroll horizontal, acciones siempre alcanzables y scroll único de página.

### Modified Capabilities
<!-- Ninguna: `app-navigation` no cambia; este change reutiliza su umbral de 768px. -->

## Impact

- Frontend únicamente: `features/anime/components/` (`episodes-table.tsx`, `anime-poster-panel.tsx`, `anime-detail-skeleton.tsx`), `features/downloads/components/` (`downloads-list.tsx`, `download-row.tsx`, `download-row-skeleton.tsx`), `features/storage/components/storage-table.tsx`.
- Sin cambios de backend ni API. Sin dependencias nuevas (`useWindowVirtualizer` ya está en `@tanstack/react-virtual`).
- Release: sale junto con `mobile-bottom-navigation` en el mismo PR; el bump de `VERSION` a 2.2.0 ya hecho cubre ambos.
