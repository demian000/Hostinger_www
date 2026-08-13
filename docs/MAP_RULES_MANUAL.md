# Manual: Map Rules

Las **Map Rules** permiten interceptar requests que coinciden con un patrón de URL y redirigirlos a un archivo local (Map Local) o a una URL remota diferente (Map Remote). Equivalente a las funciones "Map Local" y "Map Remote" de Charles Proxy.

---

## Conceptos básicos

### Tipos de Map

| Tipo | Qué hace | Ejemplo |
|------|----------|---------|
| **Map Local** | Sirve un archivo local como response. El request nunca va al upstream. | `*://api.ejemplo.com/users/*` → `/home/user/mocks/users.json` |
| **Map Remote** | Redirige el request a otra URL. Se hace un nuevo request HTTP al destino. | `*://prod.ejemplo.com/*` → `https://staging.ejemplo.com/*` |

### Estructura de una regla

| Campo | Descripción |
|-------|-------------|
| **Habilitada** | Si la regla está activa. Las deshabilitadas se ignoran. |
| **Patrón de coincidencia** | URL glob con `*` wildcards. Ej: `*://api.ejemplo.com/*` |
| **Tipo de mapa** | `Local` (archivo) o `Remote` (URL alternativa) |
| **Destino** | Para Local: ruta absoluta al archivo. Para Remote: URL completa. |
| **Preservar host original** | Solo para Remote. Preserva el header `Host` original y agrega `X-Original-Host`. |
| **Descripción** | Texto opcional para identificar la regla. |

### Orden de evaluación

Las reglas se evalúan **en orden** (primera coincidencia gana). La posición #1 tiene la mayor prioridad. Puedes reordenar las reglas arrastrándolas o usando los controles de posición.

### Prioridad en la pipeline

- **Map Rules** tienen prioridad sobre **Script Rules** — si una Map Rule coincide, el request no llega a Script Rules.
- Map Rules se evalúan antes de Rewrite Rules.
- Si una Map Rule coincide, el request **no va al upstream** (se resuelve localmente o se redirige).

---

## Map Local: Servir archivos locales

### Cómo funciona

Cuando un request coincide con el patrón, el proxy lee el archivo desde disco y lo devuelve como response. El request nunca llega al servidor upstream.

### Content-Type automático

El proxy infiere el Content-Type del archivo según su extensión:

| Extensión | Content-Type |
|-----------|-------------|
| `.json` | `application/json` |
| `.html` | `text/html` |
| `.xml` | `application/xml` |
| `.txt` | `text/plain` |
| `.png` | `image/png` |
| `.jpg` | `image/jpeg` |
| `.css` | `text/css` |
| `.js` | `application/javascript` |

### Headers de tracking

El proxy agrega los siguientes headers a las respuestas Map Local:

| Header | Valor | Propósito |
|--------|-------|-----------|
| `X-Map-Local` | Ruta del archivo | Identifica que la response fue generada por Map Local |
| `Cache-Control` | `no-cache, no-store, must-revalidate` | Evita que el navegador cachee la respuesta. Los cambios al archivo se reflejan inmediatamente |
| `Pragma` | `no-cache` | Compatibilidad con HTTP/1.0 |
| `Expires` | `0` | Marca la respuesta como expirada |

> **Importante**: Sin estos headers, los navegadores cachearían la respuesta y los cambios hechos al archivo fuera del proxy no se reflejarían hasta vaciar la caché del navegador. Los headers aseguran que cada request obtenga el contenido fresco del archivo.

### Editor JSON integrado

Para archivos `.json`, la UI muestra un editor integrado con:
- Vista formateada del JSON
- Edición directa (Ctrl+S para guardar, Ctrl+Z para undo, Esc para salir)
- Vista de diferencias (diff)
- Drag-and-drop: arrastra archivos desde Finder al campo destino

### Ejemplo: Mock de API

1. Crea un archivo `/home/user/mocks/users.json`:
   ```json
   [{"id": 1, "name": "Mock User"}]
   ```
2. Crea una regla Map Local:
   - Patrón: `*://api.ejemplo.com/users*`
   - Destino: `/home/user/mocks/users.json`
3. Todas las requests a `/users` recibirán el JSON mock como response.

### Error: Archivo no encontrado

Si el archivo no existe en la ruta especificada, el proxy devuelve `404 Not Found` con un mensaje descriptivo.

---

## Map Remote: Redirigir a otra URL

### Cómo funciona

El proxy intercepta el request, crea un nuevo request HTTP al destino, y devuelve la response del destino al cliente. El cliente nunca se comunica directamente con el servidor original.

### Preservar host original

Por defecto, Map Remote cambia el header `Host` al host del destino. Si activas **"Preservar host original"**:
- El header `Host` se mantiene con el valor original
- Se agrega un header `X-Original-Host` con el host original
- Esto es útil cuando el servidor destino espera el host original (ej: virtual hosts)

### Query parameters

Los query parameters del request original se conservan y se agregan al destino. Ejemplo:
- Original: `https://prod.ejemplo.com/api?q=test`
- Destino: `https://staging.ejemplo.com/api`
- Resultado: `https://staging.ejemplo.com/api?q=test`

### Headers de tracking

El proxy agrega dos headers:
- `X-Map-Remote-Target`: URL destino
- `X-Map-Remote-Original-Url`: URL original

### Ejemplo: Redirigir API de prod a staging

1. Crea una regla Map Remote:
   - Patrón: `*://prod.ejemplo.com/*`
   - Destino: `https://staging.ejemplo.com`
   - Preservar host: desactivado (el staging server espera su propio host)
2. Todas las requests a `prod.ejemplo.com` se redirigen a `staging.ejemplo.com`

### Ejemplo: Redirigir API a localhost

1. Patrón: `*://api.external.com/v1/*`
2. Destino: `http://localhost:3000`
3. Las requests se redirigen a tu servidor local de desarrollo

### Configuración de reqwest

Map Remote usa reqwest con:
- `no_proxy` para evitar loops
- Acepta certificados inválidos (para testing)
- Timeout: 15 segundos (conexión: 5 segundos)
- DNS mappings se aplican al destino

---

## Patrones glob (wildcards)

| Patrón | Qué coincide |
|---------|-------------|
| `*` | Todo — cualquier URL |
| `*://api.ejemplo.com/*` | Cualquier protocolo, solo api.ejemplo.com |
| `*://*.ejemplo.com/*` | Cualquier subdominio de ejemplo.com |
| `*://*/path/*` | Cualquier dominio, solo paths que contienen /path/ |

### Normalización de URLs

Los ports default (`:443` para HTTPS, `:80` para HTTP) se eliminan antes del matching, así los patrones coinciden independientemente de si el port está explícito o no.

### Panel de preview en vivo

Al editar o crear una regla, el panel de preview se muestra automáticamente debajo del formulario con:

- **Input de URL**: textarea para ingresar la URL de prueba con tooltip explicativo
- **Resultado antes/después**: muestra la URL original y la transformada si coincide
- **Estado de coincidencia**: ✓ Coincide / ✗ No coincide
- **Badge de destino**: indica si es Map Local (📁) o Map Remote (🌐)

#### Captura de segmentos ($1, $2)

Cada `*` en el patrón captura un segmento de la URL real. Puedes usar `$1`, `$2`, etc. en el destino para reutilizarlos:

| Patrón | URL real | $1 captura | $2 captura |
|--------|----------|-----------|-----------|
| `https://*.ejemplo.com/*` | `https://api.ejemplo.com/v1/users` | `api` | `v1/users` |
| `https://api.ejemplo.com/*/items/*` | `https://api.ejemplo.com/v2/items/42` | `v2` | `42` |

Ejemplos de uso en el destino:
- Destino `/$2` + patrón `https://*.ejemplo.com/*` → resultado: `/v1/users`
- Destino `http://$1.local/$2` + patrón `https://*.ejemplo.com/*` → resultado: `http://api.local/v1/users`

El panel de preview resuelve `$1`, `$2` en vivo y muestra el resultado transformado automáticamente.

---

## Importar/Exportar reglas

### Exportar

Haz clic en el botón **Exportar** para descargar todas las reglas como un archivo JSON.

### Importar

Haz clic en **Importar** para cargar reglas desde un archivo JSON. Puedes elegir:
- **Fusionar**: agrega las reglas importadas a las existentes (sin duplicar)
- **Reemplazar**: elimina todas las reglas existentes y carga las importadas

---

## Configuración en config.toml

Las reglas se persisten en `~/.valdam-proxy/config.toml`:

```toml
[[map_rules]]
enabled = true
match_pattern = "*://api.ejemplo.com/users*"
map_type = "Local"
target = "/home/user/mocks/users.json"
description = "Mock de API users"

[[map_rules]]
enabled = true
match_pattern = "*://prod.ejemplo.com/*"
map_type = "Remote"
target = "https://staging.ejemplo.com"
preserve_host_header = false
description = "Redirigir prod a staging"
```

---

## Troubleshooting

### El archivo no se sirve

Verifica:
1. La ruta es **absoluta** (no relativa)
2. El archivo existe en disco
3. El patrón coincide con la URL del request (usa el panel de preview en vivo)
4. La regla está **habilitada**

### Map Remote devuelve error

Verifica:
1. El destino empieza con `http://` o `https://`
2. El servidor destino está accesible
3. No hay certificado SSL issues (el proxy acepta certificados inválidos)
4. El timeout no es demasiado corto (default: 15s)

### La regla no coincide

- Usa el **panel de preview** para verificar
- Recuerda que los ports default se normalizan
- Verifica que la regla no esté detrás de otra que ya coincide (primera coincidencia gana)
