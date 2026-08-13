#!/usr/bin/env python3
"""
redirigir_api.py — Redirección de llamadas API
redirigir_api.py — API call redirector

Modo: Request / Filter
Fase: Request — Redirige requests a diferentes servidores o rutas.

Mode: Request / Filter — Redirects requests to different servers or paths.

Uso / Usage:
  - match_pattern: *://api.example.com/v1/*
  - phase: Request
  - mode: Filter

Útil para migraciones de API v1 → v2, o para redirigir tráfico de
producción a staging durante pruebas.

Useful for API migrations v1 → v2, or redirecting production traffic
to staging during testing.
"""
import json
import sys
import re


# ═══════════════════════════════════════════════════════════════════
# Reglas de redirección / Redirect rules
# ═══════════════════════════════════════════════════════════════════
REDIRECT_RULES = [
    # Migración v1 → v2
    {
        "pattern": r"https?://api\\.example\\.com/v1/users",
        "replacement": "https://api.example.com/v2/users",
    },
    {
        "pattern": r"https?://api\\.example\\.com/v1/products",
        "replacement": "https://api.example.com/v2/products",
    },
    # Redirigir a staging
    {
        "pattern": r"https?://api\\.production\\.com/",
        "replacement": "https://api.staging.com/",
    },
    # Cambiar puerto de desarrollo
    {
        "pattern": r":3000/",
        "replacement": ":3001/",
    },
]


def main():
    data = json.load(sys.stdin)

    if data.get("phase") != "request" or data.get("mode") != "filter":
        json.dump({
            "method": data.get("method", "GET"),
            "url": data.get("url", ""),
            "headers": data.get("headers", {}),
            "body": data.get("body"),
        }, sys.stdout)
        return

    url = data.get("url", "")
    original_url = url
    headers = data.get("headers", {})

    # Aplicar reglas de redirección / Apply redirect rules
    for rule in REDIRECT_RULES:
        new_url = re.sub(rule["pattern"], rule["replacement"], url)
        if new_url != url:
            print(f"[redirigir_api] 🔀 Redirigiendo: {url} → {new_url}", file=sys.stderr)
            url = new_url
            headers["X-Redirected-From"] = original_url
            headers["X-Redirect-Rule"] = rule["replacement"]
            break  # Solo aplicar primera regla / Apply only first rule

    result = {
        "method": data.get("method", "GET"),
        "url": url,
        "headers": headers,
        "body": data.get("body"),
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
