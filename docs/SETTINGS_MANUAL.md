# Manual: Preferencias (Settings)

Las **Preferencias** permiten configurar el proxy runtime, SSL/sniffer behavior, y certificados. Tres tabs: Proxy, Seguridad, Acerca de.

---

## Tab: Proxy

### Runtime controls

| Control | Descripción |
|---------|-------------|
| **Iniciar** | Inicia el proxy en el host/port configurado |
| **Detener** | Detiene el proxy. Ya puedes editar host, port y certificados. |

El indicador de estado muestra:
- 🟢 **Activo**: proxy corriendo y escuchando
- 🔴 **Detenido**: proxy inactivo

### Configuración del proxy

| Campo | Default | Descripción |
|-------|---------|-------------|
| **Host/Interface** | `127.0.0.1` | Interface donde escucha el proxy. `0.0.0.0` = todas las interfaces (para dispositivos en la red). |
| **Puerto** | `8080` | Port donde escucha. |
| **CA cert** | `~/.valdam-proxy/ca.pem` | Ruta al archivo de certificado CA (`.pem`). |
| **CA key** | `~/.valdam-proxy/ca.key` | Ruta al archivo de key CA (`.key`). |

⚠️ **No se puede editar host, port o certificados mientras el proxy está activo**. Detén el proxy primero.

### Auto-start

Toggle **"Auto-start al abrir"** — inicia el proxy automáticamente cuando se abre la aplicación.

### Guardar

El botón **Guardar** persiste la configuración en `~/.valdam-proxy/config.toml`. Solo disponible cuando el proxy está detenido.

---

## Sniffer SSL

### Modos de interceptación

| Modo | Descripción |
|------|-------------|
| **Todos** | MITM para TODOS los hosts HTTPS. Cualquier conexión HTTPS se intercepta. |
| **Lista** | MITM solo para los hosts listados. Otros hosts van en passthrough. |
| **Ninguno** | Passthrough total. No se intercepta ningún host HTTPS. |

### Agregar/eliminar hosts

1. Ingresa el hostname en el campo (ej: `api.ejemplo.com`)
2. Haz clic en **Agregar** o presiona Enter
3. El host aparece en la lista con botón ✕ para eliminar
4. El modo cambia automáticamente a "Lista" si estaba en "Todos" o "Ninguno"

### Hosts observados (auto-detectados)

El proxy detecta automáticamente los hosts que pasan por CONNECT tunnels. Cada host observado tiene:
- **"usado"**: el host ya está en la lista de interceptación
- **"usar"**: el host no está en la lista — haz clic para agregarlo

### Passthrough hosts visibles en el inspector

Los hosts que **no** son interceptados por el proxy SSL (passthrough) ahora aparecen en la tabla de tráfico del inspector:

- **Entradas CONNECT virtuales**: el proxy crea una entrada CONNECT por cada túnel SSL no interceptado
- **Badge "No SSL"**: se muestra un badge ámbar con el texto **"No SSL"** para distinguirlos de conexiones normales
- **Solo dominio y hora**: como el tráfico passthrough es un túnel TCP transparente, solo se muestra el dominio y el timestamp — no hay headers, body, status code ni latencia
- **Visibles siempre**: estos hosts no se ocultan por el filtro de SSL activo (por definición, no están siendo interceptados)
- **Útil para diagnosticar**: si esperabas ver tráfico HTTP detallado y solo ves entradas CONNECT con "No SSL", significa que el host no está en la lista SSL o el certificado CA no está instalado en el cliente

### MITM Failed hosts (passthrough automático)

Cuando el MITM falla repetidamente para un host, se agrega automáticamente a la lista de passthrough. El proxy NO intentará MITM para estos hosts hasta que se resetee.

| Acción | Descripción |
|--------|-------------|
| **Reintentar MITM** (global) | Resetea toda la lista de hosts fallidos. El proxy reintentará MITM para todos. |
| **Reintentar** (per-host) | Resetea un host específico para reintentar MITM. |

### Timeout MITM fallido

Configura cuántos segundos esperar antes de marcar un host como permanentemente fallido. Default: 30 segundos. Rango: 1–300.

### Cooldown reintento MITM

Configura el tiempo de espera antes de que el proxy reintente automáticamente MITM para un host fallido. Default: 30 segundos. Rango: 5–600.

### Guardar SSL

El botón **Guardar SSL** persiste la configuración SSL en `config.toml`. Se aplica instantáneamente (hot-reload, no necesita reiniciar proxy).

---

## Tab: Seguridad

### Estado del certificado raíz

Verifica 4 condiciones para MITM:

| Check | Qué verifica |
|-------|-------------|
| **Archivo CA cert** | El archivo `.pem` existe en la ruta configurada |
| **Archivo CA key** | El archivo `.key` existe en la ruta configurada |
| **Proxy activo** | El proxy está corriendo |
| **SSL proxy habilitado** | El modo SSL no es "Ninguno" |

Si todos son ✅ — MITM está listo para interceptar HTTPS.

### Fechas del certificado

Se muestran las fechas de emisión y expiración del certificado CA. Si el certificado está vencido, se muestra en rojo con "Vencido".

### Regenerar CA

El botón **Regenerar CA** crea un nuevo certificado CA:
1. Detiene el proxy si está activo
2. Reemplaza los archivos `ca.pem` y `ca.key`
3. ⚠️ **Todos los dispositivos que confiaban en el certificado anterior deben instalar el nuevo certificado**

### Reglas de confianza (instalar certificado)

#### Desde otro dispositivo (en la misma red)

1. Configura el proxy en el dispositivo (IP + port)
2. Abre `http://valdam.pro` en el navegador del dispositivo
3. Descarga e instala el certificado CA

#### iOS

1. Settings → General → VPN/Profiles → Install profile
2. Settings → General → Info → Certificate Trust Settings → Enable full trust

#### Android

1. Settings → Security → Install certificate → CA certificate
2. ⚠️ Apps con certificate pinning no funcionarán con MITM

#### macOS

1. Abre el certificado → Keychain Access → Set to "Always trust"

#### Windows

1. Install certificate → Local Machine → Trusted Root Certification Authorities

### Avisos de tráfico cifrado

- MITM solo funciona si el CA cert es confiado por el cliente
- Entries que solo muestran CONNECT (sin headers/body) indican que el certificado no está confiado
- Apps con certificate pinning no funcionan — usa modo Passthrough SSL para esas apps
- El portal de certificados (`http://valdam.pro`) está disponible mientras el proxy está activo

---

## Tab: Acerca de

Información general de la aplicación:
- Versión
- Tech stack: Tauri v2, React, TypeScript, Rust
- Links: GitHub (rdvt), website (valedam.lat)

---

## Configuración en config.toml

```toml
[proxy]
port = 8080
interface = "127.0.0.1"
max_connections = 1000
auto_start = true

[tls]
ca_cert = "~/.valdam-proxy/ca.pem"
ca_key = "~/.valdam-proxy/ca.key"
regenerate_on_start = false

[proxy.ssl]
mode = "selected"
hosts = ["api.ejemplo.com"]
mitm_stale_timeout_secs = 10
```

---

## Troubleshooting

### El proxy no inicia

1. Verifica que el port no está en uso por otra aplicación
2. Los archivos CA cert y CA key deben existir
3. Si el cert está vencido, regenera CA

### MITM no funciona (CONNECT entries sin contenido)

1. Instala el CA cert en el dispositivo cliente
2. Para iOS: habilita "Full Trust" en Certificate Trust Settings
3. Verifica que el modo SSL no es "Ninguno"
4. Verifica que el host está en la lista (si modo es "Lista")

### Hosts en passthrough automático

1. El MITM falló repetidamente para esos hosts
2. Haz clic en "Reintentar MITM" para resetear
3. Verifica que el certificado está instalado en el cliente
