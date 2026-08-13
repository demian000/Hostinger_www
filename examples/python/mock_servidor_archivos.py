#!/usr/bin/env python3
"""
mock_servidor_archivos.py — Servidor de archivos mock desde el sistema local
mock_servidor_archivos.py — Mock file server from local filesystem

Modo: Request / Origin
Fase: Request — Lee archivos locales y los sirve como respuesta HTTP.

Mode: Request / Origin — Reads local files and serves them as HTTP responses.

Uso / Usage:
  - match_pattern: *://files-mock.example.com/*
  - phase: Request
  - mode: Origin

Configuración: Define el directorio raíz y archivos por defecto.
Configuration: Define root directory and default files.

NOTA: Por seguridad, solo permite leer archivos dentro del directorio
configurado. No accede a rutas fuera de este directorio.

NOTE: For security, only allows reading files within the configured
directory. Does not access paths outside this directory.
"""
import json
import sys
import os
import mimetypes
import re


# ═══════════════════════════════════════════════════════════════════
# Configuración / Configuration
# ═══════════════════════════════════════════════════════════════════
# Directorio raíz para servir archivos / Root directory to serve files
# Cambia esto a tu ruta local / Change this to your local path
ROOT_DIR = "/tmp/mock-files"

# Archivos por defecto / Default files
INDEX_FILE = "index.html"
NOT_FOUND_FILE = "404.html"


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    method = data.get("method", "GET")
    path = extract_path(url)

    # Construir ruta al archivo / Build file path
    if path == "/" or not path:
        file_path = os.path.join(ROOT_DIR, INDEX_FILE)
    else:
        # Limpiar path, quitar leading slash
        clean_path = path.lstrip("/")
        file_path = os.path.join(ROOT_DIR, clean_path)

    # ⚠️ Seguridad: evitar path traversal / Security: prevent path traversal
    real_path = os.path.realpath(file_path)
    real_root = os.path.realpath(ROOT_DIR)
    if not real_path.startswith(real_root):
        result = {
            "status": 403,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Acceso denegado: path fuera del directorio permitido"}),
        }
        json.dump(result, sys.stdout)
        return

    # Leer archivo / Read file
    if os.path.isfile(real_path):
        try:
            with open(real_path, "rb") as f:
                content = f.read()

            content_type, _ = mimetypes.guess_type(real_path)
            if content_type is None:
                content_type = "application/octet-stream"

            # Si es texto, decodificar para JSON / If text, decode for JSON
            try:
                body_str = content.decode("utf-8")
            except UnicodeDecodeError:
                body_str = content.decode("latin-1")

            result = {
                "status": 200,
                "headers": {
                    "Content-Type": content_type,
                    "X-Mock-File": os.path.basename(real_path),
                    "Content-Length": str(len(content)),
                },
                "body": body_str,
            }
        except Exception as e:
            result = {
                "status": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Error leyendo archivo: {str(e)}"}),
            }
    else:
        # Archivo no encontrado / File not found
        not_found_path = os.path.join(ROOT_DIR, NOT_FOUND_FILE)
        if os.path.isfile(not_found_path):
            with open(not_found_path, "r") as f:
                not_found_body = f.read()
        else:
            not_found_body = json.dumps({
                "error": "Archivo no encontrado",
                "path": path,
                "hint": f"Verifica que el archivo exista en {ROOT_DIR}",
            })

        result = {
            "status": 404,
            "headers": {"Content-Type": "application/json"},
            "body": not_found_body,
        }

    json.dump(result, sys.stdout)


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
    return "/" if not url else url


if __name__ == "__main__":
    main()
