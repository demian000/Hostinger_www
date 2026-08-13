#!/usr/bin/env python3
"""
strip_pii.py — Removedor de datos PII (Información Personal Identificable)
strip_pii.py — PII (Personally Identifiable Information) remover

Modo: Response / Filter
Fase: Response — Remueve campos sensibles de respuestas JSON antes de llegar al cliente.

Mode: Response / Filter — Removes sensitive fields from JSON responses before reaching client.

Uso / Usage:
  - match_pattern: *://api.example.com/v2/users*
  - phase: Response
  - mode: Filter

Campos que redacta / Fields it redacts:
  - email → [REDACTED]
  - phone → [REDACTED]
  - address → [REDACTED]
  - ssn → [REDACTED]
  - credit_card → [REDACTED]
  - password → [REDACTED]
  - secret → [REDACTED]
"""
import json
import sys


# Lista de campos PII a redactar / List of PII fields to redact
PII_FIELDS = {"email", "phone", "address", "ssn", "credit_card", "password", "secret"}


def main():
    data = json.load(sys.stdin)

    if data.get("phase") != "response" or data.get("mode") != "filter":
        json.dump({
            "status": data.get("status", 200),
            "headers": data.get("headers", {}),
            "body": data.get("body", ""),
        }, sys.stdout)
        return

    body_str = data.get("body", "")
    if not body_str:
        json.dump({
            "status": data.get("status", 200),
            "headers": data.get("headers", {}),
            "body": body_str,
        }, sys.stdout)
        return

    try:
        body = json.loads(body_str)
    except json.JSONDecodeError:
        # No es JSON, pasar sin cambios / Not JSON, pass through
        json.dump({
            "status": data.get("status", 200),
            "headers": data.get("headers", {}),
            "body": body_str,
        }, sys.stdout)
        return

    # Redactar PII recursivamente / Redact PII recursively
    redact_pii(body)

    result = {
        "status": data.get("status", 200),
        "headers": data.get("headers", {}),
        "body": json.dumps(body),
    }
    json.dump(result, sys.stdout)


def redact_pii(obj):
    """Redacta campos PII en cualquier nivel del JSON."""
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            key_lower = key.lower()
            if key_lower in PII_FIELDS:
                obj[key] = "[REDACTED]"
            else:
                redact_pii(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            redact_pii(item)


if __name__ == "__main__":
    main()
