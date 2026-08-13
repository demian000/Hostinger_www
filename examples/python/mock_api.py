#!/usr/bin/env python3
"""
mock_api.py — Generador de respuestas mock para APIs REST
mock_api.py — Mock response generator for REST APIs

Modo: Request / Origin
Fase: Request — El script genera la response completa, el request NO va al upstream.
Mode: Request / Origin — The script generates the full response, request does NOT reach upstream.

Uso / Usage:
  - match_pattern: *://api.example.com/*
  - phase: Request
  - mode: Origin

Este script analiza la URL y el método HTTP, y devuelve respuestas simuladas
para endpoints comunes como /users, /products, /orders, etc.

This script inspects the URL and HTTP method, returning mock responses
for common endpoints like /users, /products, /orders, etc.
"""
import json
import sys
import re


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    method = data.get("method", "GET")
    path = extract_path(url)
    status = 200
    headers = {
        "Content-Type": "application/json",
        "X-Mock-Generated": "true",
        "X-Mock-URL": url,
    }

    # ── Enrutamiento de respuestas mock / Mock response routing ──
    body = None

    if re.search(r"/users/?$", path) and method == "GET":
        body = json.dumps({
            "users": [
                {"id": 1, "name": "Alice García", "email": "alice@ejemplo.com", "role": "admin"},
                {"id": 2, "name": "Bob Martínez", "email": "bob@ejemplo.com", "role": "user"},
                {"id": 3, "name": "Carla López", "email": "carla@ejemplo.com", "role": "user"},
            ],
            "total": 3,
            "page": 1,
        })

    elif re.search(r"/users/?\d+", path) and method == "GET":
        user_id = re.search(r"/users/?(\\d+)", path).group(1)
        body = json.dumps({
            "id": int(user_id),
            "name": f"Usuario {user_id}",
            "email": f"user{user_id}@ejemplo.com",
            "role": "user",
            "createdAt": "2024-01-15T10:30:00Z",
        })

    elif re.search(r"/users/?$", path) and method == "POST":
        body = json.dumps({
            "id": 4,
            "name": "Nuevo Usuario",
            "email": "nuevo@ejemplo.com",
            "role": "user",
            "created": True,
        })
        status = 201

    elif re.search(r"/products/?$", path) and method == "GET":
        body = json.dumps({
            "products": [
                {"id": 1, "name": "Widget Pro", "price": 29.99, "stock": 150},
                {"id": 2, "name": "Gadget X", "price": 49.99, "stock": 75},
                {"id": 3, "name": "SuperTool", "price": 99.99, "stock": 200},
            ],
            "total": 3,
        })

    elif re.search(r"/orders/?$", path) and method == "POST":
        body = json.dumps({
            "orderId": "ORD-2024-001",
            "status": "confirmed",
            "total": 129.97,
            "estimatedDelivery": "2024-02-01",
        })
        status = 201

    elif re.search(r"/health|/status", path):
        body = json.dumps({
            "status": "healthy",
            "version": "2.0.0-mock",
            "uptime": "72h",
            "database": "connected",
        })

    else:
        # Endpoint desconocido / unknown endpoint
        body = json.dumps({
            "message": "Mock API - Endpoint no implementado / Endpoint not implemented",
            "url": url,
            "method": method,
            "hint": "Endpoints disponibles: /users, /products, /orders, /health",
        })

    result = {
        "status": status,
        "headers": headers,
        "body": body,
    }
    json.dump(result, sys.stdout)


def extract_path(url: str) -> str:
    """Extrae el path de una URL."""
    if "://" in url:
        # Encontrar el path después del host
        after_protocol = url.split("://", 1)[1]
        # Encontrar el primer /
        slash_idx = after_protocol.find("/")
        if slash_idx >= 0:
            path_part = after_protocol[slash_idx:]
            # Quitar query string
            q_idx = path_part.find("?")
            if q_idx >= 0:
                path_part = path_part[:q_idx]
            return path_part
    return url


if __name__ == "__main__":
    main()
