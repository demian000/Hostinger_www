#!/usr/bin/env python3
"""
modificar_json_response.py — Modificación dinámica de respuestas JSON
modificar_json_response.py — Dynamic JSON response modification

Modo: Response / Filter
Fase: Response — Modifica campos específicos en respuestas JSON.

Mode: Response / Filter — Modifies specific fields in JSON responses.

Uso / Usage:
  - match_pattern: *://api.example.com/*
  - phase: Response
  - mode: Filter

Útil para modificar datos de prueba, cambiar valores, o inyectar
información adicional en respuestas JSON.

Useful for modifying test data, changing values, or injecting
additional info into JSON responses.
"""
import json
import sys
import re


# ═══════════════════════════════════════════════════════════════════
# Reglas de modificación / Modification rules
# ═══════════════════════════════════════════════════════════════════
# Cada regla: (path_regex, field, new_value_function)
MODIFICATION_RULES = [
    # Limitar resultados de listas a 2 items / Limit list results to 2 items
    (r"/api/users", lambda data: truncate_list(data, "users", 2)),
    (r"/api/products", lambda data: truncate_list(data, "products", 1)),
    # Forzar campos específicos / Force specific fields
    (r"/api/users/\d+", lambda data: force_field(data, "role", "premium")),
    (r"/api/status", lambda data: force_field(data, "status", "degraded")),
    # Agregar campos adicionales / Add extra fields
    (r"/api/.+", lambda data: add_field(data, "_debug", True)),
    (r"/api/.+", lambda data: add_field(data, "_proxyTimestamp", sys.intern(""))),
]


def main():
    data = json.load(sys.stdin)

    if data.get("phase") != "response" or data.get("mode") != "filter":
        json.dump({
            "status": data.get("status", 200),
            "headers": data.get("headers", {}),
            "body": data.get("body", ""),
        }, sys.stdout)
        return

    url = data.get("url", "")
    body_str = data.get("body", "")
    status = data.get("status", 200)
    headers = data.get("headers", {})

    if not body_str:
        json.dump({"status": status, "headers": headers, "body": body_str}, sys.stdout)
        return

    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        json.dump({"status": status, "headers": headers, "body": body_str}, sys.stdout)
        return

    # Aplicar reglas de modificación / Apply modification rules
    modified = False
    for pattern, modifier in MODIFICATION_RULES:
        if re.search(pattern, url):
            try:
                result = modifier(body)
                if result:
                    modified = True
            except Exception as e:
                print(f"[modificar_json_response] ⚠️ Error en regla '{pattern}': {e}", file=sys.stderr)

    headers["X-JSON-Modified"] = "true" if modified else "false"

    result = {
        "status": status,
        "headers": headers,
        "body": json.dumps(body),
    }
    json.dump(result, sys.stdout)


# ── Funciones auxiliares de modificación / Helper modification functions ──

def truncate_list(data: dict, field: str, max_items: int) -> bool:
    """Trunca una lista a N items."""
    if field in data and isinstance(data[field], list) and len(data[field]) > max_items:
        data[field] = data[field][:max_items]
        data["_truncated"] = True
        data["_originalCount"] = len(data[field]) + 1 if len(data) > 0 else 0
        return True
    return False


def force_field(data: dict, field: str, value) -> bool:
    """Fuerza un campo a un valor específico."""
    if field in data:
        data[field] = value
        return True
    return False


def add_field(data: dict, field: str, value) -> bool:
    """Agrega un campo si no existe."""
    if field not in data:
        data[field] = value
        return True
    return False


if __name__ == "__main__":
    main()
