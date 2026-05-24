# Página de calendário

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/calendar.

Archivo principal: @frontend/src/routes/\_app/calendar.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive

## Vista

La vista se va a componer de 2 secciones principales:

1. La sección de título/header
2. Una tabla/lista de 7 columnas con los nombres de los días de la semana sin fecha en particular. Cada item de la columna es un anime con su poster y el nombre del anime. Al dar clic en el anime se va a redireccionar a la página de detalles del anime.

## General

Los días de la semana se obtienen del siguiente endpoint:

- Endpoint: `/api/animes/in-emission`
- Método: `GET`

Ejemplo de respuesta:

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
        "weekDay": "Thursday"
      },
      {
        "id": "rezero-kara-hajimeru-isekai-seikatsu-4th-season",
        "title": "Re:Zero kara Hajimeru Isekai Seikatsu 4th Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/3968.jpg",
        "isSaved": true,
        "saveDate": "2026-05-22T19:52:16.226518Z",
        "weekDay": "Wednesday"
      }
    ],
    "total": 2
  },
  "statusCode": 200
}
```

Escribir los resultados en este documento

## Resultados

**Fecha:** 2026-05-23 — Implementado y verificado en browser.

**Archivos creados:**
- `frontend/src/features/calendar/types.ts` — `WeekDay`, `InEmissionAnime`, `InEmissionList`, `InEmissionResponse`
- `frontend/src/features/calendar/api.ts` — `inEmissionQueryOptions` (TanStack Query, `staleTime: 60_000`)
- `frontend/src/features/calendar/lib/week-days.ts` — `WEEK_DAYS`, `getTodayWeekDay()`, `groupAnimesByWeekDay()`
- `frontend/src/features/calendar/components/calendar-header.tsx`
- `frontend/src/features/calendar/components/calendar-anime-card.tsx` — poster + título, sin badge ni bookmark
- `frontend/src/features/calendar/components/calendar-day-column.tsx` — columna con highlight si es hoy
- `frontend/src/features/calendar/components/calendar-grid-skeleton.tsx`
- `frontend/src/features/calendar/components/calendar-grid.tsx` — grid responsive, maneja loading/error/data

**Archivos modificados:**
- `frontend/src/routes/_app/calendar.tsx` — reemplazado placeholder por orquestador

**Verificación (browsermcp):**
- ✅ 7 columnas Lunes→Domingo renderizadas
- ✅ Columna del día actual (Sábado) resaltada con color primary
- ✅ Cards muestran solo poster + título (sin badge, sin botón guardar)
- ✅ Columnas vacías se renderizan con la misma altura mínima, sin texto placeholder
- ✅ Click en anime navega a `/anime/:slug` correctamente
- ✅ Sin errores en consola
- ✅ lint y tsc sin errores nuevos

**Decisiones tomadas:**
- Orden lunes→domingo (convención latina)
- Grid responsive: `grid-cols-1 sm:2 md:3 lg:4 xl:7`
- Componente nuevo `CalendarAnimeCard` en lugar de reutilizar `AnimeCard` de search (más compacto, sin controles)