#!/usr/bin/env python3
"""
inyectar_sesion.py — Inyector de cookies y sesión
inyectar_sesion.py — Cookie and session injector

Modo: Request / Filter
Fase: Request — Inyecta cookies y headers de sesión en requests salientes.

Mode: Request / Filter — Injects cookies and session headers into outgoing requests.

Uso / Usage:
  - match_pattern: *://app.example.com/*
  - phase: Request
  - mode: Filter

Útil para desarrollo cuando necesitas mantener una sesión activa sin
tener que iniciar sesión manualmente.

Useful for development when you need to keep an active session without
manual login.
"""
import json
import sys
from datetime import datetime, timezone


# ═══════════════════════════════════════════════════════════════════
# Configuración de sesión / Session configuration
# ═══════════════════════════════════════════════════════════════════
SESSION_CONFIG = {
    "session_id": f"dev-session-{int(__import__('time').time())}",
    "user_id": "dev-user-42",
    "role": "admin",
    "csrf_token": "dev-csrf-token-abc123",
}


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

    headers = data.get("headers", {})

    # Inyectar cookie de sesión / Inject session cookie
    cookie_parts = [
        f"session_id={SESSION_CONFIG['session_id']}",
        f"user_id={SESSION_CONFIG['user_id']}",
        f"role={SESSION_CONFIG['role']}",
    ]
    headers["Cookie"] = "; ".join(cookie_parts)

    # Inyectar headers de sesión adicionales / Inject extra session headers
    headers["X-User-ID"] = SESSION_CONFIG["user_id"]
    headers["X-User-Role"] = SESSION_CONFIG["role"]
    headers["X-CSRF-Token"] = SESSION_CONFIG["csrf_token"]
    headers["X-Session-Created"] = datetime.now(timezone.utc).isoformat()

    print(f"[inyectar_sesion] 🔐 Sesión inyectada: usuario={SESSION_CONFIG['user_id']} rol={SESSION_CONFIG['role']}", file=sys.stderr)

    result = {
        "method": data.get("method", "GET"),
        "url": data.get("url", ""),
        "headers": headers,
        "body": data.get("body"),
    }
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
