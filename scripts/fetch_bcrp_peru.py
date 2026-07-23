#!/usr/bin/env python3
"""
Fetch data from BCRP (Banco Central de Reserva del Perú) — no auth required.
Proof-of-concept: this pipeline can feed macro data into the unified API gateway.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import requests

BCRP_BASE = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"

SERIES = [
    {"code": "PN01270PM", "name": "IPC_Lima", "freq": "M", "unit": "índice"},
    {"code": "PN01288PM", "name": "Encaje_Bancario_MN", "freq": "M", "unit": "millones S/"},
    {"code": "PN01289PM", "name": "Encaje_Bancario_ME", "freq": "M", "unit": "millones US$"},
]


def fetch_series(code: str, start: str = "1990-1", end: str = "2026-6") -> dict:
    url = f"{BCRP_BASE}/{code}/json/{start}/{end}/esp"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    output_dir = Path(__file__).resolve().parents[1] / "data" / "peru" / "bcrp"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for serie in SERIES:
        code = serie["code"]
        print(f"Fetching {serie['name']} ({code})...", end=" ")
        try:
            data = fetch_series(code)
            periods = data.get("periods", [])
            rows = []
            for p in periods:
                month_name = p["name"]
                val = p["values"][0] if p["values"] else None
                rows.append({"fecha": month_name, "valor": val})

            # Save JSON
            json_path = output_dir / f"{serie['name']}.json"
            json_path.write_text(json.dumps({
                "metadata": {"code": code, "name": serie["name"], "unit": serie["unit"], "freq": serie["freq"]},
                "data": rows
            }, indent=2, ensure_ascii=False), encoding="utf-8")

            # Save CSV
            csv_path = output_dir / f"{serie['name']}.csv"
            with csv_path.open("w", encoding="utf-8") as f:
                f.write("fecha,valor\n")
                for r in rows:
                    f.write(f"{r['fecha']},{r['valor']}\n")

            results.append({"name": serie["name"], "records": len(rows), "path": str(json_path)})
            print(f"✓ {len(rows)} registros")

        except Exception as e:
            print(f"✗ ERROR: {e}")

    # Summary
    summary = {"fetched_at": date.today().isoformat(), "series": results}
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓ {len(results)}/{len(SERIES)} series guardadas en {output_dir}")
    for r in results:
        print(f"  - {r['name']}: {r['records']} registros")


if __name__ == "__main__":
    main()
