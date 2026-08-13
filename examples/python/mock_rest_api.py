#!/usr/bin/env python3
"""
mock_rest_api.py — Mock completo de API REST con operaciones CRUD
mock_rest_api.py — Full REST API mock with CRUD operations

Modo: Request / Origin
Fase: Request — Simula una API REST completa con base de datos en memoria.

Mode: Request / Origin — Simulates a full REST API with an in-memory database.

Uso / Usage:
  - match_pattern: *://rest-mock.example.com/api/*
  - phase: Request
  - mode: Origin

Soporta operaciones CRUD para múltiples recursos:
- GET /api/users — Listar usuarios
- GET /api/users/:id — Obtener usuario por ID
- POST /api/users — Crear usuario
- PUT /api/users/:id — Actualizar usuario
- DELETE /api/users/:id — Eliminar usuario
- GET /api/products — Listar productos
- POST /api/products — Crear producto
"""
import json
import sys
import re
from datetime import datetime, timezone


# ── Base de datos en memoria / In-memory database ──
USERS = [
    {"id": 1, "name": "Ana Torres", "email": "ana@ejemplo.com", "role": "admin", "active": True},
    {"id": 2, "name": "Luis Pérez", "email": "luis@ejemplo.com", "role": "user", "active": True},
    {"id": 3, "name": "María Díaz", "email": "maria@ejemplo.com", "role": "user", "active": False},
]

PRODUCTS = [
    {"id": 1, "name": "Laptop Pro", "price": 1299.99, "category": "electronics", "stock": 50},
    {"id": 2, "name": "Mouse Inalámbrico", "price": 29.99, "category": "electronics", "stock": 200},
    {"id": 3, "name": "Teclado Mecánico", "price": 89.99, "category": "electronics", "stock": 100},
]

ORDERS = []

NEXT_IDS = {"users": 4, "products": 4, "orders": 1}


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    method = data.get("method", "GET")
    path = extract_path(url)

    # Parsear body si existe / Parse body if present
    body = None
    body_str = data.get("body")
    if body_str:
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            body = {}

    result = route_request(path, method, body)
    json.dump(result, sys.stdout)


def route_request(path: str, method: str, body: dict) -> dict:
    """Enruta la petición al manejador correspondiente."""
    headers = {
        "Content-Type": "application/json",
        "X-Mock-REST": "true",
    }

    # ── Users ──
    m = re.search(r"/api/users/(\\d+)", path)
    if m:
        user_id = int(m.group(1))
        if method == "GET":
            return handle_get_user(user_id, headers)
        elif method == "PUT":
            return handle_update_user(user_id, body, headers)
        elif method == "DELETE":
            return handle_delete_user(user_id, headers)
        else:
            return error_response(405, "Método no permitido", headers)

    if re.search(r"/api/users/?$", path):
        if method == "GET":
            return handle_list_users(headers)
        elif method == "POST":
            return handle_create_user(body, headers)
        else:
            return error_response(405, "Método no permitido", headers)

    # ── Products ──
    m = re.search(r"/api/products/(\\d+)", path)
    if m:
        product_id = int(m.group(1))
        if method == "GET":
            return handle_get_product(product_id, headers)
        elif method == "PUT":
            return handle_update_product(product_id, body, headers)
        else:
            return error_response(405, "Método no permitido", headers)

    if re.search(r"/api/products/?$", path):
        if method == "GET":
            return handle_list_products(headers)
        elif method == "POST":
            return handle_create_product(body, headers)
        else:
            return error_response(405, "Método no permitido", headers)

    # ── Health ──
    if re.search(r"/api/health", path):
        return {
            "status": 200,
            "headers": headers,
            "body": json.dumps({
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resources": {
                    "users": len(USERS),
                    "products": len(PRODUCTS),
                    "orders": len(ORDERS),
                },
            }),
        }

    return error_response(404, "Endpoint no encontrado", headers)


# ── Handlers de Users ──

def handle_list_users(headers: dict) -> dict:
    """GET /api/users — Lista todos los usuarios."""
    return {
        "status": 200,
        "headers": headers,
        "body": json.dumps({
            "users": USERS,
            "total": len(USERS),
        }),
    }


def handle_get_user(user_id: int, headers: dict) -> dict:
    """GET /api/users/:id — Obtiene un usuario por ID."""
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"Usuario {user_id} no encontrado", headers)
    return {"status": 200, "headers": headers, "body": json.dumps(user)}


def handle_create_user(body: dict, headers: dict) -> dict:
    """POST /api/users — Crea un nuevo usuario."""
    global NEXT_IDS
    required = ["name", "email"]
    missing = [f for f in required if not body or f not in body]
    if missing:
        return error_response(400, f"Campos requeridos faltantes: {missing}", headers)

    new_user = {
        "id": NEXT_IDS["users"],
        "name": body["name"],
        "email": body["email"],
        "role": body.get("role", "user"),
        "active": body.get("active", True),
    }
    USERS.append(new_user)
    NEXT_IDS["users"] += 1
    return {"status": 201, "headers": headers, "body": json.dumps(new_user)}


def handle_update_user(user_id: int, body: dict, headers: dict) -> dict:
    """PUT /api/users/:id — Actualiza un usuario."""
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"Usuario {user_id} no encontrado", headers)
    if body:
        for key in ("name", "email", "role", "active"):
            if key in body:
                user[key] = body[key]
    return {"status": 200, "headers": headers, "body": json.dumps(user)}


def handle_delete_user(user_id: int, headers: dict) -> dict:
    """DELETE /api/users/:id — Elimina un usuario."""
    global USERS
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return error_response(404, f"Usuario {user_id} no encontrado", headers)
    USERS = [u for u in USERS if u["id"] != user_id]
    return {"status": 200, "headers": headers, "body": json.dumps({"deleted": True, "id": user_id})}


# ── Handlers de Products ──

def handle_list_products(headers: dict) -> dict:
    products_with_tax = []
    for p in PRODUCTS:
        p_copy = dict(p)
        p_copy["price_with_tax"] = round(p["price"] * 1.16, 2)
        products_with_tax.append(p_copy)
    return {
        "status": 200,
        "headers": headers,
        "body": json.dumps({"products": products_with_tax, "total": len(PRODUCTS)}),
    }


def handle_get_product(product_id: int, headers: dict) -> dict:
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return error_response(404, f"Producto {product_id} no encontrado", headers)
    p = dict(product)
    p["price_with_tax"] = round(p["price"] * 1.16, 2)
    return {"status": 200, "headers": headers, "body": json.dumps(p)}


def handle_create_product(body: dict, headers: dict) -> dict:
    global NEXT_IDS
    if not body or "name" not in body:
        return error_response(400, "El campo 'name' es requerido", headers)
    new_product = {
        "id": NEXT_IDS["products"],
        "name": body["name"],
        "price": body.get("price", 0.0),
        "category": body.get("category", "general"),
        "stock": body.get("stock", 0),
    }
    PRODUCTS.append(new_product)
    NEXT_IDS["products"] += 1
    return {"status": 201, "headers": headers, "body": json.dumps(new_product)}


def handle_update_product(product_id: int, body: dict, headers: dict) -> dict:
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return error_response(404, f"Producto {product_id} no encontrado", headers)
    if body:
        for key in ("name", "price", "category", "stock"):
            if key in body:
                product[key] = body[key]
    return {"status": 200, "headers": headers, "body": json.dumps(product)}


# ── Utilidades / Utilities ──

def error_response(status: int, message: str, headers: dict) -> dict:
    return {
        "status": status,
        "headers": headers,
        "body": json.dumps({"error": True, "message": message}),
    }


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
