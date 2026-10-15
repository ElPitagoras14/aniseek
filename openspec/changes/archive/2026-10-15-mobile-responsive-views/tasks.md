## 1. Downloads

- [x] 1.1 Convertir `DownloadRow` en tarjeta bajo `md` (póster `w-12`, título `line-clamp-2`, línea de metadatos con episodio y tamaño, estado/progreso, menú) manteniendo `md:grid ${ROW_COLS}`; verificar en 390px que estado, tamaño y menú son visibles y en 1280px que la fila es idéntica a la actual
- [x] 1.2 En `DownloadsList` ocultar el encabezado bajo `md` y mover los `min-w` a `md:`; ajustar `DownloadRowSkeleton` a la misma estructura; verificar que `/downloads` en 390px no tiene contenedores con desborde horizontal (incluido el estado de carga)

## 2. Episodes

- [x] 2.1 Separar el cuerpo de `EpisodesTable` en `EpisodeRowsContained` (actual) y `EpisodeRowsWindow` (`useWindowVirtualizer` con `scrollMargin` recalculado ante cambios de tamaño), elegidos con `useIsMobile`; verificar en 390px que al desplazar se mueve la página y no un contenedor interno
- [x] 2.2 Columnas bajo `md`: `grid-cols-[3rem_1fr_2.75rem_4.5rem]` conservando `#` y sin `min-w`; desde `md` las columnas actuales; verificar en 390px que `#`, descargar y reproducir están dentro de la pantalla y que tocar descargar encola el episodio
- [x] 2.3 Verificar con un anime de muchos episodios que en 390px el último episodio queda visible sobre la barra inferior y que en 1280px se mantiene el contenedor de 60vh

## 3. Storage

- [x] 3.1 Ocultar la columna `#` bajo `md`, truncar el título en móvil y corregir los `colSpan` a 4; verificar en 390px que el botón de borrar está dentro de la pantalla y que no hay desborde horizontal en la tabla

## 4. Detalle de anime

- [x] 4.1 Reestructurar `AnimePosterPanel` con póster compacto bajo `md` (`grid-cols-[7rem_1fr]`, estado y stats a la derecha, `md:contents` para escritorio); verificar en 390x844 que el título del anime es visible sin scroll y el botón de guardar funciona
- [x] 4.2 Ajustar `AnimeDetailSkeleton` a la misma estructura; verificar en 390px que el skeleton no salta de layout al cargar los datos

## 5. Verificación

- [x] 5.1 Recorrer Downloads, Storage, detalle (Information y Episodes) en 390px, 820px y 1280px: sin desborde horizontal en 390px y sin cambios visuales en 820px y 1280px respecto de la versión anterior
- [x] 5.2 Ejecutar `biome check`, typecheck (sin errores nuevos) y `vite build` sin errores
