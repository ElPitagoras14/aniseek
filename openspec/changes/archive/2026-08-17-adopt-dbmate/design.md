## Context

El esquema se define hoy en `postgres/init.sql` (210 líneas, 13 tablas, 9 índices y tres bloques de datos de referencia), montado en `/docker-entrypoint-initdb.d/` de la imagen de Postgres. Ese directorio solo corre con el directorio de datos vacío, y los dos composes se comportan de forma opuesta al respecto: `compose.dev.yaml` no declara volumen persistente, así que la base se reconstruye y el archivo vuelve a correr; `compose.yaml` declara `postgres-data`, así que el archivo queda inerte tras el primer arranque.

Restricciones que enmarcan el diseño:

- **Dos servicios consumen el esquema con stacks distintos.** El backend usa SQL crudo sobre `databases[asyncpg]`; el worker usa SQLAlchemy sobre `psycopg2`. Ninguno declara modelos de los que se pueda derivar el esquema.
- **Los dos dependen de que el esquema exista antes de arrancar.** Hoy ambos declaran `depends_on: aniseek-db: condition: service_healthy`, que garantiza que Postgres responde pero no que las tablas estén.
- **El despliegue existente tiene datos que no se pueden perder**: usuarios, listas guardadas e historial de descargas.
- **`DB_URL` ya usa el scheme `postgresql://`**, que dbmate acepta, así que no hace falta una variable nueva ni traducirla.

## Goals / Non-Goals

**Goals:**

- Que exista un camino de actualización del esquema que no requiera borrar el volumen ni aplicar SQL a mano.
- Que el esquema quede descrito por una única fuente de verdad, versionada y revisable en un diff.
- Que el despliegue existente adopte el mecanismo conservando sus datos.
- Que ambos servicios arranquen con la garantía de que el esquema está al día, no solo de que Postgres responde.

**Non-Goals:**

- Modificar el esquema. Este change no agrega, quita ni altera ninguna tabla, columna, índice ni dato de referencia.
- Adoptar un ORM o cambiar cómo los servicios consultan la base.
- Resolver el drift de `.env.example` documentado en otros changes.

## Decisions

### D1 — dbmate, no Alembic

La alternativa natural en un proyecto Python sería Alembic, pero su ventaja principal —autogenerar migraciones comparando modelos de SQLAlchemy contra la base— no aplica acá: el backend no tiene modelos, sus repositorios son strings de SQL. Sin modelos, Alembic queda como un runner de SQL a mano con bastante más ceremonia y con la migración atada al intérprete de Python del backend.

dbmate es un binario independiente que ejecuta SQL plano. Eso encaja con cómo el proyecto ya escribe queries, y al ser externo a ambos servicios evita tener que decidir cuál de los dos stacks "posee" el esquema.

*Alternativas consideradas:* Flyway guarda checksums de cada migración aplicada y falla si el esquema derivó del script, lo que complica adoptar sobre una base existente. Seguir con SQL a mano es el estado actual y es lo que el change viene a resolver.

### D2 — `db/` vive en la raíz del repositorio

Ni `backend/` ni `worker/` son dueños del esquema: los dos lo consumen. Poner las migraciones dentro de uno lo convertiría en dependencia implícita del otro.

`db/migrations/` y `db/schema.sql` en la raíz, siguiendo las rutas por defecto de dbmate, lo que además permite montar `./db:/db` tal como documenta la herramienta sin configurar nada.

### D3 — Las migraciones corren en un servicio one-shot de compose

Se agrega un servicio que usa la imagen oficial `ghcr.io/amacneil/dbmate`, espera a que Postgres esté sano, aplica las migraciones pendientes y termina. La API y el worker pasan a depender de que ese servicio **haya terminado con éxito**, no solo de que la base responda.

El motivo decisivo es el worker. Si las migraciones corrieran dentro de `backend/entrypoint.sh`, el worker no tendría ninguna señal de cuándo el esquema está listo: hoy arranca en paralelo con la API y podría consultar tablas que todavía no existen. Un servicio separado da un punto de sincronización para los dos.

Beneficios secundarios: la imagen del backend no necesita incorporar un binario ajeno a su stack, y el paso de migración es visible como un servicio propio en los logs de compose en vez de quedar escondido en un entrypoint.

*Detalle operativo que es fácil errar:* el servicio **no** debe llevar `restart: unless-stopped` como el resto. Es de un solo uso y terminar con éxito es su comportamiento correcto; una política de reinicio lo relanzaría indefinidamente.

*Alternativa considerada:* meter el binario en la imagen del backend con un `COPY --from` y correrlo en el entrypoint es menos infraestructura, pero deja al worker sin garantía y acopla el ciclo de vida de las migraciones al de un servicio en particular. Con una sola instancia de API no hay riesgo de carrera entre réplicas en ninguna de las dos opciones, así que la decisión se juega enteramente en la sincronización del worker.

### D4 — El despliegue existente se da de alta con un `INSERT`, y el supuesto se verifica

dbmate registra las migraciones aplicadas en una tabla de una sola columna. No guarda checksums ni reconstruye un grafo de revisiones, así que dar de alta una base preexistente consiste en crear esa tabla e insertar la versión de la primera migración. No ejecuta SQL de esquema y no toca los datos.

Pero eso apoya todo el procedimiento en un supuesto: que el esquema real coincide con `postgres/init.sql`. Ese supuesto es exactamente el que el change pone en duda —la posibilidad de deriva silenciosa es parte de la motivación—, así que **no se asume, se comprueba**: se construye una base limpia aplicando la primera migración, se vuelca el esquema de esa base y el de la base real, y se comparan. Si difieren, la deriva se descubre ahora, cuando todavía es barata, en vez de manifestarse como una migración que falla dentro de seis meses.

*Alternativa considerada:* escribir la primera migración con `CREATE TABLE IF NOT EXISTS` y `ON CONFLICT DO NOTHING` la vuelve idempotente y elimina el paso manual de alta. Se descarta porque enmascara justamente lo que hay que averiguar: si el esquema real difiere, la migración lo pasaría por alto en silencio y la deriva quedaría instalada dentro del nuevo mecanismo.

### D5 — `schema.sql` lo regenera el desarrollador, no el servicio en runtime

dbmate mantiene un volcado completo del esquema tras cada migración, útil para revisar cambios en un diff. Pero el servicio de D3 corre en cada arranque de la aplicación, y dejarlo volcar el esquema significaría escribir dentro de un bind mount en producción, en un momento en que nadie va a leer el resultado.

El servicio de runtime corre con el volcado desactivado. `db/schema.sql` se regenera localmente al crear una migración y se commitea junto con ella, que es cuando el archivo tiene valor: al revisar el cambio.

*Verificado:* la imagen oficial sí incluye las herramientas cliente de Postgres —`pg_dump` 18.4 y `psql`, además de las de MariaDB, MySQL y SQLite—, de modo que el volcado local puede hacerse con la misma imagen sin necesidad de instalar nada ni recurrir a la imagen de Postgres. La versión de `pg_dump` es superior a la del servidor (`postgres:18.1-alpine`), que es la dirección compatible: `pg_dump` solo se niega a operar cuando el servidor es más nuevo que él.

### D6 — `postgres/init.sql` y su montaje se eliminan

Conservarlo sería mantener una tercera descripción del esquema junto a las migraciones y a la base real. Como solo se ejecuta con el directorio de datos vacío, quedaría además como una trampa: seguiría corriendo en despliegues nuevos, compitiendo con las migraciones por crear las mismas tablas.

Se elimina el archivo y su montaje en ambos composes. El `README.md`, que hoy indica copiar `postgres/init.sql` al montar el proyecto, deja de mencionarlo.

### D7 — Numeración secuencial de cuatro dígitos, no timestamps

Los nombres siguen el formato `NNNN_descripción.sql`, con el número rellenado con ceros a cuatro dígitos y la descripción en `snake_case`. La primera migración es `db/migrations/0001_create_initial_schema.sql`.

Esto se aparta del formato que genera dbmate por defecto —catorce dígitos de timestamp— pero es compatible: la herramienta registra como versión **únicamente los caracteres numéricos iniciales del nombre**, sin exigir que sean una fecha. La versión de la primera migración es entonces `0001`, que es lo que el alta de D4 debe insertar.

*Por qué secuencial:* el orden de aplicación queda explícito y legible, y el identificador que hay que reproducir a mano en el alta es de cuatro caracteres en lugar de catorce. Con un solo desarrollador, la ventaja que ofrecen los timestamps —que dos personas trabajando en paralelo nunca elijan el mismo identificador— no compra nada.

*El costo que se acepta:* dos ramas que agreguen una migración cada una elegirán ambas el número siguiente, y al fusionarlas quedarían dos archivos distintos declarando la misma versión. Git no detecta ese conflicto, porque son archivos con nombres distintos. Con desarrollo lineal el riesgo es teórico, pero si alguna vez se trabaja en ramas paralelas hay que renumerar antes de fusionar.

*Verificado cómo se comporta dbmate ante ese caso:* aplica la primera migración del par, ejecuta el SQL de la segunda y falla al registrar la versión repetida, con la transacción de esa segunda migración revertida por completo. La base queda con la primera aplicada y sin rastro de la segunda; las migraciones posteriores no llegan a correr y el proceso termina con código distinto de cero. Es decir, el error es ruidoso y atómico, no un descarte silencioso. La única salvedad es que el SQL de la migración duplicada sí se ejecuta antes de revertirse, así que la limpieza depende de que sus instrucciones sean transaccionales —cierto para el DDL ordinario en Postgres, no para operaciones como la creación concurrente de índices.

Reglas que se desprenden:

- **El relleno con ceros es obligatorio.** El orden se resuelve comparando las versiones como texto, así que `0010` se ordena después de `0009`, mientras que `10` se ordenaría antes que `9`. Cuatro dígitos alcanzan de sobra y mantienen el orden alineado con el numérico.
- `dbmate new <descripción>` sigue siendo la forma de crear el archivo, renombrándolo enseguida al número que corresponda. Hacerlo antes de aplicarlo no tiene ninguna consecuencia.
- Una vez que una migración fue aplicada o dada de alta, su número no se modifica. Renombrar la parte descriptiva es seguro; cambiar el número hace que dbmate la vea como una migración desconocida e intente aplicarla contra una base que ya la contiene.

**La sección `migrate:down` de la migración inicial queda vacía**, deliberadamente. Ambas marcas —`-- migrate:up` y `-- migrate:down`— deben estar presentes, pero deshacer la migración inicial significa destruir el esquema completo, y `dbmate rollback` revierte la última aplicada, que tras el alta es precisamente esa. Poblarla con los `DROP TABLE` de las trece tablas convertiría un comando de un solo paso en la pérdida total de la base. Para reconstruir una base de desarrollo desde cero ya existe `dbmate drop`, así que un `down` real sería un duplicado peligroso de algo ya cubierto.

Las migraciones posteriores sí llevan un `migrate:down` real: revertir un cambio acotado es una operación legítima y el motivo por el que la sección existe.

## Risks / Trade-offs

- **El alta manual debe ocurrir antes de que el nuevo compose arranque.** → Verificado experimentalmente: si el servicio de migraciones corre contra una base preexistente sin la fila de alta, falla con `relation ... already exists`, revierte la transacción sin dejar estado parcial y termina con código 2, lo que bloquea el arranque de la API y del worker por la dependencia de D3. Con el alta hecha, la misma ejecución no aplica nada y termina con código 0. El fallo es ruidoso y no destructivo, pero deja la aplicación caída hasta hacer el alta. El orden es parte del procedimiento de despliegue, no algo que el change pueda automatizar.

- **La comparación de volcados de D4 puede revelar deriva real.** → Es el resultado útil del ejercicio, no un problema del change, pero puede convertir una tarea mecánica en uno o varios días de reconciliación. Conviene hacer la comparación antes de comprometerse con una ventana de despliegue.

- **Un `pg_dump` de versión distinta a la del servidor produce diferencias espurias.** → El servidor es `postgres:18.1-alpine`. Los volcados de D4 y D5 deben hacerse con las herramientas cliente de esa misma versión mayor, por ejemplo ejecutándolas desde la propia imagen de Postgres en vez de desde una instalación local.

- **La condición de dependencia de D3 exige una versión de Compose que la soporte.** → Esperar a que un servicio termine con éxito es parte de la Compose Spec y está soportado por Docker Compose v2, que es lo que el proyecto ya usa, pero conviene confirmarlo al implementar antes de que falle en el despliegue.

- **Se agrega una imagen externa a la cadena de arranque.** → `ghcr.io/amacneil/dbmate` pasa a ser una dependencia de despliegue más. Es pequeña y de un solo uso, y la alternativa —incorporar el binario a la imagen del backend— tiene el costo de D3 en sincronización.

## Migration Plan

1. Crear `db/migrations/` con la primera migración conteniendo el esquema actual íntegro: tablas, índices y datos de referencia.
2. Verificar la equivalencia (D4): levantar una base limpia, aplicar la migración, volcar su esquema y compararlo con el volcado de la base real. Resolver cualquier diferencia antes de continuar.
3. Agregar el servicio de migraciones a ambos composes y cambiar las dependencias de la API y del worker para que esperen su finalización exitosa.
4. Eliminar `postgres/init.sql`, su montaje en ambos composes y su mención en el `README.md`.
5. **En el despliegue existente, antes de levantar la versión nueva**: crear la tabla de registro e insertar la versión de la primera migración.
6. Levantar la versión nueva y confirmar que el servicio de migraciones termina sin aplicar nada, y que la API y el worker arrancan después de él.
7. Verificar en un entorno limpio que, sin `init.sql`, el esquema se construye enteramente desde las migraciones.

**Rollback:** revertir el commit y volver a la imagen anterior. El esquema no cambió, así que la base sirve a ambas versiones sin conversión. La tabla de registro queda en la base sin que nadie la lea, lo cual es inofensivo y ahorra rehacer el alta si se vuelve a intentar.

## Open Questions

Ninguna abierta. Las dos que había se resolvieron ejecutando dbmate contra una base descartable, y sus respuestas están incorporadas en D5, D7 y en los riesgos:

- **¿La imagen oficial incluye las herramientas cliente de Postgres?** Sí: `pg_dump` 18.4 y `psql`. Compatible con el servidor `postgres:18.1-alpine`. Los volcados locales se hacen con la misma imagen.
- **¿Cómo reacciona dbmate a dos migraciones con la misma versión?** Falla de forma ruidosa y atómica: ejecuta el SQL de la segunda, no puede registrar la versión repetida, revierte esa transacción entera y aborta con código distinto de cero sin correr las migraciones siguientes. No hay descarte silencioso.

Queda decidido, además, que el sembrado del usuario `admin` se mantiene donde está: en el arranque de la API (`backend/src/main.py`), con la contraseña hasheada en Python. Moverlo junto a los demás datos de referencia exigiría generar el hash fuera de la aplicación y fijarlo en una migración, lo que ataría una credencial a un archivo versionado. Queda fuera del alcance de este change.
