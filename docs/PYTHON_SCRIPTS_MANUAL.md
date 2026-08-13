# Manual: Python Scripts

Los **Python Scripts** permiten procesar requests y responses dinámicamente usando scripts Python. El proxy invoca el script como subprocess, enviando JSON por stdin y recibiendo JSON por stdout.

---

## Conceptos básicos

### Fases (Phase)

| Fase | Qué hace |
|------|----------|
| **Request** | Procesa el request antes de enviar al servidor |
| **Response** | Procesa la response del servidor antes de devolver al cliente |

### Modos (Mode)

| Modo | Qué hace |
|------|----------|
| **Origin** | El script genera la response completa. El request **NO** va al upstream. |
| **Filter** | El script modifica el tráfico en tránsito (request o response). |

### Combinaciones Phase × Mode

| Phase | Mode | Comportamiento | Input | Output |
|-------|------|---------------|-------|--------|
| **Request** | **Origin** | Script genera la response completa. Similar a Map Local pero dinámico. | url, method, headers, body | status, headers, body |
| **Request** | **Filter** | Script modifica el request antes de enviar al upstream. | url, method, headers, body | method, url, headers, body |
| **Response** | **Filter** | Script modifica la response antes de devolver al cliente. | url, method, request_headers, request_body, status, headers, body | status, headers, body |
| **Response** | **Origin** | ⚠️ **No válido** — la response ya viene del upstream. Se ignora. Usa Filter. | — | — |

---

## Estructura de una regla

| Campo | Descripción |
|-------|-------------|
| **Habilitada** | Si la regla está activa. |
| **Patrón de coincidencia** | URL glob con `*` wildcards. Ej: `*://api.ejemplo.com/*` |
| **Fase** | `Request` o `Response` |
| **Modo** | `Origin` (genera response) o `Filter` (modifica tráfico) |
| **Ruta del script** | Ruta absoluta al archivo `.py`. Debe ser ejecutable con `python3`. |
| **Métodos HTTP** | Filtra por método. Vacío = todos. |
| **Timeout (ms)** | Tiempo máximo de espera. Rango: 100-120000. Default: 15000. |
| **Descripción** | Texto opcional. |

### Orden de evaluación

Las reglas se evalúan **en orden** (primera coincidencia gana). La posición #1 = mayor prioridad.

### Prioridad en la pipeline

1. **Map Rules** tienen prioridad — si una Map Rule coincide, el request no llega a Script Rules.
2. **Script Origin (Request)** se evalúa después de Map Rules.
3. **Script Filter (Request)** se evalúa después de Rewrite Rules.
4. **Script Filter (Response)** se evalúa después de Rewrite Rules en handle_response.

---

## Contrato JSON

### Input (JSON enviado por stdin al script)

#### Request/Origin — el script genera la response completa

```json
{
  "phase": "request",
  "mode": "origin",
  "url": "https://api.ejemplo.com/v2/users/123",
  "method": "GET",
  "headers": {"Accept": "application/json"},
  "body": null,
  "rule_pattern": "*://api.ejemplo.com/v2/*"
}
```

#### Request/Filter — el script modifica el request

```json
{
  "phase": "request",
  "mode": "filter",
  "url": "https://api.ejemplo.com/v2/users/123",
  "method": "GET",
  "headers": {"Accept": "application/json"},
  "body": null,
  "rule_pattern": "*://api.ejemplo.com/*"
}
```

#### Response/Filter — el script modifica la response

```json
{
  "phase": "response",
  "mode": "filter",
  "url": "https://api.ejemplo.com/v2/users/123",
  "method": "GET",
  "request_headers": {"Accept": "application/json"},
  "request_body": null,
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"name\":\"Juan\",\"email\":\"juan@dev.com\"}",
  "rule_pattern": "*://api.ejemplo.com/v2/*"
}
```

### Output (JSON que el script debe escribir por stdout)

#### Mode = Origin (phase = Request)

```json
{
  "status": 200,
  "headers": {"Content-Type": "application/json", "X-Script-Generated": "true"},
  "body": "{\"users\": [{\"id\": 1, \"name\": \"Mock\"}]}"
}
```

#### Mode = Filter (phase = Request) — modifica el request

```json
{
  "method": "GET",
  "url": "https://api.ejemplo.com/v2/users/123?debug=true",
  "headers": {"Authorization": "Bearer new-token", "X-Debug": "true"},
  "body": null
}
```

#### Mode = Filter (phase = Response) — modifica la response

```json
{
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"name\":\"Juan\",\"email\":\"[REDACTED]\"}"
}
```

---

## Fallback (cuando el script falla)

| Modo | Comportamiento si falla |
|------|------------------------|
| **Origin** | Proxy devuelve **500 Internal Server Error** con header `X-Script-Error: true` y mensaje descriptivo. |
| **Filter** | Proxy **pasa el tráfico original sin modificaciones** (passthrough graceful). No se rompe el flujo. |

Causas de fallo: timeout, error de ejecución, JSON inválido en stdout, texto extra antes/después del JSON.

---

## Script mínimo

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)

# Tu lógica aquí...

result = {
    "status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps({"message": "hello from script"}),
}
json.dump(result, sys.stdout)
```

---

## Debug con print()

`print()` va a **stderr** (no stdout), así que no rompe el JSON output. El proxy logea stderr automáticamente.

```python
import json, sys

data = json.load(sys.stdin)
print(f"DEBUG: URL={data['url']}, method={data['method']}")  # → stderr

result = {"status": 200, "headers": {}, "body": ""}
json.dump(result, sys.stdout)  # → stdout (lo que lee el proxy)
```

---

## Ejemplos prácticos

### Mock de API (Request/Origin)

Sirve una response mock para endpoints de API sin tener un servidor real.

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)

if "/users" in data["url"]:
    result = {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"users": [{"id": 1, "name": "Mock User"}]})
    }
else:
    result = {
        "status": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "not found"})
    }

json.dump(result, sys.stdout)
```

### Agregar auth header (Request/Filter)

Agrega un header de autenticación a requests que van a una API específica.

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
headers = data.get("headers", {})
headers["Authorization"] = "Bearer my-secret-token"

result = {
    "method": data["method"],
    "url": data["url"],
    "headers": headers,
    "body": data.get("body"),
}
json.dump(result, sys.stdout)
```

### Remover PII de responses (Response/Filter)

Elimina campos sensibles (email, phone) de JSON responses.

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
body = json.loads(data.get("body", "{}"))

for field in ["email", "phone", "address"]:
    if field in body:
        body[field] = "[REDACTED]"

result = {
    "status": data["status"],
    "headers": data["headers"],
    "body": json.dumps(body),
}
json.dump(result, sys.stdout)
```

---

## Mejores prácticas

1. **Usa `print()` para debug** — no rompe el JSON output.
2. **Mantén los scripts simples** — el proxy tiene timeout configurable.
3. **Retorna JSON válido** — stdout debe contener exactamente un objeto JSON.
4. **Maneja errores gracefully** — en Filter mode, si no puedes procesar, retorna el input sin cambios.
5. **Usa rutas absolutas** — `script_path` debe ser ruta absoluta al `.py`.
6. **No escribas texto extra en stdout** — ni prints, ni logs, ni mensajes antes/después del JSON.

---

## Configuración en config.toml

```toml
[[script_rules]]
enabled = true
match_pattern = "*://api.ejemplo.com/v2/*"
phase = "Response"
mode = "Filter"
script_path = "/Users/usuario/scripts/strip_pii.py"
description = "Remover PII de responses"
http_methods = ["GET"]
timeout_ms = 15000
```

---

## Troubleshooting

### El script no se ejecuta

1. Verifica que `python3` está disponible en el PATH
2. La ruta debe ser **absoluta**
3. El archivo debe tener permisos de lectura

### El script devuelve error 500 (Origin mode)

1. Verifica que stdout contiene JSON válido
2. No hay texto extra (prints, mensajes) antes/después del JSON
3. El timeout no es demasiado corto

### El tráfico no se modifica (Filter mode)

Si el script falla, el proxy pasa el tráfico original sin cambios (passthrough). Verifica stderr para mensajes de error.
