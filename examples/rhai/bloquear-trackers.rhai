// =============================================================================
// bloquear-trackers.rhai
// =============================================================================
// Bloquea dominios de trackers y anuncios conocidos.
//
// Uso:
//   proxy_command(RunScript("examples/rhai/bloquear-trackers.rhai"));
//
// Nota: El comando BlockDomain esta definido pero pendiente de implementacion
// en el handler de comandos. Estos ejemplos son conceptuales y funcionaran
// cuando se complete la implementacion.
// =============================================================================

print("[Block] Bloqueando trackers conocidos...");

// ── Lista de dominios a bloquear ──
let dominios = [
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "googletagmanager.com",
    "facebook.com/tr",
    "analytics.twitter.com",
    "ads.linkedin.com",
    "scorecardresearch.com",
    "quantserve.com",
    "outbrain.com",
    "taboola.com",
    "criteo.com",
    "criteo.net",
    "casalemedia.com",
    "adsrvr.org",
    "adsymptotic.com",
    "rubiconproject.com",
    "pubmatic.com",
    "openx.net",
    "appnexus.com",
];

// ── Bloquear cada dominio ──
for dominio in dominios {
    print("[Block] Bloqueando: " + dominio);
    proxy_command(BlockDomain(dominio, true));
}

print("[Block] " + dominios.len() + " trackers bloqueados.");
print("[Block] Ejecuta 'desbloquear-trackers.rhai' para restaurar.");
