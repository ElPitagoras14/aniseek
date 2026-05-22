# Página de búsqueda de anime

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/search.

Archivo principal: @frontend/src/routes/_app/search.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive

## Vista

La vista se va a componer de 2 partes:

1. La sección de búsqueda
2. La sección de resultados

### Sección de búsqueda

Esta sección debe tener un campo de búsqueda y un botón de buscar.

El botón de buscar debe llamar al siguiente endpoint:

- Endpoint: `/api/animes/search?query=$query`
- Método: `GET`

### Sección de resultados

Esta sección debe mostrar los resultados de la búsqueda.

Cada resultado debe ser una especie de tarjeta bastante ligera con el título, el tipo de anime y la imagen del anime.

La estructura es la siguiente: en la parte superior debe aparecer la imagen del anime, en la parte inferior el título y el tipo de anime.

Dentro de la imagen en la esquina superior derecha debe aparecer un botón de guardado el cual corresponde al ícono de `Bookmark` de lucide. Este ícono está vacío (solo bordes) por defecto y lleno cuando el usuario ha guardado el anime.

El componente debe ser clickeable y debe redireccionar al detalle del anime en la ruta `/anime/$slug`.

Un ejemplo de respuesta que llega del endpoint es la siguiente:

```json
{
  "status": "success",
  "message": "Anime searched",
  "payload": {
    "items": [
      {
        "id": "boku-no-hero-academia-final-season",
        "title": "Boku no Hero Academia: Final Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/2889.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-the-movie-4-youre-next",
        "title": "Boku no Hero Academia the Movie 4: You're Next",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/1114.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-7th-season",
        "title": "Boku no Hero Academia 7th Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/88.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-memories",
        "title": "Boku no Hero Academia: Memories",
        "type": "Special",
        "poster": "https://cdn.animeav1.com/covers/3825.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-ua-heroes-battle",
        "title": "Boku no Hero Academia: UA Heroes Battle",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/185.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-6th-season",
        "title": "Boku no Hero Academia 6th Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/183.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-ona",
        "title": "Boku no Hero Academia (ONA)",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/184.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-the-movie-3-world-heroes-mission",
        "title": "Boku no Hero Academia the Movie 3: World Heroes' Mission",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/188.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-5th-season",
        "title": "Boku no Hero Academia 5th Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/182.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-ikinokore-kesshi-no-survival-kunren",
        "title": "Boku no Hero Academia: Ikinokore! Kesshi no Survival Kunren",
        "type": "OVA",
        "poster": "https://cdn.animeav1.com/covers/3824.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-the-movie-2-heroesrising",
        "title": "Boku no Hero Academia the Movie 2: Heroes:Rising",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/187.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-4th-season",
        "title": "Boku no Hero Academia 4th Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/181.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-the-movie-1-futari-no-hero",
        "title": "Boku no Hero Academia the Movie 1: Futari no Hero",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/186.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-3rd-season",
        "title": "Boku no Hero Academia 3rd Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/180.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-2nd-season",
        "title": "Boku no Hero Academia 2nd Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/179.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia",
        "title": "Boku no Hero Academia",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/178.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-hero-academia-more",
        "title": "Boku no Hero Academia: More",
        "type": "Special",
        "poster": "https://cdn.animeav1.com/covers/4089.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "vigilante-boku-no-hero-academia-illegals-2nd-season",
        "title": "Vigilante: Boku no Hero Academia Illegals 2nd Season",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/3473.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "vigilante-boku-no-hero-academia-illegals",
        "title": "Vigilante: Boku no Hero Academia Illegals",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/874.jpg",
        "isSaved": false,
        "saveDate": null
      },
      {
        "id": "boku-no-tsuma-wa-kanjou-ga-nai",
        "title": "Boku no Tsuma wa Kanjou ga Nai",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/89.jpg",
        "isSaved": false,
        "saveDate": null
      }
    ],
    "total": 20
  },
  "statusCode": 200
}
```

---

## Resultado

### Archivos creados

| Archivo | Descripción |
|---|---|
| `frontend/src/features/search/types.ts` | `AnimeInfo`, `SearchResponse` |
| `frontend/src/features/search/api.ts` | `animeSearchQuery` (queryOptions), `saveAnime`, `unsaveAnime` |
| `frontend/src/features/search/hooks/use-search-animes.ts` | `useSearchAnimes` — wrapper de `useQuery` |
| `frontend/src/features/search/hooks/use-toggle-saved.ts` | `useToggleSaved` — mutación save/unsave con estado optimista y rollback |
| `frontend/src/features/search/components/search-form.tsx` | Input + botón; submit con Enter o click |
| `frontend/src/features/search/components/anime-card.tsx` | Tarjeta con `Link`, imagen, título, badge de tipo y bookmark |
| `frontend/src/features/search/components/search-results.tsx` | Grilla responsive con estados idle/loading/empty/error |

### Archivos modificados

| Archivo | Cambio |
|---|---|
| `frontend/src/routes/_app/search.tsx` | Orquestador con `validateSearch` para URL search params (`?query=`) |
| `frontend/src/api.ts` | Fix de token key: `nwhub-auth` → `aniseek-auth` |

### Decisiones técnicas

- **Query en URL params**: `validateSearch` de TanStack Router persiste el query en `?query=`; la búsqueda sobrevive a refresh y es compartible.
- **React Query**: patrón `queryOptions` con `queryFn` como referencia directa (extrae el query desde `QueryFunctionContext.queryKey`).
- **Bookmark**: estado optimista local con rollback en `onError`; toasts vía sonner.
- **Accesibilidad**: la tarjeta usa `<Link>` semántico en lugar de `<div onClick>`, con `e.preventDefault()` + `e.stopPropagation()` en el botón de bookmark para no disparar la navegación.