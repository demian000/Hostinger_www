// =============================================================================
// analizar-rendimiento.rhai
// =============================================================================
// Prueba el comportamiento de la aplicacion en 3 perfiles de red diferentes.
// Ideal para hacer pruebas de rendimiento manuales.
//
// Funcionamiento:
//   1. Aplica perfil → muestra resumen
//   2. El usuario navega y observa el comportamiento
//   3. Ejecuta el paso siguiente cuando este listo
//
// Uso paso a paso:
//
//   Paso 1 - 4G (linea base):
//     proxy_command(RunScript("examples/rhai/analizar-rendimiento.rhai"));
//     (por defecto carga perfil 4G)
//
//   Paso 2 - 3G Lento:
//     Editar PASO = 2 y re-ejecutar
//
//   Paso 3 - Edge:
//     Editar PASO = 3 y re-ejecutar
// =============================================================================

const PASO = 1;

if PASO == 1 {
    // Linea base: 4G
    proxy_command(SetThrottle(ThrottleConfig::new(true, 10000, 5000, 50, 0.1)));
    print("[Analisis] ========================================");
    print("[Analisis] 📱 PASO 1/3: Linea base - 4G");
    print("[Analisis] ↓10Mbps ↑5Mbps latencia=50ms perdida=0.1%");
    print("[Analisis]");
    print("[Analisis] Navega por la app y verifica:");
    print("[Analisis]   ✔ Tiempos de carga aceptables");
    print("[Analisis]   ✔ Imagenes y recursos cargan correctamente");
    print("[Analisis]   ✔ Animaciones fluidas");
    print("[Analisis]");
    print("[Analisis] Cuando termines, cambia PASO = 2 y re-ejecuta.");
    print("[Analisis] ========================================");
}

if PASO == 2 {
    // Red movil tipica: 3G lento
    proxy_command(SetThrottle(ThrottleConfig::new(true, 400, 100, 300, 2.0)));
    print("[Analisis] ========================================");
    print("[Analisis] 📱 PASO 2/3: Red movil tipica - 3G Lento");
    print("[Analisis] ↓400Kbps ↑100Kbps latencia=300ms perdida=2%");
    print("[Analisis]");
    print("[Analisis] Verifica:");
    print("[Analisis]   ✔ Indicador de carga visible");
    print("[Analisis]   ✔ Timeouts manejados correctamente");
    print("[Analisis]   ✔ 2% de requests fallan con 503 (esperado)");
    print("[Analisis]   ✔ La app se recupera de errores de red");
    print("[Analisis]");
    print("[Analisis] Cuando termines, cambia PASO = 3 y re-ejecuta.");
    print("[Analisis] ========================================");
}

if PASO == 3 {
    // Red pesima: Edge
    proxy_command(SetThrottle(ThrottleConfig::new(true, 200, 50, 500, 5.0)));
    print("[Analisis] ========================================");
    print("[Analisis] 📱 PASO 3/3: Red pesima - Edge (2G)");
    print("[Analisis] ↓200Kbps ↑50Kbps latencia=500ms perdida=5%");
    print("[Analisis]");
    print("[Analisis] Verifica:");
    print("[Analisis]   ✔ Mensajes de 'sin conexion' apropiados");
    print("[Analisis]   ✔ Reintentos automaticos funcionan");
    print("[Analisis]   ✔ No hay crashes ante 5% de perdida");
    print("[Analisis]   ✔ UX aceptable en condiciones adversas");
    print("[Analisis]");
    print("[Analisis] Al finalizar, ejecuta restaurar-throttle.rhai");
    print("[Analisis] ========================================");
}
