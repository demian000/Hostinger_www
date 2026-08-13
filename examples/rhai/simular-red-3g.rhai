// =============================================================================
// simular-red-3g.rhai
// =============================================================================
// Simula una red 3G lenta durante 30 segundos y luego restaura la
// configuración original.
//
// Uso:
//   proxy_command(RunScript("examples/rhai/simular-red-3g.rhai"));
// =============================================================================

const DURACION_SEGUNDOS = 30;
const INTERVALO_CHECK_MS  = 1000;

print("[Throttle] Iniciando simulacion 3G lenta...");

// ── 1. Guardar config actual (se lee desde la UI antes de ejecutar) ──
// Nota: cuando se implementen los comandos GetThrottleConfig / GetThrottleStats,
// podremos guardar/restaurar automaticamente.

// ── 2. Aplicar config 3G lenta ──
let cfg_3g = ThrottleConfig::new(true, 400, 100, 300, 2.0);
proxy_command(SetThrottle(cfg_3g));

print("[Throttle] 3G activado: ↓400Kbps ↑100Kbps latencia=300ms perdida=2%");

// ── 3. Esperar la duracion configurada ──
// Como Rhai no tiene sleep, el script termina y el proxy mantiene la config.
// Para restaurar, ejecutar el script "restaurar-throttle.rhai".
// En una implementacion futura con sleep, hariamos:
//
//   let inicio = timestamp();
//   while timestamp() - inicio < DURACION_SEGUNDOS {
//       sleep(INTERVALO_CHECK_MS);
//   }
//   proxy_command(SetThrottle(ThrottleConfig::disabled()));

print("[Throttle] Configuracion 3G aplicada. ");
print("[Throttle] Ejecuta 'restaurar-throttle.rhai' para volver a la normalidad.");
