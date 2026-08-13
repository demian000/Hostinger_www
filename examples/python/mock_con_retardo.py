#!/usr/bin/env python3
"""
mock_con_retardo.py — Simulador de latencia de red en respuestas mock
mock_con_retardo.py — Network latency simulator for mock responses

Modo: Request / Origin
Fase: Request — Simula latencia de red y luego responde con datos mock.

Mode: Request / Origin — Simulates network latency, then responds with mock data.

Uso / Usage:
  - match_pattern: *://mock-delayed.example.com/*
  - phase: Request
  - mode: Origin

Útil para probar cómo se comporta tu aplicación con respuestas lentas.
Los tiempos de latencia se pueden configurar por endpoint.

Useful for testing how your app behaves with slow responses.
Latency times can be configured per endpoint.
"""
import json
import sys
import time
import random
import re


def main():
    data = json.load(sys.stdin)

    url = data.get("url", "")
    method = data.get("method", "GET")
    path = extract_path(url)

    # ── Configurar latencia según endpoint / Configure latency per endpoint ──
    if "/slow" in path:
        delay_s = 5.0  # 5 segundos — simula endpoint muy lento
    elif "/medium" in path:
        delay_s = 2.0  # 2 segundos
    elif "/unreliable" in path:
        # Entre 0.5 y 8 segundos con variación aleatoria
        delay_s = random.uniform(0.5, 8.0)
    else:
        delay_s = random.uniform(0.3, 1.5)  # Latencia normal simulada

    # Simular latencia de red / Simulate network latency
    print(f"[mock_con_retardo] ⏳ Esperando {delay_s:.1f}s para {url}", file=sys.stderr)
    time.sleep(delay_s)

    # ── Generar respuesta / Generate response ──
    result = {
        "status": 200,
        "headers": {
            "Content-Type": "application/json",
            "X-Mock-Delayed": "true",
            "X-Mock-Latency": f"{delay_s:.2f}s",
        },
        "body": json.dumps({
            "message": "Respuesta con retardo simulado / Delayed response",
            "url": url,
            "method": method,
            "delay_seconds": round(delay_s, 2),
            "timestamp": time.time(),
        }),
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
    return url


if __name__ == "__main__":
    main()
