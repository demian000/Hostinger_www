#!/usr/bin/env python3
"""
agregar_params_tracking.py — Inyector de parámetros de tracking/analytics
agregar_params_tracking.py — Tracking/analytics parameters injector

Modo: Request / Filter
Fase: Request — Agrega parámetros de tracking a las URLs de salida.

Mode: Request / Filter — Adds tracking parameters to outgoing URLs.

Uso / Usage:
  - match_pattern: *://analytics.example.com/*
  - phase: Request
  - mode: Filter

Útil para agregar parámetros de campaña, IDs de sesión, o datos de
depuración a todas las requests que pasan por el proxy.

Useful for adding campaign parameters, session IDs, or debug data
to all requests passing through the proxy.
"""
import json
import sys
import time
import random
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse


# ═══════════════════════════════════════════════════════════════════
# Configuración / Configuration
# ═══════════════════════════════════════════════════════════════════
SESSION_ID = f"session-{int(time.time())}"
CAMPAIGN = "proxy-debug"


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
    headers = data.get("headers", {})

    # Agregar parámetros de tracking / Add tracking params
    tracking_params = {
        "_session": SESSION_ID,
        "_campaign": CAMPAIGN,
        "_ts": str(int(time.time())),
        "_rid": str(random.randint(100000, 999999)),
    }

    # Preservar parámetros existentes / Preserve existing params
    parsed = urlparse(url)
    existing_params = parse_qs(parsed.query, keep_blank_values=True)
    existing_flat = {k: v[0] if len(v) == 1 else v for k, v in existing_params.items()}
    existing_flat.update(tracking_params)

    new_query = urlencode(existing_flat, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))

    # También agregar header de tracking / Also add tracking header
    headers["X-Tracking-Session"] = SESSION_ID
    headers["X-Tracking-Campaign"] = CAMPAIGN

    print(f"[agregar_params_tracking] 📊 Tracking agregado a {url}", file=sys.stderr)

    result = {
        "method": data.get("method", "GET"),
        "url": new_url,
        "headers": headers,
        "body": data.get("body"),
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
