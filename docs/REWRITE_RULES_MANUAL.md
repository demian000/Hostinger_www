# Manual: Rewrite Rules

Las **Rewrite Rules** permiten modificar requests y responses al vuelo mientras el tráfico pasa por el proxy. Puedes agregar, reemplazar o eliminar headers, modificar el body, y cambiar el código de estado HTTP.

---

## Conceptos básicos

### Estructura de una regla

Cada regla tiene:

| Campo | Descripción |
|-------|-------------|
| **Habilitada** | Si la regla está activa. Las deshabilitadas se ignoran. |
| **Condiciones (AND)** | Criterios para decidir si la regla aplica. TODAS deben coincidir. |
| **Tipo de coincidencia (legacy)** | Alternativa antigua: Url, Header, Body o Status. |
| **Patrón** | Texto a buscar — su significado depende del tipo de coincidencia y tipo de reemplazo. |
| **Tipo de reemplazo** | Qué se modifica: Header, Body o Status. |
| **Valor de reemplazo** | Texto que se aplica — su significado depende del tipo de reemplazo. |
| **Métodos HTTP** | Filtra por método GET, POST, etc. Vacío = todos. |

### Orden de evaluación

Las reglas se evalúan **en orden** (primera coincidencia gana). Si dos reglas coinciden con el mismo tráfico, solo la primera se aplica.

### Tipos de reemplazo

| Tipo | Qué hace | Campos clave |
|------|----------|-------------|
| **Header** (`HeaderValue`) | Agrega o reemplaza un header HTTP | Valor = valor del header, Reemplazo = nombre del header |
| **Body** (`BodyContent`) | Busca y reemplaza texto en el body | Patrón = texto a buscar, Reemplazo = nuevo texto |
| **Status** (`StatusCode`) | Cambia el código de estado HTTP | Reemplazo = nuevo código (ej. `200`, `404`) |

---

## Caso 1: Agregar un header

### Ejemplo: Agregar `X-Debug: true` a todas las requests

1. Haz clic en **Nueva regla**
2. En **Tipo de reemplazo**, selecciona **Header** (`HeaderValue`)
3. Se auto-agrega una condición `Url = *` (que coincide con todo)
4. En **Valor del header**, escribe `true`
5. En **Nombre del header**, escribe `X-Debug`
6. Verifica el preview: `X-Debug: true`
7. Guarda la regla

> **⚠️ Importante**: Cuando el tipo de reemplazo es **Header**, el campo **"Valor del header"** es el contenido que se asigna al header, y **"Nombre del header"** es el nombre del header. La UI muestra un preview del resultado.

### Ejemplo: Agregar header solo a un dominio específico

1. Tipo de reemplazo: **Header**
2. Condiciones: agregar `Host = api.ejemplo.com`
3. Valor del header: `application/json`
4. Nombre del header: `Content-Type`
5. Resultado: todas las requests a `api.ejemplo.com` recibirán `Content-Type: application/json`

### ¿Qué pasa si el header ya existe?

- Si el header **ya existe**, su valor se **reemplaza** con el nuevo.
- Si el header **no existe**, se **agrega** uno nuevo.

---

## Caso 2: Reemplazar texto en el body

### Ejemplo: Cambiar `http://` por `https://` en responses

1. Tipo de coincidencia (legacy): **Url** con patrón `*` (o usa condiciones)
2. Tipo de reemplazo: **Body** (`BodyContent`)
3. Patrón de coincidencia: `http://`
4. Texto de reemplazo: `https://`
5. Guarda la regla

### Ejemplo: Reemplazar versión de API en el body

1. Condiciones: `Path = /api/v1/*`
2. Tipo de reemplazo: **Body**
3. Patrón: `v1`
4. Reemplazo: `v2`
5. Resultado: toda la palabra `v1` en el body se cambia a `v2`

> **Nota**: La búsqueda y reemplazo en el body es **case-sensitive** y reemplaza **todas** las ocurrencias (no solo la primera).

---

## Caso 3: Cambiar el código de estado

### Ejemplo: Cambiar todos los 404 a 200

1. Condiciones: `Status = 404` (o legacy: `Status` con patrón `404`)
2. Tipo de reemplazo: **Status** (`StatusCode`)
3. Nuevo código de estado: `200`
4. Guarda la regla

### Ejemplo: Cambiar cualquier 5xx a 503

1. Condiciones: `Status = 5*` (o legacy: `Status` con patrón `5*`)
2. Tipo de reemplazo: **Status**
3. Nuevo código: `503`

---

## Condiciones AND vs. Legacy Match Type

### Condiciones AND (recomendado)

Las condiciones permiten especificar **múltiples criterios** que TODOS deben coincidir:

| Tipo de condición | Qué coincide | Ejemplo patrón |
|-------------------|-------------|----------------|
| **Url** | URL completa | `*://api.ejemplo.com/*` |
| **Path** | Solo el path | `/api/v1/*` |
| **Host** | El dominio | `*.ejemplo.com` |
| **Query** | Query string | `id=*` |
| **Header** | Header HTTP | `Content-Type: application/json` |
| **Body** | Contenido del body | `texto a buscar` |
| **Status** | Código de estado | `4*` |

Ejemplo: Si quieres que una regla solo aplique a POST requests al host `api.ejemplo.com` con path `/users`:
- Condición 1: `Host = api.ejemplo.com`
- Condición 2: `Path = /users`
- Métodos HTTP: `POST`

### Legacy Match Type (alternativa simple)

Cuando no hay condiciones, se usa el tipo de coincidencia legacy:

| Tipo | Qué hace | Patrón |
|------|----------|--------|
| **Url** | Coincide con la URL completa usando glob | `*://api.ejemplo.com/*` |
| **Header** | Busca un header por nombre, su valor debe contener el reemplazo | Nombre del header |
| **Body** | Busca texto en el body | Texto a buscar |
| **Status** | Coincide con código de estado usando glob | `4*` |

> **⚠️ Limitación**: Cuando usas tipo legacy **Url** o **Header** junto con reemplazo **Header**, el patrón de coincidencia también se usa como valor del header. Esto puede causar resultados incorrectos. **Recomendamos usar condiciones AND** para el reemplazo de headers.

---

## Patrones glob (wildcards)

Los patrones glob usan `*` como comodín:

| Patrón | Qué coincide |
|---------|-------------|
| `*` | Todo (cualquier URL, cualquier status) |
| `*://api.ejemplo.com/*` | Cualquier protocolo, solo api.ejemplo.com, cualquier path |
| `*.ejemplo.com` | Cualquier subdominio de ejemplo.com |
| `/api/v1/*` | Cualquier path que empieza con /api/v1/ |
| `4*` | Cualquier código 4xx |
| `4??` | Cualquier código 4xx (tres dígitos) |
| `200` | Solo 200 exacto |

---

## Filtrar por método HTTP

El campo **Métodos HTTP** filtra a qué métodos aplica la regla:

- **Vacío**: la regla aplica a TODOS los métodos (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- **GET, POST**: la regla solo aplica a requests GET y POST

---

## Configuración en config.toml

Las reglas se persisten en `~/.valdam-proxy/config.toml`:

```toml
[[rewrite_rules]]
enabled = true
match_type = "Url"
match_pattern = "*"
replace_type = "HeaderValue"
replace_value = "X-Debug"
http_methods = []

[[rewrite_rules]]
enabled = true
match_type = "Url"
match_pattern = "*"
replace_type = "BodyContent"
replace_value = "https://"
http_methods = ["GET"]

[[rewrite_rules]]
enabled = true
conditions = [{ condition_type = "Host", pattern = "api.ejemplo.com" }]
match_type = "Url"
match_pattern = "true"
replace_type = "HeaderValue"
replace_value = "X-Debug"
http_methods = []
```

> **Nota sobre HeaderValue**: En el formato TOML/Rust, `match_pattern` es el **valor del header** y `replace_value` es el **nombre del header**. Es inverso a lo que podría parecer: `replace_value = "X-Debug"` y `match_pattern = "true"` produce el header `X-Debug: true`.

---

## Ejemplos comunes

### Agregar header de debug a todas las requests

| Condiciones | Url = `*` |
|---|---|
| Reemplazo | Header |
| Valor del header | `true` |
| Nombre del header | `X-Debug` |

### Forzar Content-Type en responses de un dominio

| Condiciones | Host = `api.ejemplo.com` |
|---|---|
| Reemplazo | Header |
| Valor del header | `application/json` |
| Nombre del header | `Content-Type` |

### Eliminar header (reemplazar con vacío)

| Condiciones | Url = `*` |
|---|---|
| Reemplazo | Header |
| Valor del header | *(vacío)* |
| Nombre del header | `X-Powered-By` |

> Resultado: el header `X-Powered-By` se reemplaza con valor vacío. Nota: el header sigue existiendo con valor vacío — para eliminarlo completamente, considera usar un script Python (Response/Filter mode).

### Reemplazar URL base en el body

| Condiciones | Host = `prod.ejemplo.com` |
|---|---|
| Reemplazo | Body |
| Patrón | `https://prod.ejemplo.com` |
| Reemplazo | `https://staging.ejemplo.com` |

### Cambiar todos los 500 a 200 (para testing)

| Condiciones | Status = `5*` |
|---|---|
| Reemplazo | Status |
| Nuevo código | `200` |

### Agregar CORS headers a responses

| Condiciones | Url = `*` |
|---|---|
| Reemplazo | Header |
| Valor del header | `*` |
| Nombre del header | `Access-Control-Allow-Origin` |

---

## Troubleshooting

### "Se agrega `texto: texto` en vez del header que quiero"

Esto ocurre cuando se usan los campos incorrectamente. Verifica:
- **Valor del header** = el CONTENIDO del header (ej. `true`)
- **Nombre del header** = el NOMBRE del header (ej. `X-Debug`)
- Usa **condiciones AND** para matching, no el legacy match type

### La regla no aplica

Verifica:
1. La regla está **habilitada**
2. Las condiciones coinciden con el tráfico (usa el filtro de la dashboard para verificar)
3. Los métodos HTTP incluyen el método de la request (o está vacío para todos)
4. La regla no está después de otra que ya coincide (primera coincidencia gana)

### El header se agrega con valor incorrecto

Si usas legacy match type `Url` con patrón `*://api.ejemplo.com/*` y reemplazo Header, el valor del header será `*://api.ejemplo.com/*` (el patrón URL literal). Usa condiciones AND para separar el matching del valor del header.

---

## Interacción con otros sistemas

- **Map Rules** tienen prioridad — si una Map Rule coincide, el request se redirige y no llega a Rewrite Rules.
- **Script Rules** (Python Scripts) se evalúan después de Rewrite Rules en la pipeline del proxy.
- Rewrite Rules aplican a **requests** (antes de enviar al servidor) y a **responses** (antes de devolver al cliente).
