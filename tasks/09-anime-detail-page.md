# Página de detalle de anime

El archivo en la carpeta @frontend/src/routes es un orquestador de componentes. La mayoría de los componentes y lógica debe existir en el módulo correspondiente a esa vista en @frontend/src/features/anime.

Archivo principal: @frontend/src/routes/\_app/anime.tsx

## Restricciones

- Usar componentes shadcn cuando sea posible
- Tener en cuenta el responsive

## Vista

La vista se va a componer de 2 secciones principales que tienen una proporción de 1 (izquierda) y 3 (derecha), es decir, en total 4 unidades:

1. La sección izquierda con el poster del anime (con el botón de guardado), estado del anime, día de la semana de emisión (en caso de estar en emisión) y los géneros
2. La sección derecha tiene 2 secciones que son un header con el nombre del anime, un subtitulo que dice la última vez que se scrapeó, un botón de actualizar info y debajo 2 tab: information y episodes
   2.1 En la pestaña de información se mostrará la descripción del anime y los animes relacionados con redireccionamiento (secuela, prequel, etc.)
   2.2 En la sección de episodios se mostrará unas cards con información relacionada a los episodios: cantidad de episodios, episodios descargados y espacio de almacenamiento ocupado. Debajo de esa card debe haber un text input para agregar el episodio o rango de episodios a descargar. Al final debe estar la lista de episodios como una tabla con las columnas id, episode, downloaded y actions que debe ser scrolleable. Debes usar una lista virtualizada para no cargar la tabla en memoria.

### General

Debes usar el siguiente endpoint para obtener la información del anime:

- Endpoint: `/api/animes/$anime_id`
- Método: `GET`

Un ejemplo de respuesta sería:

```json
{
  "status": "success",
  "message": "Anime retrieved",
  "payload": {
    "id": "kusuriya-no-hitorigoto",
    "title": "Kusuriya no Hitorigoto",
    "type": "TV",
    "poster": "https://cdn.animeav1.com/covers/139.jpg",
    "isSaved": false,
    "saveDate": null,
    "season": 1,
    "platform": "AnimeAV1",
    "description": "Maomao, la hija de un boticario, ha sido arrancada de su pacífica vida y vendida a los niveles más bajos de la corte imperial. Ahora, y siendo solo una sirvienta, Maomao se adapta a su nueva vida mundana y oculta su extenso conocimiento de medicina para evitar cualquier atención no deseada.\\n\\nNo mucho después de la llegada de Maomao, los niños infantes del emperador comienzan a experimentar inexplicablemente síntomas graves, como si se hubiera lanzado una maldición. La curiosa Maomao resuelve fácilmente el misterio y, para mantenerse fuera del centro de atención, intenta dejar una pista anónima. Desafortunadamente, el apuesto y perceptivo eunuco Jinshi ve a través de su disfraz y logra identificarla.\\n\\nEn reconocimiento a su talento, Maomao es promovida a dama de compañía de la concubina favorita del emperador, Gyokuyou. A medida que Maomao continúa remedando las numerosas dolencias que afectan a la corte imperial, su experiencia farmacéutica pronto demuestra ser indispensable. ",
    "genres": ["Drama", "Histórico", "Misterio"],
    "relatedInfo": [
      {
        "id": "kusuriya-no-hitorigoto-2nd-season",
        "title": "Kusuriya no Hitorigoto 2nd Season",
        "type": "sequel"
      }
    ],
    "weekDay": null,
    "episodes": [
      {
        "id": 1,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/1.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 2,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/2.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 3,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/3.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 4,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/4.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 5,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/5.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 6,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/6.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 7,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/7.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 8,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/8.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 9,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/9.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 10,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/10.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 11,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/11.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 12,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/12.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 13,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/13.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 14,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/14.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 15,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/15.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 16,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/16.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 17,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/17.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 18,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/18.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 19,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/19.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 20,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/20.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 21,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/21.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 22,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/22.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 23,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/23.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      },
      {
        "id": 24,
        "animeId": "kusuriya-no-hitorigoto",
        "imagePreview": "https://cdn.animeav1.com/covers/139/24.jpg",
        "isUserDownloaded": false,
        "isGlobalDownloaded": false
      }
    ],
    "isFinished": true,
    "lastScrapedAt": "2026-05-22T05:26:30.425371Z"
  },
  "statusCode": 200
}
```
