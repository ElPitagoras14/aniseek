# Página de animes guardados

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/saved.

Archivo principal: @frontend/src/routes/\_app/saved.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive

## Vista

La vista se va a componer de 3 partes:

1. La sección de header
2. La sección de filtros y ordenamiento
3. La sección de resultados

### Sección de header

Esta sección debe tener un título y un subtitulo que indiquen que se trata de animes guardados.

### Sección de filtros y ordenamiento

Esta sección debe tener un campo de búsqueda y un botón de ordenar. Estas funciones se realizarán en el lado del cliente. Las opciones de ordenamiento serán:

- Orden alfabético
- Orden por fecha de guardado

De forma ascendente y descendente.

Y el filtro será opcional con opciones:

- Filtrar por anime en emisión
- Filtrar por anime finalizado

Por defecto no tendrá filtro y será ordenado por fecha de guardado en orden descendente.

### Sección de resultados

Esta sección debe mostrar los resultados de la búsqueda.

Cada resultado debe ser una especie de tarjeta bastante ligera con el título, el tipo de anime y la imagen del anime similar a la de la sección de búsqueda.

El endpoint a llamar para obtener los animes guardados es el siguiente:

- Endpoint: `/api/animes/saved`
- Método: `GET`

Un ejemplo de respuesta sería:

```json
{
  "status": "success",
  "message": "Saved animes retrieved",
  "payload": {
    "items": [
      {
        "id": "mushikaburi-hime",
        "title": "Mushikaburi-hime",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/3201.jpg",
        "isSaved": true,
        "saveDate": "2026-05-22T03:29:24.580113Z"
      },
      {
        "id": "mushoku-tensei-isekai-ittara-honki-dasu",
        "title": "Mushoku Tensei: Isekai Ittara Honki Dasu",
        "type": "TV",
        "poster": "https://cdn.animeav1.com/covers/353.jpg",
        "isSaved": true,
        "saveDate": "2026-05-22T03:29:31.377387Z"
      }
    ],
    "total": 2
  },
  "statusCode": 200
}
```