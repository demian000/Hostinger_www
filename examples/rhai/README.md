# 🧪 Ejemplos de scripts Rhai

Esta carpeta contiene scripts **Rhai** de ejemplo para controlar el proxy ValDam mediante comandos (`ProxyCommand`).

## 📋 Requisitos

- ValDam Proxy con soporte Rhai habilitado
- Los comandos usados deben estar implementados en `process_commands`

## 📁 Scripts disponibles

| Script | Descripción | Comandos usados |
|--------|-------------|-----------------|
| [`simular-red-3g.rhai`](./simular-red-3g.rhai) | Simula una red 3G lenta (↓400Kbps / ↑100Kbps / 300ms / 2% pérdida) | `SetThrottle` ✅ |
| [`restaurar-throttle.rhai`](./restaurar-throttle.rhai) | Restaura el throttling a su estado por defecto (desactivado) | `SetThrottle` ✅ |
| [`throttle-con-escenario.rhai`](./throttle-con-escenario.rhai) | 7 perfiles de red: 4G, 3G, Edge, satelital, WiFi malo | `SetThrottle` ✅ |
| [`analizar-rendimiento.rhai`](./analizar-rendimiento.rhai) | Prueba guiada en 3 pasos (4G → 3G → Edge) para testear una app | `SetThrottle` ✅ |
| [`modo-depuracion.rhai`](./modo-depuracion.rhai) | Activa breakpoints + throttling para debugging | `SetBreakpointEnabled` ✅, `SetThrottle` ✅ |
| [`bloquear-trackers.rhai`](./bloquear-trackers.rhai) | Bloquea 20 dominios de trackers conocidos | `BlockDomain` ⏳ |

### Leyenda

| Símbolo | Significado |
|---------|-------------|
| ✅ | Comando implementado y funcional |
| ⏳ | Comando definido, pendiente de implementación |

## 🚀 Cómo usar

```bash
# Desde la UI del proxy, ejecutar:
proxy_command(RunScript("examples/rhai/simular-red-3g.rhai"));

# O directamente desde la consola Rhai (cuando este implementada):
proxy_command(SetThrottle(ThrottleConfig::new(true, 400, 100, 300, 2.0)));
```

## 📝 Notas

- Los scripts con `⏳` funcionarán cuando se complete la implementación del comando correspondiente en `proxy-core/src/proxy.rs`.
- Para contribuir nuevos ejemplos, crear un archivo `.rhai` en esta carpeta con:
  - Encabezado descriptivo (nombre y propósito)
  - Sección de uso
  - Comandos documentados
