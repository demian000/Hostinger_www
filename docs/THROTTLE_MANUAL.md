# Manual: Throttle (Simulación de red)

El **Throttle** permite simular condiciones de red adversas controlando el ancho de banda, agregando latencia y simulando pérdida de paquetes. Equivalente a la función Throttle de Charles Proxy.

---

## Conceptos básicos

### Qué hace cada control

| Control | Qué hace | Rango |
|---------|----------|-------|
| **Ancho de banda de descarga** | Limita la velocidad de descarga (response → cliente). 0 = sin límite. | 0–100,000 Kbps |
| **Ancho de banda de subida** | Limita la velocidad de subida (request → servidor). 0 = sin límite. | 0–100,000 Kbps |
| **Latencia artificial** | Agrega un retardo a cada request y response. | 0–5,000 ms |
| **Pérdida de paquetes** | Porcentaje de requests que se descartan (se devuelve 503). | 0–100% |

### Cómo funciona el throttling

1. **Latencia**: El proxy espera (`sleep`) los milisegundos configurados antes de enviar cada request y antes de devolver cada response.
2. **Ancho de banda**: El proxy calcula un retardo basado en el tamaño del body y la velocidad configurada: `delay_ms = (body_bytes × 8000) / (kbps × 1024)`
3. **Pérdida de paquetes**: Para cada request, se genera un número aleatorio [0, 100). Si es menor al porcentaje configurado, el request se descarta y se devuelve `503 Service Unavailable`.

### Aplicación del throttling

El throttling se aplica en:
- Requests normales (latencia + upload bandwidth + packet loss)
- Responses normales (latencia + download bandwidth)
- Map Local responses (latencia + download bandwidth)
- Map Remote responses (latencia + download bandwidth)

Los cambios se aplican **instantáneamente** sin necesidad de reiniciar el proxy (hot-reload via Arc Mutex).

---

## Presets rápidos

| Preset | Descarga | Subida | Latencia | Pérdida |
|--------|----------|--------|----------|---------|
| **Sin límite** | 0 Kbps | 0 Kbps | 0 ms | 0% |
| **3G Lento** | 400 Kbps | 100 Kbps | 300 ms | 2.0% |
| **3G Rápido** | 1,600 Kbps | 750 Kbps | 150 ms | 0.5% |
| **4G** | 10,000 Kbps | 5,000 Kbps | 50 ms | 0.1% |
| **Edge (2G)** | 200 Kbps | 50 Kbps | 500 ms | 5.0% |

Los presets activan throttling automáticamente. Puedes modificar los valores después de seleccionar un preset.

---

## Panel en vivo

Cuando el proxy está activo y hay tráfico, el panel muestra estadísticas en tiempo real (actualiza cada 2 segundos):

| Estadística | Descripción |
|-------------|-------------|
| **Requests** | Total de requests procesadas |
| **Descargado** | Bytes descargados (responses) |
| **Subido** | Bytes subidos (requests) |
| **Paquetes perdidos** | Requests descartados por pérdida de paquetes |

El panel también muestra:
- Uptime del proxy (formato: `Xh Xm Xs`)
- Indicador animado de actividad
- Badges de configuración activa (↓descarga, ↑subida, ⏱latencia, ✕pérdida)
- Porcentaje de pérdida real vs configurada

---

## Cómo usar

### Ejemplo: Simular red 3G

1. En la página Throttle, haz clic en **"3G Lento"**
2. Throttling se activa automáticamente
3. Verifica los valores: ↓400 Kbps, ↑100 Kbps, 300ms, 2%
4. Haz clic en **Guardar**
5. Todas las requests que pasan por el proxy ahora experimentan condiciones 3G

### Ejemplo: Latencia personalizada

1. Activa el toggle "Throttling activo"
2. Configura: Descarga = 0 (sin límite), Subida = 0, Latencia = 200ms, Pérdida = 0%
3. Guardar
4. Cada request/response tendrá 200ms de retardo adicional

### Ejemplo: Bloquear requests aleatoriamente

1. Activa throttling
2. Configura: Pérdida de paquetes = 10%
3. Guardar
4. ~10% de las requests recibirán 503 Service Unavailable

---

## Configuración en config.toml

```toml
[throttle]
enabled = true
download_kbps = 1600
upload_kbps = 750
latency_ms = 150
packet_loss_percent = 0.5
```

---

## Troubleshooting

### El throttling no se aplica

1. Verifica que el toggle "Throttling activo" está habilitado
2. Haz clic en **Guardar** para persistir los cambios
3. El proxy debe estar corriendo para que throttling tenga efecto
4. Los cambios se aplican instantáneamente (no necesita reiniciar)

### Los valores no se guardan

1. Haz clic en **Guardar** explícitamente (los cambios en sliders no se auto-guardan)
2. Verifica que no hay errores en la UI (mensaje rojo)

### Stats no se muestran

El panel en vivo solo aparece cuando hay tráfico (`stats.totalRequests > 0`). Si no hay requests, el panel se oculta.
