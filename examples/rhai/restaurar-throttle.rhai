// =============================================================================
// restaurar-throttle.rhai
// =============================================================================
// Restaura la configuracion de throttling a su estado por defecto (desactivado).
//
// Uso:
//   proxy_command(RunScript("examples/rhai/restaurar-throttle.rhai"));
// =============================================================================

print("[Throttle] Restaurando configuracion por defecto...");

proxy_command(SetThrottle(ThrottleConfig::disabled()));

print("[Throttle] ✅ Throttling desactivado.");
print("[Throttle] Todo el trafico fluye sin restricciones.");
