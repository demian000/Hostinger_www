# Manual: DNS Tools

Las **DNS Tools** ofrecen dos funcionalidades: (1) un DNS Resolver para consultar direcciones IP de hostnames, y (2) Custom Host Mapping para sobreescribir la resolución DNS del tráfico del proxy (similar a `/etc/hosts`).

---

## DNS Resolver

### Qué hace

Resuelve hostnames a direcciones IP usando el sistema DNS del OS. No afecta el tráfico del proxy — es solo una herramienta de consulta.

### Cómo usar

1. Ingresa un hostname en el campo (ej: `api.ejemplo.com`)
2. Haz clic en **Resolver** o presiona Enter
3. Se muestra: hostname, tiempo de resolución, y todas las IPs encontradas

### Historial de resolución

Todas las consultas se guardan en el historial de la sesión (máximo 100 entries):

| Campo | Descripción |
|-------|-------------|
| **Hostname** | El dominio consultado |
| **Direcciones** | IPs encontradas |
| **Duración** | Tiempo de resolución en ms |
| **Timestamp** | Hora de la consulta |
| **Estado** | ✅ Exitoso / ❌ Error |
| **Badge "Slow"** | Se muestra si la resolución tomó > 1000ms |

Puedes limpiar el historial con el botón **Limpiar**.

### Quick resolve desde mappings

Cada fila en la lista de mappings tiene un botón **Resolver** para consultar rápidamente ese hostname.

---

## Custom Host Mapping

### Qué hace

Sobreescribe la resolución DNS para tráfico que pasa por el proxy. Cuando un request incluye un hostname configurado, el proxy lo resuelve a la IP configurada en vez de usar DNS real.

### Estructura de un mapping

| Campo | Descripción |
|-------|-------------|
| **Habilitado** | Si el mapping está activo |
| **Hostname** | El dominio a mapear (case-insensitive). Ej: `api.mi-app.local` |
| **IP Address** | La IP destino. Ej: `127.0.0.1`, `192.168.1.100`, `0.0.0.0` |
| **Descripción** | Texto opcional |

### Cómo funciona en el proxy

Los mappings se aplican en dos puntos:

1. **Requests normales**: Después de Rewrite Rules y Script Filter/Request, antes de enviar al upstream. Si el hostname coincide, el URI se reescribe con la IP configurada.
2. **Map Remote targets**: Antes de hacer el request reqwest al destino. Si el hostname del destino coincide, se usa la IP configurada.

### Orden de evaluación

Los mappings se evalúan en orden (primera coincidencia gana). El hostname se compara case-insensitive.

---

## Ejemplos prácticos

### Redirigir API a servidor local

| Hostname | IP | Descripción |
|----------|-----|-------------|
| `api.ejemplo.com` | `192.168.1.100` | Redirigir API a servidor de desarrollo local |

Todas las requests a `api.ejemplo.com` se resolverán a `192.168.1.100`.

### Bloquear dominios (ads, trackers)

| Hostname | IP | Descripción |
|----------|-----|-------------|
| `ads-tracker.net` | `0.0.0.0` | Bloquear ads |
| `analytics.spam.com` | `0.0.0.0` | Bloquear analytics |

`0.0.0.0` hace que la conexión falle inmediatamente, bloqueando efectivamente el dominio.

### Testing con IP específica

| Hostname | IP | Descripción |
|----------|-----|-------------|
| `prod-service.com` | `10.0.0.5` | Forzar IP de servicio en testing |

---

## Configuración en config.toml

```toml
[[dns_mappings]]
enabled = true
hostname = "api.ejemplo.com"
ip_address = "192.168.1.100"
description = "Redirigir API a servidor local"

[[dns_mappings]]
enabled = true
hostname = "ads-tracker.net"
ip_address = "0.0.0.0"
description = "Bloquear ads"
```

---

## Troubleshooting

### El mapping no se aplica

1. Verifica que el mapping está **habilitado**
2. El hostname es case-insensitive — no importa si es mayúscula o minúscula
3. El port se stripped del hostname antes de comparar
4. DNS mappings se aplican después de Rewrite Rules — si una Rewrite Rule cambia el hostname, el mapping puede no coincidir

### La resolución DNS falla

1. Verifica que el hostname es válido
2. Puede ser un problema de red/DNS del OS
3. Intenta resolver desde la terminal: `nslookup hostname`

### Stats/history desaparece

El historial de resolución se resetea cuando la app se reinicia (es de sesión, no persistido).
