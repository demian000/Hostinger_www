#!/usr/bin/env python3
"""
transformar_body.py — Transformación de body entre formatos
transformar_body.py — Body format transformation

Modo: Request / Filter o Response / Filter
Fase: Request o Response — Transforma el body entre formatos (JSON ↔ XML, etc.)

Mode: Request / Filter or Response / Filter
Phase: Request or Response — Transforms body between formats (JSON ↔ XML, etc.)

Uso / Usage:
  - match_pattern: *://api.example.com/legacy/*
  - phase: Request
  - mode: Filter

Soporta / Supports:
  - JSON → XML (simple)
  - XML → JSON (simple)
  - JSON path filtering (jq-like)
  - Reemplazo de texto en body
"""
import json
import sys
import re
from xml.etree.ElementTree import Element, tostring, fromstring


# ═══════════════════════════════════════════════════════════════════
# Configuración / Configuration
# ═══════════════════════════════════════════════════════════════════
TRANSFORM_CONFIG = {
    # Transformar JSON → XML cuando el endpoint es legacy
    "legacy": {"from": "json", "to": "xml"},
    # Transformar XML → JSON para endpoints modernos
    "modern": {"from": "xml", "to": "json"},
}


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    body_str = data.get("body", "")

    if not body_str:
        # Sin body, pasar sin cambios / No body, pass through
        passthrough(data)
        return

    # Determinar transformación según URL / Determine transform by URL
    if "/legacy" in url and is_json(body_str):
        print(f"[transformar_body] 🔄 JSON → XML: {url}", file=sys.stderr)
        xml_str = json_to_xml_simple(body_str)
        result = build_result(data, xml_str, "application/xml")
    elif "/modern" in url and is_xml(body_str):
        print(f"[transformar_body] 🔄 XML → JSON: {url}", file=sys.stderr)
        json_str = xml_to_json_simple(body_str)
        result = build_result(data, json_str, "application/json")
    elif "/uppercase" in url:
        result = build_result(data, body_str.upper(), data.get("headers", {}).get("Content-Type", "text/plain"))
    elif "/lowercase" in url:
        result = build_result(data, body_str.lower(), data.get("headers", {}).get("Content-Type", "text/plain"))
    elif "/reverse" in url:
        result = build_result(data, body_str[::-1], data.get("headers", {}).get("Content-Type", "text/plain"))
    else:
        passthrough(data)
        return

    json.dump(result, sys.stdout)


def build_result(data, new_body: str, content_type: str) -> dict:
    """Construye el resultado con el nuevo body."""
    base = {"headers": data.get("headers", {})}
    base["headers"]["X-Transformed"] = "true"
    base["headers"]["Content-Type"] = content_type

    # Dependiendo de la fase / Depending on phase
    if data.get("phase") == "response":
        base["status"] = data.get("status", 200)
    else:
        base["method"] = data.get("method", "GET")
        base["url"] = data.get("url", "")

    base["body"] = new_body
    return base


def passthrough(data):
    """Devuelve los datos sin cambios."""
    base = {
        "headers": data.get("headers", {}),
        "body": data.get("body", ""),
    }
    if data.get("phase") == "response":
        base["status"] = data.get("status", 200)
    else:
        base["method"] = data.get("method", "GET")
        base["url"] = data.get("url", "")
    json.dump(base, sys.stdout)


def is_json(s: str) -> bool:
    s = s.strip()
    return s.startswith("{") or s.startswith("[")


def is_xml(s: str) -> bool:
    s = s.strip()
    return s.startswith("<")


def json_to_xml_simple(json_str: str) -> str:
    """Convierte JSON simple a XML."""
    try:
        obj = json.loads(json_str)
    except json.JSONDecodeError:
        return json_str

    def dict_to_xml(d: dict, root_name="root") -> str:
        root = Element(root_name)
        for key, value in d.items():
            child = Element(key)
            if isinstance(value, dict):
                child.text = dict_to_xml(value, key)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        item_elem = Element(key.rstrip("s") or "item")
                        for k, v in item.items():
                            sub = Element(k)
                            sub.text = str(v)
                            item_elem.append(sub)
                        root.append(item_elem)
                    else:
                        child.text = str(item)
                        root.append(child)
                continue
            else:
                child.text = str(value)
            root.append(child)
        return tostring(root, encoding="unicode", short_empty_elements=False)

    return dict_to_xml(obj)


def xml_to_json_simple(xml_str: str) -> str:
    """Convierte XML simple a JSON."""
    try:
        root = fromstring(xml_str)
    except Exception:
        return xml_str

    def elem_to_dict(elem) -> dict:
        result = {}
        for child in elem:
            if len(child) > 0:
                result[child.tag] = elem_to_dict(child)
            else:
                result[child.tag] = child.text or ""
        return result

    return json.dumps({root.tag: elem_to_dict(root)}, indent=2)


if __name__ == "__main__":
    main()
