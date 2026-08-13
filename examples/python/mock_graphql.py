#!/usr/bin/env python3
"""
mock_graphql.py — Simulador de respuestas GraphQL
mock_graphql.py — GraphQL response simulator

Modo: Request / Origin
Fase: Request — Analiza consultas GraphQL y genera respuestas mock.

Mode: Request / Origin — Parses GraphQL queries and generates mock responses.

Uso / Usage:
  - match_pattern: *://graphql-mock.example.com/graphql
  - phase: Request
  - mode: Origin

Soporta consultas comunes como:
  - query { users { ... } }
  - query { user(id: 1) { ... } }
  - mutation { createUser(...) { ... } }
  - query { products { ... } }
"""
import json
import sys
import re


# ── Base de datos mock / Mock database ──
MOCK_USERS = [
    {"id": "1", "name": "Sofía Ramos", "email": "sofia@ejemplo.com", "postsCount": 12},
    {"id": "2", "name": "Diego Castillo", "email": "diego@ejemplo.com", "postsCount": 5},
    {"id": "3", "name": "Valentina Ortiz", "email": "valentina@ejemplo.com", "postsCount": 23},
]

MOCK_POSTS = [
    {"id": "101", "title": "Introducción a Python", "body": "Python es un lenguaje...", "authorId": "1"},
    {"id": "102", "title": "APIs REST con FastAPI", "body": "FastAPI permite crear...", "authorId": "1"},
    {"id": "103", "title": "GraphQL vs REST", "body": "Comparativa entre...", "authorId": "2"},
]


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    body_str = data.get("body", "")

    # Parsear la consulta GraphQL / Parse GraphQL query
    query_data = {}
    if body_str:
        try:
            query_data = json.loads(body_str)
        except json.JSONDecodeError:
            pass

    query = query_data.get("query", "")
    variables = query_data.get("variables", {})

    # Generar respuesta / Generate response
    response_data = resolve_graphql(query, variables)

    result = {
        "status": 200,
        "headers": {
            "Content-Type": "application/json",
            "X-Mock-GraphQL": "true",
        },
        "body": json.dumps(response_data),
    }
    json.dump(result, sys.stdout)


def resolve_graphql(query: str, variables: dict) -> dict:
    """Resuelve una consulta GraphQL y devuelve datos mock."""
    result = {"data": {}}

    # Detectar operaciones comunes
    if "query" in query:
        if "users" in query:
            if "user(id:" in query or "user(id:" in query:
                # Buscar usuario específico / Find specific user
                id_match = re.search(r'user\\(\\s*id:\\s*\"?(\\d+)\"?\\s*\\)', query)
                if id_match:
                    user_id = id_match.group(1)
                    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
                    result["data"]["user"] = user
                else:
                    result["data"]["users"] = MOCK_USERS
            else:
                result["data"]["users"] = MOCK_USERS

        if "posts" in query:
            if "post(id:" in query:
                id_match = re.search(r'post\\(\\s*id:\\s*\"?(\\d+)\"?\\s*\\)', query)
                if id_match:
                    post_id = id_match.group(1)
                    post = next((p for p in MOCK_POSTS if p["id"] == post_id), None)
                    result["data"]["post"] = post
                else:
                    result["data"]["posts"] = MOCK_POSTS
            else:
                result["data"]["posts"] = MOCK_POSTS

    elif "mutation" in query:
        if "createUser" in query:
            result["data"]["createUser"] = {
                "id": "4",
                "name": variables.get("name", "Nuevo Usuario"),
                "email": variables.get("email", "nuevo@ejemplo.com"),
                "postsCount": 0,
            }
        elif "deleteUser" in query:
            result["data"]["deleteUser"] = {
                "success": True,
                "message": "Usuario eliminado correctamente",
            }

    # Si no se pudo resolver, devolver error / If can't resolve, return error
    if not result["data"]:
        result["errors"] = [{
            "message": f"Consulta no soportada: {query[:100]}...",
            "locations": [{"line": 1, "column": 1}],
        }]

    return result


if __name__ == "__main__":
    main()
