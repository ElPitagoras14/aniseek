# Página de descargas

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/download.

Archivo principal: @frontend/src/routes/\_app/download.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive

## Vista

La vista se va a componer de 2 secciones principales:

1. La sección de título/header con un text input para buscar por el nombre del anime
2. La sección de listado de descargas de animes con paginación.

## General

Las descargas se obtienen del siguiente endpoint:

- Endpoint: `/api/episodes/download`
- Método: `GET`

El progreso de descarga se obtiene de la siguiente endpoint:

- Endpoint: `/api/episodes/stream/status`
- Método: `GET`
- Query Params:
  - `jobIds`: Lista de ids de descargas

Ejemplo de petición:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/episodes/stream/status?job_ids=123%2C432' \
  -H 'accept: application/json'
```

Revisar en @queue/src/tasks/download.py la función `notify_job` para ver el formato de los datos enviados.

### Sección de título/header

Debe tener un input de texto para buscar por el nombre del anime con debounce de 300ms, sin botón de busqueda

### Sección de listado de descargas

Debe tener una lista de filas de descargas con la siguiente estructura (dividido en 3 secciones horizontales):

1. Poster del anime
2. De arriba a abajo:
  2.1. Nombre del anime
  2.2. Número de episodio y tamaño del archivo
  2.3. Barra de progreso
3. De izquierda a derecha:
  3.1. Botón de descarga
  3.2. Botón ghost con icono elipsis que contiene las opciones de: eliminar, reintentar, ver anime

## Lógica de estado

Recomendar en el plan si es mejor abrir 1 SSE por cada episodio o abrir 1 SSE con todas las episodios de un anime.

Los ids enviado son los pendiente que se encuentran en la página actual

---

## Implementación

### Decisiones tomadas

- **Búsqueda**: Se añadió filtro `q` (ILIKE sobre `a.title`) al backend en los 3 layers (router → service → repository). Input con debounce 300ms usando patrón `useRef` + `useLayoutEffect` para estabilizar el callback.
- **SSE**: 1 sola conexión por página con todos los `job_ids` activos (PENDING/GETTING-LINK/DOWNLOADING/RETRYING) separados por coma. Se usa `URLSearchParams` para encoding seguro.
- **Paginación**: Numérica con prev/next. `q` y `page` persisten en search params de la URL. No se renderiza si hay solo 1 página.
- **Acciones por fila**: Descargar archivo (solo SUCCESS via `<a download>`), Eliminar, Reintentar (deshabilitado si activo), Ver anime (Link de TanStack Router).

### Archivos modificados (backend)

- `backend/src/packages/episodes/router.py` — param `q: str | None`, strip de whitespace
- `backend/src/packages/episodes/service.py` — propaga `q`
- `backend/src/packages/episodes/repository.py` — `AND a.title ILIKE :q` con `%q%`

### Archivos creados (frontend)

- `frontend/src/lib/format-bytes.ts`
- `frontend/src/features/downloads/types.ts`
- `frontend/src/features/downloads/api.ts`
- `frontend/src/features/downloads/hooks/use-download-progress.ts`
- `frontend/src/features/downloads/components/downloads-search-input.tsx`
- `frontend/src/features/downloads/components/downloads-header.tsx`
- `frontend/src/features/downloads/components/download-row-skeleton.tsx`
- `frontend/src/features/downloads/components/download-progress.tsx`
- `frontend/src/features/downloads/components/download-row-actions.tsx`
- `frontend/src/features/downloads/components/download-row.tsx`
- `frontend/src/features/downloads/components/downloads-pagination.tsx`
- `frontend/src/features/downloads/components/downloads-list.tsx`

### Archivos modificados (frontend)

- `frontend/src/routes/_app/downloads.tsx` — orquestador completo con `validateSearch`

### Rama

`feature/frontend-migration-and-refactor`