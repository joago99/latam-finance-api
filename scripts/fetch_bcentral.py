#!/usr/bin/env python3
"""
BCCh Fetcher — Descarga series macroeconómicas de Chile desde el Banco Central.
Uso: python fetch_bcentral.py [--since 1958] [--output data/chile/bcentral/]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import requests

BCCH_USER = os.getenv("BCCH_USER", "joaquin.almendra@gmail.com")
BCCH_PASS = os.getenv("BCCH_PASS", "BCCjoago20")
BCCH_BASE = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

# Series confirmadas y de interés prioritario
# (nombre_legible, código, frecuencia, metadatos extra)
SERIES = [
    # ---- Diarias ----
    ("TPM",              "F022.TPM.TIN.D001.NO.Z.D", "DAILY",   "%"),
    ("UF",               "F073.UFF.PRE.Z.D",         "DAILY",   "CLP"),
    ("Dolar_Observado",  "F073.TCO.PRE.Z.D",         "DAILY",   "CLP"),
    ("Euro",             "F072.CLP.EUR.N.O.D",       "DAILY",   "CLP"),
    # ---- Mensuales ----
    ("UTM",              "F073.UTR.PRE.Z.M",         "MONTHLY", "CLP"),
    ("IMACEC",           "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M", "MONTHLY", "índice 2018=100"),
    ("IPC_var_mensual",  "G073.IPC.VAR.2023.M",      "MONTHLY", "var % mensual"),
    ("Desempleo",        "F049.DES.TAS.HIST.10.M",   "MONTHLY", "%"),
    # ---- Trimestrales ----
    ("PIB_var_anual",    "F019.PIB.VAR.CH.T",        "QUARTERLY", "var % anual"),
    # ---- Índices bursátiles (bonus) ----
    ("IPSA",             "F013.IBC.IND.N.7.LAC.CL.CLP.BLO.D", "DAILY", "puntos"),
    ("IGPA",             "F013.IBG.IND.N.7.LAC.CL.CLP.BLO.D", "DAILY", "puntos"),
    ("Cobre_USD",        "F019.PPB.PRE.100.D",       "DAILY",   "USD/oz"),
    ("Petroleo_WTI",     "F019.PPB.PRE.41B.D",       "DAILY",   "USD/barril"),
    # ---- Anuales (bonus) ----
    ("PIB_per_capita",   "F019.PIBPC.FLU.CH.A",      "ANNUAL",  "USD PPP"),
    ("Poblacion",        "F049.POB.STO.INE1.01.A",   "ANNUAL",  "personas"),
    ("Pob_Hombres",      "F049.POB.STO.INE1.02.A",   "ANNUAL",  "personas"),
    ("Pob_Mujeres",      "F049.POB.STO.INE1.03.A",   "ANNUAL",  "personas"),
]


def _fetch_series(code: str, firstdate: Optional[str] = None, lastdate: Optional[str] = None) -> dict:
    """Llamada directa al endpoint GetSeries del BCCh."""
    params = {
        "user": BCCH_USER,
        "pass": BCCH_PASS,
        "function": "GetSeries",
        "timeseries": code,
    }
    if firstdate:
        params["firstdate"] = firstdate
    if lastdate:
        params["lastdate"] = lastdate

    resp = requests.get(BCCH_BASE, params=params, timeout=60)
    resp.encoding = "iso-8859-1"
    resp.raise_for_status()
    data = resp.json()

    if data.get("Codigo") != 0:
        raise RuntimeError(f"BCCh API error {data.get('Codigo')}: {data.get('Descripcion')}")

    return data


def fetch_and_save(
    code: str,
    name: str,
    unit: str,
    output_dir: Path,
    firstdate: Optional[str] = None,
    lastdate: Optional[str] = None,
) -> dict:
    """Descarga una serie y la guarda como JSON + CSV. Retorna resumen."""
    print(f"  ↓ {name} ({code})...", end=" ", flush=True)
    data = _fetch_series(code, firstdate, lastdate)
    series = data["Series"]
    obs = series.get("Obs") or []

    rows = []
    for o in obs:
        rows.append({
            "fecha": o["indexDateString"],
            "valor": o["value"],
            "status": o.get("statusCode", "OK"),
        })

    # JSON
    json_path = output_dir / f"{name}.json"
    json_path.write_text(json.dumps({
        "metadata": {
            "code": code,
            "name": series.get("descripEsp", name),
            "name_en": series.get("descripIng", ""),
            "unit": unit,
            "fetched_at": datetime.now().isoformat(),
            "first_obs": rows[0]["fecha"] if rows else None,
            "last_obs": rows[-1]["fecha"] if rows else None,
        },
        "data": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # CSV
    csv_path = output_dir / f"{name}.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        f.write("fecha,valor\n")
        for r in rows:
            f.write(f"{r['fecha']},{r['valor']}\n")

    print(f"✓ {len(rows)} obs ({rows[0]['fecha']} → {rows[-1]['fecha']})")
    return {"name": name, "code": code, "records": len(rows), "json": str(json_path), "csv": str(csv_path)}


def search_catalog(frequency: str = "MONTHLY") -> list[dict]:
    """Busca el catálogo completo de series para una frecuencia dada."""
    params = {
        "user": BCCH_USER,
        "pass": BCCH_PASS,
        "function": "SearchSeries",
        "frequency": frequency,
    }
    resp = requests.get(BCCH_BASE, params=params, timeout=60)
    resp.encoding = "iso-8859-1"
    resp.raise_for_status()
    data = resp.json()
    if data.get("Codigo") != 0:
        raise RuntimeError(f"SearchSeries error: {data.get('Descripcion')}")
    return data.get("SeriesInfos", [])


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fetch BCCh macroeconomic series")
    parser.add_argument("--since", type=str, default="1958-01-01", help="First date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, default=None, help="Last date (default: today)")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    parser.add_argument("--search", type=str, default=None, help="SearchSeries for frequency (DAILY|MONTHLY|QUARTERLY|ANNUAL)")
    args = parser.parse_args()

    if args.search:
        print(f"Buscando catálogo de series {args.search}...")
        catalog = search_catalog(args.search)
        print(f"Encontradas {len(catalog)} series:")
        for s in catalog:
            print(f"  {s['seriesId']}: {s['spanishTitle']} ({s['firstObservation']} → {s['lastObservation']})")
        # Guardar catálogo
        out = Path(args.output) if args.output else Path("data/chile/bcentral")
        out.mkdir(parents=True, exist_ok=True)
        cat_path = out / f"catalog_{args.search.lower()}.json"
        cat_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Catálogo guardado: {cat_path}")
        return

    output_dir = Path(args.output) if args.output else Path("data/chile/bcentral")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"BCCh Fetcher — {len(SERIES)} series desde {args.since}")
    print(f"Output: {output_dir}")
    print()

    results = []
    errors = []

    for name, code, freq, unit in SERIES:
        try:
            r = fetch_and_save(code, name, unit, output_dir, args.since, args.until)
            results.append(r)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            errors.append({"name": name, "code": code, "error": str(e)})

    # Summary
    summary = {
        "fetched_at": datetime.now().isoformat(),
        "since": args.since,
        "until": args.until or str(date.today()),
        "total_series": len(results),
        "total_errors": len(errors),
        "series": results,
        "errors": errors,
    }

    summary_path = output_dir / "fetch_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"✓ {len(results)}/{len(SERIES)} series descargadas")
    for r in results:
        print(f"  {r['name']:20s} → {r['records']:6d} registros")
    if errors:
        print(f"✗ {len(errors)} errores:")
        for e in errors:
            print(f"  {e['name']}: {e['error']}")
    print(f"\nSummary: {summary_path}")


if __name__ == "__main__":
    main()
