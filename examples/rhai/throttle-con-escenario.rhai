// =============================================================================
// throttle-con-escenario.rhai
// =============================================================================
// Aplica diferentes perfiles de red para probar el comportamiento de una
// aplicacion en diversas condiciones.
//
// Uso interactivo:
//   Ejecuta el script del escenario deseado:
//
//   1. Red 4G (buena):
//      proxy_command(RunScript("examples/rhai/throttle-con-escenario.rhai"));
//      (por defecto carga 4G)
//
//   2. Red Edge (pesima):
//      Editar la variable ESCENARIO abajo.
//
// Nota: Cuando Rhai soporte argumentos de linea, esto se podra parametrizar.
// =============================================================================

// ── Escenarios disponibles ──
// Cambiar esta variable para seleccionar el perfil deseado.
const ESCENARIO = "4g";

// ── Perfiles de red ──
let perfiles = #{
    "ilimitado": ThrottleConfig::new(true, 0, 0, 0, 0.0),
    "4g":        ThrottleConfig::new(true, 10000, 5000, 50, 0.1),
    "3g-rapido": ThrottleConfig::new(true, 1600, 750, 150, 0.5),
    "3g-lento":  ThrottleConfig::new(true, 400, 100, 300, 2.0),
    "edge":      ThrottleConfig::new(true, 200, 50, 500, 5.0),
    "satelital": ThrottleConfig::new(true, 20000, 5000, 600, 0.5),
    "wifi-malo": ThrottleConfig::new(true, 5000, 2000, 200, 1.0),
};

// ── Aplicar perfil seleccionado ──
let config = perfiles[ESCENARIO];

if config == () {
    print("[Throttle] ⚠️ Escenario '" + ESCENARIO + "' no encontrado.");
    print("[Throttle] Usa uno de: " + perfiles.keys());
    return;
}

proxy_command(SetThrottle(config));

let label = switch ESCENARIO {
    "ilimitado"  => "Sin limite",
    "4g"         => "4G",
    "3g-rapido"  => "3G Rapido",
    "3g-lento"   => "3G Lento",
    "edge"       => "Edge (2G)",
    "satelital"  => "Satelital",
    "wifi-malo"  => "WiFi Malo",
    default      => ESCENARIO,
};

print("[Throttle] ========================================");
print("[Throttle] Perfil aplicado: " + label);
print("[Throttle] ========================================");
