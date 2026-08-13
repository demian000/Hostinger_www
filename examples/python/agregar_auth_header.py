#!/usr/bin/env python3
"""
agregar_auth_header.py — Inyector de headers de autenticación
agregar_auth_header.py — Authentication header injector

Modo: Request / Filter
Fase: Request — Agrega headers de autenticación a requests salientes.

Mode: Request / Filter — Adds authentication headers to outgoing requests.

Uso / Usage:
  - match_pattern: *://api.example.com/private/*
  - phase: Request
  - mode: Filter

Útil para desarrollo cuando no quieres configurar auth en tu app cliente.
Soporta múltiples esquemas de autenticación: Bearer, Basic, API Key.

Useful for development when you don't want to set up auth in your client app.
Supports multiple auth schemes: Bearer, Basic, API Key.
"""
import json
import sys
import base64


# ═══════════════════════════════════════════════════════════════════
# Configuración de autenticación / Auth configuration
# ═══════════════════════════════════════════════════════════════════
AUTH_CONFIG = {
    "default": {
        "type": "bearer",
        "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkZXZfdXNlciJ9.mocked-token",
    },
    "api.ejemplo.com": {
        "type": "api_key",
        "header": "X-API-Key",
        "value": "dev-api-key-12345",
    },
    "admin.ejemplo.com": {
        "type": "basic",
        "username": "admin",
        "password": "dev-password-2024",
    },
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

    url = data.get("url", "")
    headers = data.get("headers", {})

    # Determinar qué auth aplicar según el host / Determine auth scheme by host
    auth = select_auth(url)
    if auth:
        if auth["type"] == "bearer":
            headers["Authorization"] = f"Bearer {auth['token']}"
        elif auth["type"] == "api_key":
            headers[auth["header"]] = auth["value"]
        elif auth["type"] == "basic":
            credentials = f"{auth['username']}:{auth['password']}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"

        print(f"[agregar_auth_header] 🔑 Auth aplicado: {auth['type']} para {url}", file=sys.stderr)

    result = {
        "method": data.get("method", "GET"),
        "url": url,
        "headers": headers,
        "body": data.get("body"),
    }
    json.dump(result, sys.stdout)


def select_auth(url: str) -> dict | None:
    """Selecciona la configuración de auth según el host en la URL."""
    for host_pattern, config in AUTH_CONFIG.items():
        if host_pattern in url:
            return config
    return AUTH_CONFIG.get("default")


if __name__ == "__main__":
    main()
