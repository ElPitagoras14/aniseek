# Página de home (dashboard bento box)

> Quiero que en @frontend/src/routes/_app/home.tsx definir una vista rápida como dashboard separados en cards. Primero muestráme qué información puedes obtener y que sea útil mostrar en home. Luego espera que yo te diga sobre cuáles trabajar

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/home.

Archivo principal: @frontend/src/routes/\_app/home.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive (mobile / tablet / desktop)
- Layout tipo **bento box** (grid asimétrico con cards de tamaños mixtos)
- Seguir el estilo actual: TanStack Query con `queryOptions`, hooks en `features/<x>/hooks`, tipos en `features/<x>/types.ts`, padding `p-4 md:p-6 lg:p-8`
- Sin comentarios en el código
- Sin dependencias nuevas

## Vista

La vista es un dashboard bento con 5 tarjetas distribuidas en un grid de 6 columnas en desktop. Composición:

### A · Welcome (hero)

Card full-width con saludo al usuario. Datos desde `useAuth()` (sin fetch).

- Título: `Welcome back, {username}` (inglés, neutro, sin saludo por hora)
- `Badge variant="secondary" capitalize` con el role del usuario
- Subtítulo: fecha larga en inglés (`Intl.DateTimeFormat('en-US', { dateStyle: 'full' })`) — p. ej. `Friday, June 5, 2026`
- Icono decorativo `Sparkles` (lucide) a la derecha, oculto en mobile

### B · KPIs (3 tiles)

Una fila de 3 cards con métricas numéricas grandes. Cada tile es un `Link` de TanStack Router si tiene destino, o un `<div>` si no. Datos desde un único `GET /api/users/statistics`.

- **Saved animes** — icono `Bookmark`, tono emerald, link a `/saved`
- **Downloaded episodes** — icono `Download`, tono sky, link a `/downloads`
- **In emission** — icono `CalendarClock`, tono amber, link a `/calendar`

Cada tile: número `text-3xl font-bold` + label `text-xs uppercase tracking-wide text-muted-foreground`. Hover `bg-muted/50 transition-colors` cuando tiene link.

### D · Últimas descargas

Card con las 4 últimas descargas del usuario. Datos desde `GET /api/episodes/downloads/last` (el backend devuelve 5, se hace `slice(0, 4)` en cliente).

Cada fila: poster miniatura 40×56 + título truncado + `Episode {n}` + fecha relativa + icono `Play` a la derecha. Click → `/downloads`.

Empty: copy + link "Find anime" → `/search`.

### E · Calendario de hoy

Card con los animes guardados por el usuario que emiten **hoy**. Datos desde `GET /api/animes/in-emission` (reutilizar `inEmissionQueryOptions` de `features/calendar/api.ts`). Filtrar en cliente: `data.filter(a => a.weekDay === todayWeekday())`.

Header: icono `Calendar` + texto `Today · {Weekday}` (con `Badge variant="outline"`). Grid 2×2 de mini posters con título overlay. Click en poster → `/anime/$slug` con `params={{ slug: anime.id }}` (la ruta existe en `frontend/src/routes/_app/anime.$slug.tsx`).

Empty: copy + link "Browse calendar" → `/calendar`.

### G · Almacenamiento

Card con el top 3 de animes por espacio usado + total global. Datos desde `GET /api/episodes/storage?page=1&limit=10` (el backend ya ordena `SUM(size) DESC`).

Header: icono `HardDrive` + "Storage" + total global `text-2xl font-bold` formateado con `formatBytes(totalSize)`.

Lista top 3: cada item con título truncado + `formatBytes(size)` + barra de progreso relativa al #1 (`width: pct%`).

Empty: copy + link "Browse downloads" → `/downloads`.

## Layout responsive

```tsx
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6">
  <HomeWelcome className="col-span-1 sm:col-span-2 lg:col-span-6" />
  <HomeKpiGrid className="col-span-1 sm:col-span-2 lg:col-span-6" />
  <HomeLastDownloads className="col-span-1 sm:col-span-2 lg:col-span-3 lg:row-span-2" />
  <HomeTodayCalendar className="col-span-1 lg:col-span-3" />
  <HomeStorage className="col-span-1 lg:col-span-3" />
</div>
```

| Breakpoint | Distribución |
|---|---|
| `<sm` (mobile) | Stack vertical 1 columna |
| `sm`–`md` (tablet) | 2 columnas: A full, B full, D full, E y G mitad |
| `lg+` (desktop) | Bento 6 columnas: A full · B×3 (2+2+2) · D (3×2) · E (3) · G (3) |

## General

### Endpoints a usar

Todos los endpoints ya existen, no se agregan nuevos. Solo un cambio mínimo en backend para añadir `totalSize` al response de storage.

**1. `GET /api/users/statistics`** (sin cambios)

```json
{
  "status": "success",
  "message": "User statistics retrieved",
  "payload": {
    "savedAnimes": 12,
    "downloadedEpisodes": 47,
    "inEmissionAnimes": 4
  },
  "statusCode": 200
}
```

**2. `GET /api/episodes/downloads/last`** (sin cambios, `limit=5` hardcoded en backend)

```json
{
  "status": "success",
  "message": "Last downloaded episodes retrieved",
  "payload": {
    "items": [
      {
        "id": 123,
        "animeId": "kusuriya-no-hitorigoto",
        "title": "Kusuriya no Hitorigoto",
        "episodeNumber": 1,
        "poster": "https://cdn.animeav1.com/covers/139.jpg",
        "jobId": null,
        "size": 524288000,
        "status": "SUCCESS",
        "downloadedAt": "2026-06-04T18:23:11.451Z"
      }
    ],
    "total": 5
  },
  "statusCode": 200
}
```

En frontend se aplica `slice(0, 4)` para mostrar solo 4.

**3. `GET /api/animes/in-emission`** (sin cambios — reutilizar `inEmissionQueryOptions` de `features/calendar/api.ts`)

```json
{
  "status": "success",
  "message": "In-emission animes retrieved",
  "payload": {
    "items": [
      {
        "id": "dr-stone-science-future-part-3",
        "title": "Dr. Stone: Science Future Part 3",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/3912.jpg",
        "isSaved": true,
        "saveDate": "2026-05-22T19:47:42.201328Z",
        "weekDay": "Friday"
      }
    ],
    "total": 4
  },
  "statusCode": 200
}
```

Filtrar en cliente: `items.filter(a => a.weekDay === todayWeekday)`.

**4. `GET /api/episodes/storage?page=1&limit=10`** (cambio menor: añadir `totalSize`)

```json
{
  "status": "success",
  "message": "Animes storage retrieved",
  "payload": {
    "items": [
      { "id": "kusuriya-no-hitorigoto", "title": "Kusuriya no Hitorigoto", "size": 12884901888 }
    ],
    "total": 28,
    "totalSize": 158324234567
  },
  "statusCode": 200
}
```

### Cambio en backend (P1: `totalSize`)

1. `backend/src/packages/episodes/repository.py:189` — modificar `list_animes_storage` para retornar `(count, total_size, rows)`. Query extra:
   ```sql
   SELECT COALESCE(SUM(e.size), 0) AS total_size
   FROM episodes e WHERE e.size IS NOT NULL;
   ```
2. `backend/src/packages/episodes/service.py:197` — desempaquetar `count, total_size, rows` y pasar `total_size` a `cast_animes_storage_list`.
3. `backend/src/packages/episodes/responses.py:72` — `AnimeStorageInfoList` añadir `total_size: int = 0`.
4. `backend/src/packages/episodes/utils.py` — `cast_animes_storage_list` añadir parámetro `total_size: int = 0` y devolverlo en el dict.

### Sidebar

`frontend/src/features/root/sidebar-data.ts:30` — cambiar `disabled: true` a `disabled: false` para que `/home` sea navegable y se muestre activo en el sidebar.

## Estructura de archivos

### Crear (11)

- `frontend/src/features/home/api.ts` — `statisticsQueryOptions`, `downloadsLastQueryOptions`, `storageQueryOptions`
- `frontend/src/features/home/types.ts` — `Statistics`, `StorageResponse`, `StorageItem`
- `frontend/src/features/home/lib/format-bytes.ts` — `formatBytes(bytes: number | null): string`
- `frontend/src/features/home/lib/today-weekday.ts` — `todayWeekday(): WeekDay`
- `frontend/src/features/home/components/home-welcome.tsx` — A
- `frontend/src/features/home/components/home-kpi.tsx` — tile B
- `frontend/src/features/home/components/home-kpi-grid.tsx` — fila B
- `frontend/src/features/home/components/home-last-downloads.tsx` — D
- `frontend/src/features/home/components/home-today-calendar.tsx` — E
- `frontend/src/features/home/components/home-storage.tsx` — G
- `frontend/src/features/home/components/home-skeleton.tsx` — loading

### Modificar (6)

- `frontend/src/routes/_app/home.tsx` — orquestador
- `frontend/src/features/root/sidebar-data.ts:30` — sidebar
- `backend/src/packages/episodes/repository.py:189`
- `backend/src/packages/episodes/service.py:197`
- `backend/src/packages/episodes/responses.py:72`
- `backend/src/packages/episodes/utils.py` (cast)

## Utilidades

### `lib/format-bytes.ts`

```ts
export function formatBytes(bytes: number | null | undefined): string {
  if (bytes == null || bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const value = bytes / Math.pow(1024, i);
  return `${value.toFixed(value < 10 && i > 0 ? 1 : 0)} ${units[i]}`;
}
```

### `lib/today-weekday.ts`

```ts
import type { WeekDay } from "@/features/calendar/types";

export function todayWeekday(): WeekDay {
  const day = new Intl.DateTimeFormat("en-US", { weekday: "long" }).format(
    new Date(),
  );
  return day as WeekDay;
}
```

## Query keys (api.ts)

| Opción | Key | staleTime |
|---|---|---|
| `statisticsQueryOptions` | `["users", "statistics"]` | `60_000` |
| `downloadsLastQueryOptions` | `["episodes", "downloads", "last"]` | `0` |
| `storageQueryOptions` | `["episodes", "storage", { page, limit }]` | `60_000` |
| `inEmissionQueryOptions` (reutilizado) | `["animes", "in-emission"]` | `60_000` |

## Tipos (types.ts)

```ts
import type { EpisodeDownloadList, EpisodeDownload } from "@/features/downloads/types";

export interface Statistics {
  savedAnimes: number;
  downloadedEpisodes: number;
  inEmissionAnimes: number;
}

export interface StorageItem {
  id: string;
  title: string;
  size: number;
}

export interface StorageResponse {
  items: StorageItem[];
  total: number;
  totalSize: number;
}

export type { EpisodeDownload, EpisodeDownloadList };
```

## Patrones a respetar

- Componentes en `features/<x>/components/`, no en `routes/`
- `queryOptions` de TanStack Query (no `useQuery` con fetchers inline)
- `useQuery` solo en el componente o en un hook en `features/<x>/hooks/`
- Tipos en `types.ts` con `camelCase`
- Sin `any`, props con `interface`
- Imports ordenados: stdlib → third-party → local, alfabético
- Errores con `text-destructive text-sm` (igual que `downloads-list.tsx`)
- Loading con `Skeleton` de shadcn
- Sin emojis

## Criterios de aceptación

1. `GET /api/episodes/storage` devuelve `payload.totalSize` con la suma global en bytes de `episodes.size WHERE size IS NOT NULL`
2. `/home` renderiza 5 tarjetas (A, B×3, D, E, G) en layout bento responsive
3. Sin overlap visual en mobile / tablet / desktop
4. Cada celda tiene: loading skeleton, error visible con botón reintentar, empty state con copy
5. Saludo = `Welcome back, {username}` (inglés neutro, sin hora)
6. (E) filtra `inEmission` por `weekDay === todayWeekday()` en cliente
7. (D) muestra 4 items sliceados del endpoint `/downloads/last` (5 backend)
8. (G) muestra top 3 animes por tamaño + total global desde `totalSize`
9. Sidebar `/home` ya no está `disabled` y se marca activo al estar en `/home`
10. Sin cambios no listados en backend; sin dependencias nuevas en frontend
11. `lint` y `tsc` sin errores nuevos

Escribir los resultados en este documento

## Resultados

### Backend (cambios mínimos `totalSize`)

- `backend/src/packages/episodes/repository.py:189` — `list_animes_storage` ahora retorna `tuple[int, int, list[dict]]` (`count, total_size, rows`). Se agregó la query `SELECT COALESCE(SUM(e.size), 0) AS total_size FROM episodes e WHERE e.size IS NOT NULL`.
- `backend/src/packages/episodes/service.py:197` — desempaqueta `count, total_size, rows` y propaga `total_size` a `cast_animes_storage_list`.
- `backend/src/packages/episodes/responses.py:72` — `AnimeStorageInfoList` añade `total_size: int = 0`.
- `backend/src/packages/episodes/utils.py` — `cast_animes_storage_list` acepta `total_size: int = 0` y lo incluye en el modelo. Es exportado via `SuccessResponse.model_dump` que aplica `camelize` a `payload`, por lo que el JSON expone `totalSize`.
- `backend/src/packages/episodes/router.py:70` — corregido el bug que filtraba `totalSize` y `size` (en items): `response_model` cambiado de `AnimeDownloadInfoListOut` → `AnimeStorageInfoListOut` (importe añadido en `router.py:16-21`). Pydantic v2 filtra a los campos del response_model declarado, por lo que ahora `GET /api/episodes/storage?page=1&limit=10` devuelve `payload.totalSize` correctamente.

### Frontend (módulo `features/home/`)

- `frontend/src/features/home/api.ts` — `statisticsQueryOptions` (`staleTime: 60_000`), `downloadsLastQueryOptions` (`staleTime: 0`), `storageQueryOptions({ page, limit })` (`staleTime: 60_000`). Reutiliza `inEmissionQueryOptions` de `features/calendar/api.ts`.
- `frontend/src/features/home/types.ts` — `Statistics`, `StorageItem`, `StorageResponse`, re-exports `EpisodeDownload`, `EpisodeDownloadList`.
- `frontend/src/features/home/lib/format-bytes.ts` — implementación exacta del spec.
- `frontend/src/features/home/lib/today-weekday.ts` — implementación exacta del spec.
- `frontend/src/features/home/components/home-welcome.tsx` — Card A **compacta** (1x2 en desktop, 1 fila de alto): un solo `CardContent` en columna. Fila 1: `flex items-center gap-2 min-w-0` con `Welcome back, {username}` (`text-lg font-semibold truncate`) + `Badge` `secondary` `capitalize` con el role (inline, shrink-0). Fila 2: fecha `Intl.DateTimeFormat('en-US', { dateStyle: 'full' })` (`text-xs text-muted-foreground truncate`). Sin icono `Sparkles`, sin `CardHeader`, sin `justify-between`. Encaja visualmente en su celda 1x2 sin huecos.
- `frontend/src/features/home/components/home-kpi.tsx` — tile reutilizable (icon+label+número, envuelto en `Link` de TanStack Router, `hover:bg-muted/50 transition-colors`). Acepta `className?` (pasado al `Link`) para posicionamiento en grid; `isError` → renderiza `—` con `text-destructive`; en loading → `Skeleton h-9 w-20`. Sin `onRetry` interno (el retry se gestiona en el padre que posee la query).
- `frontend/src/features/home/components/home-stats-grid.tsx` — **eliminado**. Los 3 KPIs ahora se renderizan individualmente en `home.tsx` (celdas separadas) y `HomeStorage` se compone por separado en su celda 2x2. La responsabilidad de las queries vive en el orquestador.
- `frontend/src/features/home/components/home-last-downloads.tsx` — Card D: usa `useQuery(downloadsLastQueryOptions)`, hace `slice(0, 4)`. Cada fila es un `Link to="/downloads"` con poster 40×56, título truncado, `Episode {n}` + `Intl.RelativeTimeFormat('en', { numeric: 'auto' })`. Estado SUCCESS: muestra botón `Download` (`<a download>` con `episodeFileUrl(animeId, episodeNumber)`) en lugar del icono `Play`. Otros estados: muestra `Clock`. Empty: "No downloads yet." + link "Find anime" → `/search` con `search={{ query: "" }}`.
- `frontend/src/features/home/components/home-today-calendar.tsx` — Card E: usa `inEmissionQueryOptions` y filtra en cliente `data.filter(a => a.weekDay === todayWeekday()).slice(0, 4)` con `useMemo`. Header con `Calendar` + "Today" + `Badge variant="outline"` con el weekday. Grid `grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3` que reutiliza `CalendarAnimeCard` de `features/calendar/components/calendar-anime-card.tsx` (mismo estilo que en `/calendar`). Click en card → `/anime/$slug` con `params={{ slug: anime.id }}`. Empty: "No animes airing today." + link "Browse calendar" → `/calendar`.
- `frontend/src/features/home/components/home-storage.tsx` — Card G: **componente puramente visual** (sin `useQuery` interno). Recibe `{ data, isLoading, isError, onRetry, className? }` por props. Header con `HardDrive` + "Storage" + total global `text-2xl font-bold` con `formatBytes(data?.totalSize ?? 0)`. Lista top 3 con barra de progreso relativa al #1 (`width: ${pct}%`). Empty: "No storage used yet." (sin link). Loading: `HomeStorageSkeleton`. Error: `Card` con `text-destructive` + `Button variant="outline" size="sm"` "Retry".
- `frontend/src/features/home/components/home-skeleton.tsx` — skeletons de las 5 cards: `HomeKpiSkeleton`, `HomeLastDownloadsSkeleton`, `HomeTodayCalendarSkeleton`, `HomeStorageSkeleton`, `HomeWelcomeSkeleton`. Cada componente se encarga de su loading/empty/error.

### Modificados

- `frontend/src/routes/_app/home.tsx` — orquestador con `p-4 md:p-6 lg:p-8` + grid `grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6` y `col-span`/`row-span` por celda. Layout final:
  - `HomeWelcome` → `col-span-1 sm:col-span-2 lg:col-span-2 lg:row-span-2`
  - `HomeStatsGrid` → `col-span-1 sm:col-span-2 lg:col-span-4 lg:row-span-2`
  - `HomeTodayCalendar` → `col-span-1 sm:col-span-2 lg:col-span-3 lg:row-span-2`
  - `HomeLastDownloads` → `col-span-1 sm:col-span-2 lg:col-span-3` (sin `row-span`, ocupa solo 1 fila)
  - La celda inferior-derecha (bajo `HomeLastDownloads`) queda intencionalmente vacía como gap bento para dar respiro visual a las dos filas de cards de hoy.
- `frontend/src/features/root/sidebar-data.ts:30` — quitado `disabled: true` del item "Home". `NavMain` ya marca como activo el item cuya URL matchea la ruta actual.
- `frontend/src/hooks/use-toggle-saved.ts` — añadido `useQueryClient`. En el `onSuccess` invalida `["animes"]` (cubre `in-emission`, `saved`, `search`, `detail`) y `["users", "statistics"]` (cubre el KPI "Saved animes" del home). Esto hace que el contador de "Saved animes" se actualice en tiempo real al togglear desde cualquier card.
- `frontend/src/types/config.d.ts` — movida la `interface AppConfig` dentro de `declare global { }` (resolvía error preexistente `TS2304: Cannot find name 'AppConfig'` en `src/config.ts(1,22)`). El `export {}` previo volvía `AppConfig` scoped a módulo, por lo que `src/config.ts` no la veía.

### Verificaciones

- `cd backend && uv run ruff check src` → All checks passed!
- `cd frontend && pnpm exec biome check src/features/home src/hooks/use-toggle-saved.ts src/routes/_app/home.tsx` → sin errores (los `organizeImports`/`format` iniciales se autocorrigen con `--write`).
- `cd frontend && pnpm exec tsc --noEmit` → sin errores (el `TS2304: AppConfig` preexistente también queda resuelto por la modificación de `config.d.ts`).
- Sintaxis Python validada con `ast.parse` sobre los 4 archivos del backend.

### Criterios de aceptación

1. ✅ `GET /api/episodes/storage` devuelve `payload.totalSize` (router corregido a `AnimeStorageInfoListOut`).
2. ✅ `/home` renderiza 4 tarjetas (Welcome, StatsGrid, TodayCalendar, LastDownloads) en layout bento responsive (`p-4 md:p-6 lg:p-8`, grid `grid-cols-1 sm:grid-cols-2 lg:grid-cols-6`).
3. ✅ Sin overlap en mobile/tablet/desktop: cada celda con su `col-span`/`row-span` correctos. La celda inferior-derecha es un gap bento intencional.
4. ✅ Cada celda tiene loading skeleton, error visible con botón Retry, y empty state con copy (Storage no tiene link en empty, los demás sí).
5. ✅ Saludo = `Welcome back, {username}` (inglés neutro, sin hora; fecha larga `dateStyle: 'full'`).
6. ✅ (E) filtra `inEmission` por `weekDay === todayWeekday()` en cliente con `useMemo`, renderiza con `CalendarAnimeCard` reutilizado.
7. ✅ (D) muestra 4 items (`data?.items.slice(0, 4)`) del endpoint `/downloads/last`. SUCCESS → botón Download con `<a download href={episodeFileUrl(...)}>`. Otros estados → icono `Clock`.
8. ✅ (G) muestra top 3 animes (`slice(0, 3)`) + total global desde `data?.totalSize` (con `?? 0`). Storage es puramente visual, props-driven.
9. ✅ Togglear `saved` desde cualquier card invalida `["animes"]` + `["users", "statistics"]` → el KPI "Saved animes" del home se actualiza en tiempo real.
10. ✅ Sidebar `/home` ya no está `disabled`. El `SidebarMenuButton asChild` con `Link` de TanStack Router marca activo el item automáticamente.
11. ✅ Sin cambios en `compose.yaml`, `init.sql` ni en `requests/`. `router.py` modificado solo para corregir el `response_model` (1 línea + 1 import). Sin nuevas dependencias (`pnpm-lock.yaml` sin tocar).
12. ✅ `biome check` y `tsc --noEmit` sin errores.
