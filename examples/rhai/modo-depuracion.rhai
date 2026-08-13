// =============================================================================
// modo-depuracion.rhai
// =============================================================================
// Activa el modo depuracion: breakpoints + throttling para simular red lenta.
// Util durante el desarrollo de aplicaciones moviles o web.
//
// Uso:
//   proxy_command(RunScript("examples/rhai/modo-depuracion.rhai"));
// =============================================================================

print("[Debug] ========================================");
print("[Debug] Activando modo depuracion...");
print("[Debug] ========================================");

// ── 1. Activar breakpoints ──
// Esto pausa cada peticion para inspeccion manual.
proxy_command(SetBreakpointEnabled(true));
print("[Debug] ✅ Breakpoints activados");

// ── 2. Configurar throttling suave ──
// Red 3G rapida para simular un escenario movil realista.
let cfg = ThrottleConfig::new(true, 1600, 750, 150, 0.5);
proxy_command(SetThrottle(cfg));
print("[Debug] ✅ Throttling configurado: ↓1.6Mbps ↑750Kbps latencia=150ms perdida=0.5%");

// ── 3. Bloquear trackers (opcional) ──
// Descomentar cuando BlockDomain este implementado:
// proxy_command(BlockDomain("doubleclick.net", true));
// proxy_command(BlockDomain("googleadservices.com", true));
// print("[Debug] ✅ Trackers bloqueados");

print("[Debug] ========================================");
print("[Debug] Modo depuracion activo.");
print("[Debug]");
print("[Debug] Para desactivar, ejecuta:");
print("[Debug]   proxy_command(SetBreakpointEnabled(false));");
print("[Debug]   proxy_command(SetThrottle(ThrottleConfig::disabled()));");
print("[Debug] ========================================");
