## Context

El workflow `.github/workflows/docker.yml` corre 9 jobs y 8 builds multi-arquitectura para publicar 4 imágenes. Los cuatro jobs `build-*` construyen con `push: false` y existen solo como barrera: garantizan que ningún `publish-*` empuje nada si algún servicio no compila. Los cuatro `publish-*` reconstruyen lo mismo apoyándose en la caché `type=gha`.

El versionado actual acopla dos preguntas distintas en los mismos archivos:

```
                          ¿quién responde hoy?        problema
────────────────────────────────────────────────────────────────────────────
¿qué release es esto?     backend/pyproject.toml      duplicado en 3 archivos
¿qué hay que reconstruir? (nadie)                     imposible de responder
```

Como los tres archivos de versión viven dentro de directorios de servicio y se bumpean en lockstep, el commit de release toca `backend/`, `worker/` y `frontend/`. Cualquier detección de cambios basada en diff responde "cambió todo" por construcción. Ese acople es la causa raíz, no el número de jobs.

Restricciones del entorno:

- `compose.yaml` referencia `:latest` en los cuatro servicios. El deploy a Dokploy es un `POST /api/compose.deploy` que hace pull de esas etiquetas.
- El compose de Dokploy está en **modo Raw**: el YAML vive pegado en su UI y el repositorio no se clona al desplegar. El `compose.yaml` del repositorio no es el que corre en producción; sincronizarlos es un paso manual. Ningún archivo versionado llega al despliegue por sí solo.
- La API de Dokploy expone `compose.update` con un campo `env`, pero es el `.env` completo como string: escribirlo desde el pipeline exigiría una credencial con alcance sobre todos los secretos del stack. El pedido de una API para modificar variables de entorno desde CI está cerrado como *not planned*. Confirmado además que `compose.deploy` —el endpoint que ya usa el job `deploy`— solo acepta `composeId`, `title` y `description`: no tiene ningún parámetro de variables de entorno, ni siquiera el problemático de `compose.update`.
- Las imágenes son multi-arquitectura (`linux/amd64,linux/arm64`). Cualquier mecanismo de re-etiquetado debe preservar la lista de manifiestos.
- `openspec/specs/database-migrations` exige que la imagen de migrate se publique con la misma versión que el resto, en el mismo proceso y ejecución, y que un fallo detenga el release completo.
- `openspec/specs/frontend-runtime-config` exige que toda clave de configuración resuelva por precedencia runtime → build-time → default, con la regla de "qué cuenta como configurado" declarada por clave.
- Los tags existentes no llevan prefijo `v` (`2.0.19`, no `v2.0.19`).

## Goals / Non-Goals

**Goals:**

- Separar "qué release es" de "qué se reconstruye", que hoy comparten archivo.
- Un solo build por servicio por release, y solo si ese servicio cambió.
- Que el servicio sin cambios obtenga el tag de la versión nueva sin reconstruirse ni transferir bytes.
- Preservar la atomicidad que hoy dan los jobs `build-*`: ningún `:latest` se mueve y ningún tag de git se crea si algún servicio falló.
- Reducir el workflow a una forma legible: una definición de servicio, no cuatro copias.
- Que el gate de versión compare semver de verdad, en vez de desigualdad contra el tag alcanzable más cercano.

**Non-Goals:**

- Derivar la versión automáticamente de conventional commits (`release-please`, `semantic-release`). La versión la sigue decidiendo una persona.
- Versionado independiente por servicio. Un release es un número que aplica a los cuatro.
- Pinear `compose.yaml` a una versión exacta en lugar de `:latest`.
- Soportar versiones prerelease (`2.1.0-rc1`). El proyecto usa `X.Y.Z` plano.
- Cambiar el mecanismo de despliegue a Dokploy.
- Un disparador manual (`workflow_dispatch`). El release se dispara exclusivamente por push a `main` con una versión mayor. Descartado, no diferido: agregarlo obligaría a definir si salta el gate de semver, si re-etiqueta y si despliega, y esas tres reglas ensucian un modelo que se sostiene en una sola frase. La deriva de imágenes base se combate pineando el `FROM`, no reconstruyendo por las dudas.

## Decisions

### 1. `VERSION` en la raíz como fuente única

Un archivo `VERSION` en la raíz con el número plano (`2.1.0`, sin prefijo). Es el único archivo que se bumpea.

Lo decisivo no es que sea un archivo, sino **que no viva dentro de ningún directorio de servicio**. Eso es lo que rompe el acople: el commit de release ya no aparece en `git diff -- backend/`.

`backend/pyproject.toml`, `worker/pyproject.toml` y `frontend/package.json` conservan su campo `version` porque sus herramientas lo exigen, pero dejan de bumpearse y dejan de significar algo sobre el release.

*Alternativas consideradas:*

- **El tag de git como única fuente, sin archivo.** Elimina un archivo, pero cambia el disparador: habría que pushear un tag en vez de mergear a `main`, y el número deja de ser revisable en el PR. Se descartó por eso.
- **Derivar el release de `max(versiones de servicio)`.** Evita el archivo nuevo, pero obliga a bumpear archivos dentro de directorios de servicio, que es exactamente el acople que se quiere romper.
- **Mantener versión por servicio con tags tipo `api/2.0.21`.** Da un diff más preciso, pero rompe el release y el deploy únicos que `compose.yaml` y Dokploy ya asumen.

### 2. La detección de cambios es un diff contra el último tag, no contra el push

Baseline = el tag semver más alto: `git tag --sort=-v:refname | head -1`. Un servicio se reconstruye si `git diff --quiet <baseline>..HEAD -- <dir>` reporta cambios.

El baseline es el último release **exitoso**, no el commit anterior. Eso da una propiedad importante: si una corrida falla después de publicar imágenes pero antes de crear el tag, el baseline no avanza y la corrida siguiente vuelve a ver los mismos cambios pendientes. El pipeline se auto-repara sin intervención.

Explícitamente **no** se usa `git describe --tags --abbrev=0`, que devuelve el tag alcanzable más cercano en el historial y no el semver más alto. Esa es la función que hoy deja el gate roto.

*Alternativas consideradas:*

- **`dorny/paths-filter@v3` con `base: <tag>`.** Más declarativo y con sintaxis de globs. Se descartó por ser una dependencia externa para lo que es un `git diff --quiet` de una línea, en un workflow cuyo objetivo declarado es tener menos piezas.
- **Diff sobre el rango del push.** Rompe la auto-reparación: un release fallido pierde los cambios para siempre.

### 3. La promoción se hace con `docker buildx imagetools create`

El servicio sin cambios obtiene el tag nuevo copiando el manifiesto del lado del registry:

```
docker buildx imagetools create \
  --tag ghcr.io/elpitagoras14/aniseek-api:2.1.0 \
        ghcr.io/elpitagoras14/aniseek-api:2.0.19
```

Preserva la lista de manifiestos completa —ambas arquitecturas— sin pull, sin build y sin transferir capas: es un `PUT` de manifiesto contra GHCR. `buildx` ya está en el workflow, así que no agrega herramientas.

Se promueve **desde el tag del baseline**, no desde `:latest`. `:latest` es mutable y no ofrece garantías sobre qué versión referencia. El tag del baseline sí: por la decisión 5, todo release exitoso publica los cuatro tags, así que `<servicio>:<baseline>` existe siempre como conjunto completo.

*Alternativas consideradas:*

- **`docker pull` + `docker tag` + `docker push`.** Descarta la lista de manifiestos y publica una sola arquitectura salvo malabares con `--platform`. Además transfiere todas las capas.
- **`crane copy` / `regctl` / `skopeo copy`.** Correctos, pero exigen instalar una herramienta más para algo que `buildx` ya hace.

### 3b. La web se promueve estampando la versión, no copiando el manifiesto

`web` es el único servicio que muestra un número de versión, y la copia pura de manifiesto no puede darle el del release nuevo: no cambia bytes. Su promoción usa un mecanismo distinto — apilar una capa sobre la imagen anterior:

```dockerfile
FROM ghcr.io/elpitagoras14/aniseek-web:2.0.19
COPY app-version /app-version
```

No es reconstruir la aplicación. Se toma la imagen anterior intacta y se le agrega una capa de unos pocos bytes. Al ser **solo `COPY`, sin ningún `RUN`**, no se ejecuta nada dentro de la imagen, así que la construcción multi-arquitectura no necesita emulación QEMU: es ensamblado de capas. Cuesta un orden de magnitud menos que la reconstrucción real, que incluiría `pnpm install` y `vite build` emulados para arm64.

`api`, `worker` y `migrate` conservan la copia pura de manifiesto de la decisión 3: no muestran versión, así que pagar el estampado no les compra nada. La bifurcación se asume a cambio de pagar el costo solo donde rinde.

*Alternativas consideradas:*

- **`imagetools create --annotation`.** Las anotaciones viven en el manifiesto, no en el sistema de archivos ni en la configuración de la imagen, así que son invisibles desde adentro del container.
- **Label OCI con la versión.** Falla por la misma razón que un build-arg: la promoción copia la configuración de la imagen tal cual, labels incluidos, así que una imagen promovida arrastra el label anterior.
- **Leer la etiqueta de la imagen desde el container.** Requiere montar el socket de Docker —acceso equivalente a root sobre el host— en el container expuesto públicamente. Y como `compose.yaml` referencia `:latest`, lo que el daemon reportaría es la cadena `latest`, no un número.
- **Inyectar la versión como variable de entorno al desplegar.** Descartada por las restricciones de modo Raw y de la API de Dokploy documentadas en Context.
- **No promover nunca la web.** El footer siempre coincidiría con el release, pero se renuncia al ahorro justo en el servicio con el build más caro.

### 4. Un job con `matrix` reemplaza los ocho jobs de build y publish

La matriz recorre los cuatro servicios. Cada entrada declara el sufijo de la imagen y su directorio, que además es el path del diff y el contexto de build:

```
{ image: api,     dir: backend  }
{ image: worker,  dir: worker   }
{ image: web,     dir: frontend }
{ image: migrate, dir: dbmate   }
```

Cada leg decide por sí misma entre build y promoción. La alternativa —calcular los cuatro booleanos en el job de detección y pasarlos como salidas— obliga a serializar un objeto a JSON y a plumbing de outputs entre jobs, a cambio de ahorrar tres checkouts. Se prefiere que cada leg sea legible de forma aislada.

### 5. `:latest` se mueve en un job aparte, después de que los cuatro tengan su tag

El job de matriz publica únicamente `<servicio>:<VERSION>`. Un job posterior, que depende de las cuatro legs, mueve `:latest` en los cuatro servicios con el mismo mecanismo de promoción.

Esto conserva la atomicidad que hoy justifica los cuatro builds desechados, pero pagando cuatro llamadas al registry en vez de cuatro builds multi-arquitectura. Importa porque `compose.yaml` referencia `:latest` en los cuatro: sin esta separación existe una ventana en que `api:latest` ya avanzó y `worker:latest` no, y cualquier despliegue en ese intervalo levanta una mezcla de versiones.

Se implementa como un único job con un bucle sobre los cuatro servicios, no como una segunda matriz: cada llamada tarda segundos y levantar cuatro runners para eso es desproporcionado.

De aquí sale el invariante en que se apoya la decisión 3: **todo release exitoso deja los cuatro tags de versión publicados.**

### 6. El tag de git lo crea la action de release

`softprops/action-gh-release@v2` —ya en uso— crea el tag a partir de `tag_name` si no existe. Desaparecen los pasos manuales de `git config`, `git tag` y `git push origin`, y con ellos el checkout con `fetch-depth: 0` que el job de release necesitaba solo para eso.

### 7. `concurrency` deja de cancelar corridas en progreso

Hoy `cancel-in-progress: true`: cuando entra un push nuevo a `main`, GitHub mata la corrida viva. Es el ajuste correcto para un CI de pull requests, donde la corrida anterior queda obsoleta. En un pipeline de release ninguna corrida queda obsoleta por la siguiente — cada una publica algo distinto.

El punto crítico es dónde puede caer la cancelación. El job de la decisión 5 recorre los cuatro servicios moviendo `:latest`:

```
promote  ─┬─ imagetools create web:latest     ← 2.1.0 ✓
          ├─ imagetools create api:latest     ← 2.1.0 ✓
          ╳  cancelación
          ├─ imagetools create worker:latest     no corre
          └─ imagetools create migrate:latest    no corre
```

Eso deja exactamente el estado mixto que la decisión 5 existe para evitar, sobre las etiquetas que `compose.yaml` referencia en los cuatro servicios.

Las dos decisiones están acopladas: la 5 compra atomicidad haciendo que los cuatro movimientos sean baratos y consecutivos, pero esa garantía vale solo mientras nada mate el job a mitad del bucle. Construir esa barrera y dejar `cancel-in-progress: true` es dejar abierta la única puerta que la rompe.

Un segundo caso, menos grave: si la cancelación cae después del promote y antes del tag, los cuatro `:latest` avanzaron pero no existe tag de git ni despliegue. Producción sigue con los containers viejos hasta que algo dispare un pull, y entonces salta de versión sin que ningún tag lo registre. La auto-reparación de la decisión 2 cubre la parte de las imágenes —el baseline no avanzó, la corrida siguiente vuelve a ver los cambios— pero no devuelve `:latest` a donde estaba.

Se cambia a `cancel-in-progress: false`. Las corridas se encolan en vez de matarse; el grupo de concurrencia se conserva, porque serializar los releases sigue siendo deseable: dos publicando etiquetas en paralelo es peor que esperar. El costo es que un push a `main` aguarda a que termine el release en curso, que para un pipeline de release es la semántica correcta y no una penalidad.

### 8. La versión que muestra la UI viaja dentro de la imagen

El estampado de la decisión 3b hace que la imagen web lleve siempre un archivo con el release al que pertenece, lo escriba una construcción real o una promoción. Eso resuelve el problema sin depender de nada externo:

```
build o promoción escriben   /app-version              ← 2.1.0
entrypoint exporta           APP_VERSION=$(cat ...)
envsubst genera              config.js                 ← window.__APP_CONFIG__
frontend resuelve            capa de runtime           ← patrón que el spec ya exige
```

`APP_VERSION` se declara como clave de configuración de runtime y reutiliza el mecanismo existente: `config.template.js` la enumera junto a `API_URL` y `AUTH_ENABLED`, y `entrypoint.sh` la sustituye al arrancar el container. No hace falta ninguna llamada a la API de Dokploy, ninguna credencial nueva ni ningún paso manual por release.

El `entrypoint.sh` lee el archivo de la imagen **de forma incondicional**, pisando cualquier valor heredado del entorno. Esto es deliberado y es lo que vuelve seguro al esquema: si alguien definiera `APP_VERSION` a mano en la UI de Dokploy, ese valor quedaría congelado y enmascararía al correcto, porque la capa de runtime gana sobre las demás. Con el archivo como autoridad, esa vía de fallo desaparece.

`frontend/vite.config.ts` deja de definir `__APP_VERSION__` y de leer la versión de `package.json`, que queda congelado. No se conserva una capa de build-time para esta clave: en Docker el archivo siempre existe, y en desarrollo la clave se resuelve por el `.env` de la raíz o cae al default `"dev"`, que es la respuesta correcta fuera de un release.

### 9. El workflow se nombra por lo que produce, no por la herramienta que usa

`docker.yml` / `Build and Push Docker Images` describe dos de las cinco etapas. El workflow decide si hay release, construye o promueve imágenes, publica etiquetas, crea el tag y la release, y dispara el despliegue. Construir y empujar imágenes es el medio, no el resultado.

Pasa a `release.yml` con `name: Release`, alineado con el nombre de la capacidad que lo especifica (`release-pipeline`). Docker deja de aparecer en el nombre porque es un detalle de implementación: si mañana la promoción se hiciera con otra herramienta, el nombre seguiría siendo correcto.

*Alternativas consideradas:* `build-and-deploy.yml` sigue enumerando etapas y envejece igual de mal; `ci.yml` es demasiado genérico y este workflow no corre en pull requests.

**Consecuencia operativa:** el historial de la pestaña Actions se indexa por path de archivo, así que las corridas anteriores quedan bajo `docker.yml` y el workflow renombrado empieza con historial vacío. Dentro del repositorio ninguna referencia apunta a ese path salvo documentos de changes archivados, que no se modifican. Fuera del repositorio hay que confirmar que ninguna regla de protección de rama lo exija como status check requerido, porque el check pasaría a llamarse distinto y quedaría permanentemente pendiente.

## Risks / Trade-offs

**El tag del baseline no existe para un servicio nuevo** → Un servicio agregado después del último release no tiene `<servicio>:<baseline>` para promover. Cada leg verifica la existencia del manifiesto origen y, si falta, construye en vez de promover. El fallback también cubre el primer release tras adoptar este esquema y el caso de un registry purgado.

**Una imagen base móvil congela versiones viejas** → Si el `Dockerfile` de un servicio no cambió pero su `FROM` apunta a una etiqueta móvil, la promoción impide recoger la deriva de la base. Esto es determinismo, no un defecto, pero deja de ser cierto que "reconstruir siempre" traiga parches de seguridad. Mitigación: pinear las imágenes base; `dbmate` ya lo hizo en `pin-dbmate-version` y los otros tres deberían revisarse. No se agrega una vía de rebuild forzado: ver el Non-Goal sobre `workflow_dispatch`.

**Un cambio fuera de los directorios de servicio no reconstruye nada** → Modificar `compose.yaml`, el propio workflow o `CLAUDE.md` no dispara ningún build. Es el comportamiento correcto, pero hay que declararlo: el diff se toma exclusivamente sobre el directorio de cada servicio.

**El diff no distingue cambios sustantivos de cosméticos** → Editar un comentario en `backend/src` reconstruye la imagen de api. Se acepta: un falso positivo cuesta un build, un falso negativo despliega código que nadie construyó.

**`sort -V` no implementa precedencia semver de prereleases** → Ordena `2.1.0-rc1` por encima de `2.1.0`, al revés de lo que manda semver. Fuera de alcance mientras el proyecto use `X.Y.Z` plano; si algún día se usan prereleases hay que sustituir la comparación.

**La imagen web promovida deja de ser byte a byte la anterior** → El estampado de la decisión 3b agrega una capa, así que `web:2.1.0` y `web:2.0.19` tienen digests distintos y ya no se puede demostrar comparando digests que sean el mismo artefacto. Se degrada de una garantía verificable a una confianza en el pipeline. Mitigación: la capa estampada contiene un único archivo de texto, así que la diferencia es auditable inspeccionando la capa. `api`, `worker` y `migrate` conservan la identidad byte a byte.

**El estampado necesita traer la imagen base al runner** → A diferencia de la copia pura de manifiesto, que es un `PUT` contra el registry, apilar una capa obliga al builder a resolver la imagen anterior. La promoción de `web` pasa de segundos a algo del orden del minuto. Sigue siendo un orden de magnitud menos que reconstruirla, pero deja de ser gratuita.

**Menos redundancia frente a fallos transitorios de build** → Hoy un fallo intermitente tiene dos oportunidades (build y publish). Con un solo build por servicio, una sola. Se acepta: la duplicación actual no fue diseñada como reintento y un rerun del job cubre el caso.

## Migration Plan

1. Crear `VERSION` en la raíz con el valor actual (`2.0.20`) y dejar de tocar los tres archivos de versión de servicio.
2. Reescribir el workflow. El baseline del primer release será `2.0.19`, el tag más alto publicado.
3. Los commits de esta propia migración tocan `backend/`, `worker/`, `frontend/` y posiblemente `dbmate/`, así que el primer release reconstruirá todo. Es el caso seguro y sirve de validación: los cuatro tags nuevos quedan publicados y el invariante de la decisión 5 se restablece.
4. A partir del segundo release la promoción empieza a aplicarse.
5. Eliminar la sección "Versiones" de `CLAUDE.md`.

**Rollback:** el workflow anterior se restaura desde git y vuelve a leer `backend/pyproject.toml`. La única condición es que ese archivo tenga un valor coherente con el último tag publicado en el momento de revertir. Las imágenes ya publicadas no requieren ninguna acción: los nombres, las etiquetas y las referencias de `compose.yaml` no cambian en ningún punto de esta migración.

## Open Questions

Ninguna. Las dos que quedaron abiertas al redactar este documento se resolvieron:

- **`workflow_dispatch`** se descarta, no se difiere. Ver Non-Goals.
- **`APP_VERSION` en el entorno de despliegue** no se define en ningún lado: el número viaja dentro de la imagen, estampado durante la promoción. Ver decisiones 3b y 8.
