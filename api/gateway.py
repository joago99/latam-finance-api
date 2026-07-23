#!/usr/bin/env python3
"""
FastAPI Gateway — LatAm Finance API (Fase 1: Chile)
Sirve datos macro, presidentes, hitos y timeline unificado.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="LatAm Finance API — Fase 1: Chile",
    description="Gateway unificado de datos macroeconómicos y políticos de Chile",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CHILE_DIR = DATA_DIR / "chile"
WEB_DIR = Path(__file__).resolve().parents[1] / "web"

# =====================
# Public landing page
# =====================
@app.get("/")
def public_index():
    """Página pública 'La Línea' powered by CápsulaData."""
    public_html = WEB_DIR / "public" / "index.html"
    if public_html.exists():
        return FileResponse(public_html)
    raise HTTPException(status_code=404, detail="Página pública no encontrada")

# =====================
# Helper
# =====================
def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_date(d: str) -> date:
    """Parse YYYY-MM-DD or YYYY-MM."""
    d = d.strip()
    parts = d.split("-")
    if len(parts) == 2:
        return date(int(parts[0]), int(parts[1]), 1)
    return date(int(parts[0]), int(parts[1]), int(parts[2]))


# =====================
# Endpoints
# =====================

@app.get("/")
def root():
    return {
        "api": "LatAm Finance Gateway",
        "fase": 1,
        "pais": "Chile",
        "endpoints": [
            "/api/v1/chile/presidentes",
            "/api/v1/chile/hitos",
            "/api/v1/chile/timeline",
            "/health"
        ],
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# --- Presidentes ---
@app.get("/api/v1/chile/presidentes")
def get_presidentes():
    """Retorna la lista de presidentes de Chile desde 1990."""
    return _load_json(CHILE_DIR / "presidentes.json")


@app.get("/api/v1/chile/presidentes/{presidente_id}")
def get_presidente(presidente_id: str):
    """Retorna un presidente específico."""
    data = _load_json(CHILE_DIR / "presidentes.json")
    for p in data.get("presidentes", []):
        if p["id"] == presidente_id:
            return p
    raise HTTPException(status_code=404, detail="Presidente no encontrado")


# --- Hitos ---
@app.get("/api/v1/chile/hitos")
def get_hitos(
    categoria: Optional[str] = Query(None, description="economico|politico|social|reforma|externo"),
    desde: Optional[str] = Query(None, description="YYYY-MM-DD"),
    hasta: Optional[str] = Query(None, description="YYYY-MM-DD"),
    presidente_id: Optional[str] = Query(None, description="id del presidente"),
):
    """Retorna hitos históricos con filtros opcionales."""
    data = _load_json(CHILE_DIR / "hitos.json")
    hitos = data.get("hitos", [])

    if categoria:
        hitos = [h for h in hitos if h["categoria"] == categoria]
    if desde:
        d_desde = _parse_date(desde)
        hitos = [h for h in hitos if _parse_date(h["fecha"]) >= d_desde]
    if hasta:
        d_hasta = _parse_date(hasta)
        hitos = [h for h in hitos if _parse_date(h["fecha"]) <= d_hasta]
    if presidente_id:
        presidentes_data = _load_json(CHILE_DIR / "presidentes.json")
        pres = next((p for p in presidentes_data.get("presidentes", []) if p["id"] == presidente_id), None)
        if pres:
            d_ini = _parse_date(pres["inicio"])
            d_fin = _parse_date(pres["fin"])
            hitos = [h for h in hitos if d_ini <= _parse_date(h["fecha"]) <= d_fin]

    return {"metadata": data.get("metadata", {}), "count": len(hitos), "hitos": hitos}


# --- Macro data ---
@app.get("/api/v1/chile/macro")
def get_macro():
    """Retorna datos macroeconómicos mensuales unificados de Chile (BCCh)."""
    path = CHILE_DIR / "bcentral" / "chile_macro_monthly.json"
    if not path.exists():
        raise HTTPException(status_code=503, detail="Datos macro no disponibles. Ejecutar build_dashboard_data.py primero.")
    return _load_json(path)


# --- Timeline unificado ---
@app.get("/api/v1/chile/timeline")
def get_timeline(
    desde: str = "1990-01-01",
    hasta: str = "2026-07-22",
):
    """
    Retorna timeline unificado: presidentes + hitos en un solo arreglo cronológico.
    Ideal para la visualización "La Línea del Poder".
    """
    presidentes_data = _load_json(CHILE_DIR / "presidentes.json")
    hitos_data = _load_json(CHILE_DIR / "hitos.json")

    events = []

    # Presidentes como eventos de tipo "periodo"
    for p in presidentes_data.get("presidentes", []):
        events.append({
            "type": "periodo_presidencial",
            "id": p["id"],
            "nombre": p["nombre"],
            "coalicion": p["coalicion"],
            "partido": p["partido"],
            "color": p["color_hex"],
            "fecha_inicio": p["inicio"],
            "fecha_fin": p["fin"],
            "eventos_clave": p.get("eventos_clave", [])
        })

    # Hitos como eventos puntuales
    for h in hitos_data.get("hitos", []):
        events.append({
            "type": "hito",
            "fecha": h["fecha"],
            "titulo": h["titulo"],
            "categoria": h["categoria"],
            "descripcion": h["descripcion"],
            "impacto": h.get("impacto", "medio")
        })

    # Ordenar cronológicamente
    events.sort(key=lambda e: e.get("fecha_inicio") if e["type"] == "periodo_presidencial" else e.get("fecha", ""))

    return {
        "metadata": {
            "pais": "Chile",
            "desde": desde,
            "hasta": hasta,
        },
        "total_eventos": len(events),
        "presidentes": sum(1 for e in events if e["type"] == "periodo_presidencial"),
        "hitos": sum(1 for e in events if e["type"] == "hito"),
        "events": events
    }


# =====================
# Static files (dashboard)
# =====================

@app.get("/dashboard")
@app.get("/dashboard/")
def serve_dashboard():
    """Sirve el dashboard interactivo 'La Línea del Poder'."""
    return FileResponse(WEB_DIR / "linea-del-poder" / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
