#!/usr/bin/env python3
"""
modify_request.py — Modificación de requests salientes
modify_request.py — Outgoing request modification

Modo: Request / Filter
Fase: Request — Modifica el request antes de enviarlo al servidor upstream.

Mode: Request / Filter — Modifies the request before sending it upstream.

Uso / Usage:
  - match_pattern: *://api.example.com/*
  - phase: Request
  - mode: Filter

Funcionalidades / Features:
  - Agrega headers de depuración / Adds debugging headers
  - Agrega timestamp del script / Adds script timestamp
  - Agrega parámetro de tracking / Adds tracking query parameter
"""
import json
import sys
import time


def main():
    data = json.load(sys.stdin)

    # Verificar que es mode filter / Verify it's filter mode
    if data.get("phase") != "request" or data.get("mode") != "filter":
        # Passthrough: devolver sin cambios / Return unchanged
        json.dump({
            "method": data.get("method", "GET"),
            "url": data.get("url", ""),
            "headers": data.get("headers", {}),
            "body": data.get("body"),
        }, sys.stdout)
        return

    result = {
        "method": data.get("method", "GET"),
        "url": data.get("url", ""),
        "headers": data.get("headers", {}),
        "body": data.get("body"),
    }

    # Agregar headers de depuración / Add debug headers
    result["headers"]["X-Debug-Proxy"] = "modified-by-script"
    result["headers"]["X-Script-Timestamp"] = str(int(time.time()))
    result["headers"]["X-Script-Name"] = "modify_request.py"

    # Agregar parámetro de tracking en URL / Add tracking param to URL
    url = result["url"]
    if "?" in url:
        result["url"] = url + "&_script_processed=true"
    else:
        result["url"] = url + "?_script_processed=true"

    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
