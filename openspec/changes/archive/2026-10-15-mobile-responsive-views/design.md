## Context

- Las tablas de Downloads y Episodes son grillas CSS dentro de un `overflow-x-auto` con `min-w-[800px]` / `min-w-[500px]`; Storage usa el `Table` de shadcn (que ya trae su propio `overflow-x-auto`).
- `EpisodesTable` virtualiza con `useVirtualizer` sobre un contenedor de `h-[60vh]` con scroll propio.
- `AnimePosterPanel` apila póster (`aspect-2/3 w-full`), bloque de estado y stats; en móvil la grilla de `anime.$slug.tsx` es de una columna, así que el póster ocupa todo el ancho.
- El umbral móvil es 768px (`md`), compartido por CSS (`md:`) y JS (`useIsMobile`), según `app-navigation`.

## Goals / Non-Goals

**Goals:**
- Un solo componente por vista con variantes por breakpoint; desde `md` el DOM visual queda igual que hoy.
- Ninguna acción fuera de la pantalla en 390px.

**Non-Goals:**
- Cambiar Saved, Search, Calendar, Home o la paginación (ya entran en 390px).
- Rediseñar las vistas de escritorio.
- Gestos (swipe para borrar, pull to refresh).

## Decisions

### D1 - Variantes responsive por CSS, no por `useIsMobile`, salvo en la virtualización

Downloads, Storage y el póster se resuelven con clases `md:` sobre el mismo markup: sin parpadeo inicial (ver D2 de `mobile-bottom-navigation`) y sin duplicar componentes. La única excepción es la lista de episodios (D3), donde el tipo de virtualizador depende del layout y eso solo se puede decidir en JS.

### D2 - Downloads: la fila se vuelve tarjeta

`DownloadRow` pasa a ser `flex` bajo `md` y `md:grid ${ROW_COLS}` desde `md`:

```
< md                                         ≥ md (sin cambios)
┌──┐ Título (line-clamp-2)          ⋮        Poster | Title | Ep | Status | Size | ⋮
│▓▓│ Ep 2 · 463 MB
└──┘ [estado / barra de progreso / ⬇]
```

- Póster `w-12` fijo en móvil; título `line-clamp-2`; episodio y tamaño en una línea de metadatos que bajo `md` reemplaza a las celdas propias (estas usan `hidden md:block`).
- El bloque de estado/progreso se reutiliza tal cual; en móvil ocupa el ancho de la columna de texto y se alinea a la izquierda.
- `DownloadsList`: el encabezado de columnas es `hidden md:grid` y los `min-w-[700px]/[800px]` pasan a `md:min-w-[…]`. `DownloadRowSkeleton` sigue la misma estructura.

*Alternativa descartada:* un `DownloadCard` aparte con `md:hidden` y la fila con `hidden md:grid`. Duplica la lógica de estado en vivo y monta dos árboles por elemento.

### D3 - Episodes: virtualizador de ventana en móvil

Se separa el cuerpo de la lista en dos componentes con la misma fila:
- `EpisodeRowsContained`: el actual (`useVirtualizer` + contenedor `h-[60vh]`), usado desde `md`.
- `EpisodeRowsWindow`: `useWindowVirtualizer` con `scrollMargin` igual al `offsetTop` del contenedor de la lista (medido en un `useLayoutEffect`), usado bajo `md`.

`EpisodesTable` elige con `useIsMobile()`. Los hooks no pueden ser condicionales, por eso son dos componentes. Como `useIsMobile` arranca en `false`, el primer render en móvil usa el contenedor y en el siguiente cambia a ventana: ocurre al montar la pestaña, antes de que el usuario interactúe, y es aceptable.

Columnas: `grid-cols-[3rem_1fr_2.75rem_4.5rem]` bajo `md` (`#`, nombre, estado, acciones; anchos fijos iguales al contenido porque cada fila es su propia grilla y con `auto` el encabezado vacío se desalinearía) y `md:grid-cols-[80px_1fr_120px_160px]` desde `md`. La columna `#` se conserva siempre: muestra el identificador del episodio (`ep.id`, el `episode_number` del scraper, que es el que usa la API de descarga) y no es equivalente a la etiqueta "Episode N", ya que la numeración puede no empezar en 1 (p. ej. animes con episodio 0). Lo que se compacta en móvil es el ancho de las columnas, no su cantidad. El `min-w-[500px]` pasa a `md:min-w-[500px]`. El encabezado sigue presente con las mismas columnas.

El espacio de la barra inferior ya lo reserva `AppShell`, así que el último episodio queda visible al final del scroll de página.

*Alternativa descartada:* mantener el scroll interno y solo compactar columnas (descartado por el usuario: el scroll anidado atrapa el gesto en móvil).

### D4 - Storage: ocultar `#` y truncar

En `StorageTable`, la celda/encabezado `#` es `hidden md:table-cell`; la celda de título usa `max-w-0 w-full truncate` bajo `md` (patrón estándar para que una celda trunque dentro de una tabla de ancho automático) y conserva `max-w-xs truncate` desde `md`. Los `colSpan` de las filas de estado vacío/error se ajustan a 4 para cubrir todas las columnas (hoy usan 3).

### D5 - Póster compacto con `md:contents`

`AnimePosterPanel` pasa a `grid grid-cols-[7rem_1fr] gap-4` bajo `md` y `md:flex md:flex-col` desde `md`. El estado y las stats se envuelven en un `div` con `flex flex-col justify-center gap-3` bajo `md` y `md:contents` desde `md`, de modo que en escritorio el árbol de layout es idéntico al actual. El bloque de estado reduce su tipografía bajo `md` (`text-base md:text-xl`). El botón de guardar se mantiene sobre el póster con un ícono más chico bajo `md`. `AnimeDetailSkeleton` replica la misma estructura.

## Risks / Trade-offs

- [`scrollMargin` desactualizado si el contenido sobre la lista cambia de alto (p. ej. al cargar la imagen del póster)] → Recalcular el offset con un `ResizeObserver` sobre `document.body` o el contenedor de la página, no solo al montar.
- [El cambio de virtualizador al cruzar 768px (rotación) reinicia la posición dentro de la lista] → Aceptable: rotar un teléfono no cruza 768px en los tamaños habituales.
- [Tooltips de estado (`DownloadedIcon`) no aparecen con toque] → Comportamiento existente; el color del ícono sigue comunicando el estado. Fuera de alcance.

## Migration Plan

Cambio solo de frontend. Sale en el mismo PR que `mobile-bottom-navigation`, cubierto por el bump a 2.2.0. Rollback: revertir el PR.
