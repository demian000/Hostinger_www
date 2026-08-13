#!/usr/bin/env python3
"""
simular_errores_http.py — Simulador de errores HTTP para pruebas
simular_errores_http.py — HTTP error simulator for testing

Modo: Request / Origin
Fase: Request — Simula diferentes códigos de error HTTP según la URL.

Mode: Request / Origin — Simulates different HTTP error codes based on URL.

Uso / Usage:
  - match_pattern: *://errors.example.com/*
  - phase: Request
  - mode: Origin

Endpoints:
  /error/400  → Bad Request
  /error/401  → Unauthorized
  /error/403  → Forbidden
  /error/404  → Not Found
  /error/500  → Internal Server Error
  /error/502  → Bad Gateway
  /error/503  → Service Unavailable
  /error/504  → Gateway Timeout
  /error/429  → Too Many Requests
  /random     → Error aleatorio / Random error
  /slow+error → Error después de latencia / Error after latency
"""
import json
import sys
import time
import random
import re


ERROR_TEMPLATES = {
    400: {"title": "Bad Request", "detail": "La solicitud contiene sintaxis incorrecta."},
    401: {"title": "Unauthorized", "detail": "Se requiere autenticación para acceder al recurso."},
    403: {"title": "Forbidden", "detail": "No tienes permisos para acceder a este recurso."},
    404: {"title": "Not Found", "detail": "El recurso solicitado no fue encontrado."},
    405: {"title": "Method Not Allowed", "detail": "El método HTTP no está permitido para este endpoint."},
    408: {"title": "Request Timeout", "detail": "La solicitud excedió el tiempo máximo de espera."},
    429: {"title": "Too Many Requests", "detail": "Has excedido el límite de peticiones. Intenta de nuevo en 60 segundos."},
    500: {"title": "Internal Server Error", "detail": "Ocurrió un error inesperado en el servidor."},
    502: {"title": "Bad Gateway", "detail": "El servidor upstream respondió con una respuesta inválida."},
    503: {"title": "Service Unavailable", "detail": "El servicio está temporalmente no disponible. Mantenimiento en curso."},
    504: {"title": "Gateway Timeout", "detail": "El servidor upstream no respondió a tiempo."},
}


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    method = data.get("method", "GET")
    path = extract_path(url)

    # Determinar código de error / Determine error code
    status_code = determine_error(path)
    template = ERROR_TEMPLATES.get(status_code, {
        "title": "Unknown Error",
        "detail": "Ocurrió un error no especificado.",
    })

    # Simular latencia para algunos errores / Simulate latency for some errors
    if status_code in (408, 504):
        delay = random.uniform(2, 5)
        print(f"[simular_errores_http] ⏳ Latencia de {delay:.1f}s antes de error {status_code}", file=sys.stderr)
        time.sleep(delay)

    # Construir respuesta de error / Build error response
    result = {
        "status": status_code,
        "headers": {
            "Content-Type": "application/json",
            "X-Error-Simulated": "true",
            "X-Error-Code": str(status_code),
        },
        "body": json.dumps({
            "error": True,
            "statusCode": status_code,
            "title": template["title"],
            "detail": template["detail"],
            "path": path,
            "method": method,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "suggestion": get_suggestion(status_code),
        }),
    }
    json.dump(result, sys.stdout)


def determine_error(path: str) -> int:
    """Determina qué error HTTP simular según el path."""
    m = re.search(r"/error/(\\d+)", path)
    if m:
        code = int(m.group(1))
        if code in ERROR_TEMPLATES:
            return code

    if "/random" in path:
        return random.choice(list(ERROR_TEMPLATES.keys()))

    if "/slow" in path:
        time.sleep(random.uniform(1, 3))
        return random.choice([408, 504, 500])

    # Por defecto: error 404
    return 404


def get_suggestion(code: int) -> str:
    suggestions = {
        400: "Revisa la sintaxis de tu solicitud y los datos enviados.",
        401: "Agrega un header Authorization válido a tu solicitud.",
        403: "Verifica que tu token tenga los permisos necesarios.",
        404: "Revisa la URL del endpoint. Puede que el recurso haya sido movido.",
        429: "Implementa un backoff exponencial y reintenta después de 60 segundos.",
        500: "Contacta al administrador del servidor. Revisa los logs del servidor.",
        502: "El upstream puede estar caído. Revisa la conectividad de red.",
        503: "Espera unos minutos y reintenta. El servidor puede estar en mantenimiento.",
        504: "El upstream tardó demasiado en responder. Revisa el timeout configurado.",
    }
    return suggestions.get(code, "Revisa la documentación de la API para más información.")


def extract_path(url: str) -> str:
    if "://" in url:
        after_protocol = url.split("://", 1)[1]
        slash_idx = after_protocol.find("/")
        if slash_idx >= 0:
            path_part = after_protocol[slash_idx:]
            q_idx = path_part.find("?")
            if q_idx >= 0:
                path_part = path_part[:q_idx]
            return path_part
    return url


if __name__ == "__main__":
    main()
