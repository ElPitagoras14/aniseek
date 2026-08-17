## 1. Runner y configuración

- [ ] 1.1 Agregar al grupo de desarrollo de `backend/pyproject.toml` el runner de pruebas, su complemento de asincronía basado en asyncio y la librería que levanta contenedores de PostgreSQL
- [ ] 1.2 Configurar el runner en `backend/pyproject.toml`: declarar `src` como raíz de importación, apuntar el descubrimiento a `backend/tests/` y habilitar el modo automático de asincronía para no decorar cada prueba
- [ ] 1.3 Crear `backend/tests/` y confirmar que una prueba trivial puede importar un módulo de la aplicación con la misma forma que usa la aplicación (`from config import ...`)
- [ ] 1.4 Confirmar que `.dockerignore` no necesita cambios: el `Dockerfile` copia solo `src` y resuelve dependencias con `--no-dev`, de modo que ni las pruebas ni sus dependencias llegan a la imagen

## 2. Base de datos efímera y variables de entorno

- [ ] 2.1 Escribir en el enganche de configuración del runner —que corre **antes** de la recolección— el arranque de un contenedor de PostgreSQL de la misma versión mayor que producción
- [ ] 2.2 Fijar en ese mismo enganche todas las variables que la aplicación exige al importarse: `DB_URL` apuntando al contenedor, más `SECRET_KEY`, `ALGORITHM`, `REDIS_URL`, `ACCESS_TOKEN_EXP_MIN` y `REFRESH_TOKEN_EXP_DAY`
- [ ] 2.3 **Verificar que esas variables ganan sobre el `.env` de la raíz.** Los módulos de configuración usan `find_dotenv(usecwd=True)`, así que el `.env` del repositorio es visible durante las pruebas; si tuviera precedencia, la suite escribiría contra la base de desarrollo
- [ ] 2.4 Registrar el descarte del contenedor al finalizar la sesión, y confirmar que no queda ninguno corriendo tras una ejecución exitosa y tras una fallida

## 3. Esquema de la base de prueba

- [ ] 3.1 Escribir la creación del esquema aplicando la fuente canónica vigente —hoy `postgres/init.sql`— desde un único punto de la infraestructura de pruebas
- [ ] 3.2 Dejar ese punto documentado como el lugar a modificar cuando `adopt-dbmate` reemplace la fuente por las migraciones
- [ ] 3.3 Confirmar que los datos de referencia quedan sembrados: existen filas en `role_types`, `related_types` y `avatars`

## 4. Aislamiento entre pruebas

- [ ] 4.1 Escribir el vaciado de datos entre pruebas, derivando la lista de tablas del esquema en tiempo de ejecución y excluyendo una lista explícita de preservadas: las de referencia y la de control de migraciones
- [ ] 4.2 Aplicarlo de forma automática a cada prueba, sin que cada una tenga que solicitarlo
- [ ] 4.3 Confirmar que **no** se abre ninguna transacción envolviendo la prueba, para no degradar a savepoint la del código bajo prueba

## 5. Verificar el andamiaje antes de escribir pruebas reales

- [ ] 5.1 Escribir una prueba que inserte una fila y la lea, y confirmar que pasa
- [ ] 5.2 Escribir una segunda prueba que verifique que la fila de la anterior ya no está
- [ ] 5.3 **Comprobar que la prueba no corre dentro de una transacción**: hacer que el código escriba y confirme, y verificar desde una conexión distinta que la fila es visible. Si la prueba estuviera envuelta en una transacción, esa segunda conexión no la vería — es la comprobación directa de 4.3
- [ ] 5.4 Confirmar que los datos de referencia siguen presentes después de que el vaciado corrió varias veces

## 6. Sustituciones compartidas

- [ ] 6.1 Escribir la sustitución del encolado en Dramatiq (`download_anime_episode.send`), que los dos caminos de descarga invocan antes de abrir su transacción; sin esto las pruebas exigirían un Redis disponible y publicarían mensajes reales
- [ ] 6.2 Escribir la sustitución del scraping que `update_anime_info` ejecuta dentro de su transacción, para que ninguna prueba salga a la red
- [ ] 6.3 Escribir las funciones auxiliares que construyen los datos mínimos de cada escenario —un usuario, un anime, sus episodios—, invocables desde cada prueba

## 7. Pruebas de atomicidad, una por camino

- [ ] 7.1 `add_new_anime` (`animes/service.py:67`): interrumpir después de la primera escritura y verificar que no quedó el anime insertado
- [ ] 7.2 `update_anime_info` (`animes/service.py:115`): interrumpir tras la actualización inicial y verificar que los campos conservan su valor previo
- [ ] 7.3 `download_anime_episode_controller` (`episodes/service.py:91`): interrumpir entre la inserción de la descarga del usuario y la actualización del episodio, y verificar que ninguna de las dos persistió
- [ ] 7.4 `download_anime_episode_bulk_controller` (`episodes/service.py:176`): **este camino captura la excepción en lugar de propagarla**, así que la prueba verifica que el bucle continúa con los episodios siguientes, que el interrumpido queda registrado como fallido, y que ninguna de sus escrituras persistió
- [ ] 7.5 `delete_anime_storage_controller` (`episodes/service.py:219`): interrumpir entre el borrado de descargas y el reseteo de episodios, y verificar que ambos quedaron sin efecto
- [ ] 7.6 El bloque de `franchises/service.py:53`: interrumpir a mitad y verificar que ninguna escritura persistió
- [ ] 7.7 **Escribir el caso positivo**: al menos un camino ejecutado sin interrupción, verificando que todas sus escrituras sí persisten. Sin esto, una implementación que nunca confirmara nada pasaría las seis pruebas anteriores

## 8. Cerrar

- [ ] 8.1 Ejecutar la suite completa y confirmar que las siete pruebas pasan contra la implementación actual con `databases`
- [ ] 8.2 Si alguna falla, tratarla como un defecto preexistente y resolverla antes de dar el change por completo — no ajustar la prueba para que pase
- [ ] 8.3 Documentar en el `README.md` el comando para ejecutar las pruebas y el requisito de tener Docker corriendo
- [ ] 8.4 Ejecutar la suite dos veces seguidas y confirmar que el resultado es idéntico, para descartar arrastre de estado entre ejecuciones
