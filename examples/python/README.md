# Python Scripts para MITM Proxy

Los scripts Python permiten procesar requests y responses dinámicamente en el proxy MITM.
El proxy invoca el script como **subproceso**, enviando JSON por **stdin** y recibiendo JSON por **stdout**.

## Contrato JSON

### Input (JSON enviado por stdin al script)

#### Request/Origin — el script genera la response completa

```json
{
  "phase": "request",
  "mode": "origin",
  "url": "https://api.example.com/v2/users/123",
  "method": "GET",
  "headers": {"Accept": "application/json", "Authorization": "Bearer xyz"},
  "body": null,
  "rule_pattern": "*://api.example.com/v2/*"
}
```

#### Request/Filter — el script modifica el request

```json
{
  "phase": "request",
  "mode": "filter",
  "url": "https://api.example.com/v2/users/123",
  "method": "GET",
  "headers": {"Accept": "application/json"},
  "body": null,
  "rule_pattern": "*://api.example.com/*"
}
```

#### Response/Filter — el script modifica la response del servidor

```json
{
  "phase": "response",
  "mode": "filter",
  "url": "https://api.example.com/v2/users/123",
  "method": "GET",
  "request_headers": {"Accept": "application/json"},
  "request_body": null,
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"name\":\"Juan\",\"email\":\"juan@dev.com\"}",
  "rule_pattern": "*://api.example.com/v2/*"
}
```

### Output (JSON que el script debe escribir por stdout)

#### Mode = Origin (phase = Request): el script responde directamente

```json
{
  "status": 200,
  "headers": {"Content-Type": "application/json", "X-Script-Generated": "true"},
  "body": "{\"users\": [{\"id\": 1, \"name\": \"Mock\"}]}"
}
```

#### Mode = Filter (phase = Request): modifica el request

```json
{
  "method": "GET",
  "url": "https://api.example.com/v2/users/123?debug=true",
  "headers": {"Authorization": "Bearer new-token", "X-Debug": "true"},
  "body": null
}
```

#### Mode = Filter (phase = Response): modifica la response

```json
{
  "status": 200,
  "headers": {"Content-Type": "application/json"},
  "body": "{\"name\":\"Juan\",\"email\":\"[REDACTED]\"}"
}
```

## Combinaciones Phase × Mode

| Phase | Mode | Comportamiento | Input | Output |
|-------|------|---------------|-------|--------|
| **Request** | **Origin** | El script genera la response completa. El request **NO** va al upstream. | url, method, headers, body | status, headers, body |
| **Request** | **Filter** | El script modifica el request antes de enviar al upstream. | url, method, headers, body | method, url, headers, body |
| **Response** | **Filter** | El script modifica la response del servidor antes de devolver al cliente. | url, method, request_headers, request_body, status, headers, body | status, headers, body |
| **Response** | **Origin** | ⚠️ **No válido** — la response ya viene del upstream. Se ignora. Usa Filter. | — | — |

## Reglas de fallback (cuando el script falla)

- **Origin mode**: Si el script falla (timeout, error, JSON inválido), el proxy devuelve **500 Internal Server Error** con un mensaje descriptivo.
- **Filter mode**: Si el script falla, el proxy **pasa el tráfico original sin modificaciones** (passthrough graceful). No se rompe el flujo del proxy.

## Configuración de reglas

Las reglas se configuran en la UI → **Python Scripts** y se persisten en `~/.valdam-proxy/config.toml`:

```toml
[[script_rules]]
enabled = true
match_pattern = "*://api.example.com/v2/*"
phase = "Response"
mode = "Filter"
script_path = "/Users/usuario/scripts/strip_pii.py"
description = "Remover PII de responses de usuarios"
http_methods = ["GET"]
timeout_ms = 5000
```

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `enabled` | bool | Si la regla está activa |
| `match_pattern` | string | Patrón glob con `*` wildcard |
| `phase` | "Request" / "Response" | Fase del tráfico |
| `mode` | "Origin" / "Filter" | Modo de operación |
| `script_path` | string | Ruta absoluta al archivo `.py` |
| `description` | string | Descripción opcional |
| `http_methods` | string[] | Métodos HTTP (vacío = todos) |
| `timeout_ms` | u64 | Timeout (100-60000ms, default 5000) |

### Orden de evaluación

Las reglas se evalúan **en orden** (primera coincidencia gana), igual que Map Rules.
La interacción con otros sistemas:

1. **Map Rules** tienen prioridad — si una Map Rule coincide, el request no llega a Script Rules.
2. **Script Origin** se evalúa después de Map Rules — si coincide, el request no va al upstream.
3. **Script Filter/Request** se evalúa después de Rewrite Rules, antes de DNS mapping.
4. **Script Filter/Response** se evalúa después de Rewrite Rules en handle_response.

## Mejores prácticas

1. **Usa `print()` para debug** — `print()` va a stderr (no stdout), así que no rompe el JSON output. El proxy logea stderr automáticamente.
2. **Mantén los scripts simples** — el proxy tiene timeout configurable. Scripts complejos deben procesar rápido.
3. **Retorna JSON válido** — stdout debe contener exactamente un objeto JSON. No agregues texto extra antes o después.
4. **Maneja errores gracefulmente** — en Filter mode, si el script no puede procesar, retorna el input original sin cambios.
5. **Usa rutas absolutas** — `script_path` debe ser ruta absoluta al `.py`, no relativa.

## Scripts de ejemplo

| Archivo | Phase/Mode | Descripción |
|---------|-----------|-------------|
| `strip_pii.py` | Response/Filter | Remueve campos PII (email, phone, address) de JSON responses |
| `mock_api.py` | Request/Origin | Genera responses mock para endpoints de API |
| `modify_request.py` | Request/Filter | Agrega headers de debug y parámetros de query al request |

## Ejemplo mínimo

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
