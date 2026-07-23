#!/usr/bin/env python3
"""
Monitor semanal de estructura de datos BCCh.
Verifica:
1. Que todas las series sigan disponibles
2. Que los códigos de serie no hayan cambiado (SearchSeries)
3. Que haya nuevos datos desde la última descarga
4. Que la estructura JSON no haya cambiado (campos nuevos/eliminados)
5. Alerta si alguna serie dejó de actualizarse
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

BCCH_USER = os.getenv("BCCH_USER", "joaquin.almendra@gmail.com")
BCCH_PASS = os.getenv("BCCH_PASS", "BCCjoago20")
BCCH_BASE = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "chile" / "bcentral"
SUMMARY_PATH = DATA_DIR / "fetch_summary.json"
MONITOR_LOG = DATA_DIR / "monitor_log.json"

# Series que monitoreamos
SERIES = [
    ("TPM",              "F022.TPM.TIN.D001.NO.Z.D", "DAILY"),
    ("UF",               "F073.UFF.PRE.Z.D", "DAILY"),
    ("Dolar_Observado",  "F073.TCO.PRE.Z.D", "DAILY"),
    ("Euro",             "F072.CLP.EUR.N.O.D", "DAILY"),
    ("UTM",              "F073.UTR.PRE.Z.M", "MONTHLY"),
    ("IMACEC",           "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M", "MONTHLY"),
    ("IPC_var_mensual",  "G073.IPC.VAR.2023.M", "MONTHLY"),
    ("Desempleo",        "F049.DES.TAS.HIST.10.M", "MONTHLY"),
    ("PIB_var_anual",    "F019.PIB.VAR.CH.T", "QUARTERLY"),
    ("IPSA",             "F013.IBC.IND.N.7.LAC.CL.CLP.BLO.D", "DAILY"),
    ("IGPA",             "F013.IBG.IND.N.7.LAC.CL.CLP.BLO.D", "DAILY"),
    ("Cobre_USD",        "F019.PPB.PRE.100.D", "DAILY"),
    ("Petroleo_WTI",     "F019.PPB.PRE.41B.D", "DAILY"),
]

# Días máximos sin datos nuevos antes de alertar (según frecuencia)
MAX_STALE_DAYS = {"DAILY": 5, "MONTHLY": 45, "QUARTERLY": 120}


def fetch_latest(code: str, days: int = 30) -> dict | None:
    """Obtiene los últimos N días de una serie para verificar actividad reciente."""
    since = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "user": BCCH_USER, "pass": BCCH_PASS,
        "function": "GetSeries", "timeseries": code,
        "firstdate": since,
    }
    try:
        resp = requests.get(BCCH_BASE, params=params, timeout=30)
        resp.encoding = "iso-8859-1"
        data = resp.json()
        if data.get("Codigo") != 0:
            return {"error": f"Code {data['Codigo']}: {data['Descripcion']}"}
        return data
    except Exception as e:
        return {"error": str(e)}


def check_catalog() -> dict:
    """Verifica que cada serie esté en su catálogo de frecuencia correcta."""
    issues = []
    catalog_cache = {}

    for name, code, freq in SERIES:
        if freq not in catalog_cache:
            params = {
                "user": BCCH_USER, "pass": BCCH_PASS,
                "function": "SearchSeries", "frequency": freq,
            }
            try:
                resp = requests.get(BCCH_BASE, params=params, timeout=60)
                resp.encoding = "iso-8859-1"
                data = resp.json()
                if data.get("Codigo") != 0:
                    issues.append(f"SearchSeries {freq} error: {data.get('Descripcion')}")
                    catalog_cache[freq] = set()
                else:
                    catalog_cache[freq] = {s["seriesId"] for s in data.get("SeriesInfos", [])}
            except Exception as e:
                issues.append(f"SearchSeries {freq} exception: {e}")
                catalog_cache[freq] = set()

        if code not in catalog_cache.get(freq, set()):
            issues.append(f"  ✗ {name} ({code}): NO en catálogo {freq}")

    return {"catalog_issues": issues, "catalog_ok": len(issues) == 0}


def check_series_health() -> list[dict]:
    """Verifica cada serie individualmente."""
    results = []
    lookup_days = {"DAILY": 10, "MONTHLY": 60, "QUARTERLY": 180}

    for name, code, freq in SERIES:
        entry = {"name": name, "code": code, "freq": freq, "status": "ok", "issues": []}

        # 1. ¿Responde la API?
        data = fetch_latest(code, days=lookup_days[freq])
        if not data or "error" in data:
            entry["status"] = "error"
            entry["issues"].append(f"API error: {data.get('error', 'no response')}")
            results.append(entry)
            continue

        obs = data.get("Series", {}).get("Obs") or []
        if not obs:
            entry["status"] = "warning"
            entry["issues"].append(f"Sin observaciones en últimos {lookup_days[freq]} días")
            results.append(entry)
            continue

        # 2. ¿Hay datos dentro del umbral aceptable?
        last_date_str = obs[-1].get("indexDateString", "")
        try:
            last_date = datetime.strptime(last_date_str, "%d-%m-%Y").date()
            days_since = (date.today() - last_date).days
            entry["last_obs"] = last_date_str
            entry["days_since_last"] = days_since
            max_stale = MAX_STALE_DAYS.get(freq, 30)
            if days_since > max_stale:
                entry["status"] = "warning"
                entry["issues"].append(f"Último dato: {last_date_str} ({days_since}d, umbral {max_stale}d)")
        except ValueError:
            entry["issues"].append(f"Fecha no parseable: {last_date_str}")

        # 3. ¿Estructura de campos esperada?
        expected_fields = {"indexDateString", "value", "statusCode"}
        actual_fields = set(obs[0].keys()) if obs else set()
        new_fields = actual_fields - expected_fields
        missing_fields = expected_fields - actual_fields
        if new_fields:
            entry["issues"].append(f"Nuevos campos en respuesta: {new_fields}")
        if missing_fields:
            entry["issues"].append(f"Campos faltantes en respuesta: {missing_fields}")

        # 4. Comparar con descarga anterior
        json_path = DATA_DIR / f"{name}.json"
        if json_path.exists():
            stored = json.loads(json_path.read_text(encoding="utf-8"))
            stored_last = stored.get("metadata", {}).get("last_obs", "")
            if stored_last and stored_last == last_date_str:
                entry["issues"].append(f"Sin datos nuevos desde última descarga ({stored_last})")
            entry["stored_records"] = len(stored.get("data", []))
            entry["live_records"] = len(obs)

        entry["obs_count"] = len(obs)
        results.append(entry)

    return results


def main():
    today = date.today().isoformat()
    print(f"=== Monitor BCCh — {today} ===\n")

    # 1. Catálogo
    print("1. Verificando catálogo de series...")
    catalog = check_catalog()
    if catalog["catalog_ok"]:
        print("   ✓ Todas las series presentes en el catálogo")
    else:
        for issue in catalog["catalog_issues"]:
            print(f"   ✗ {issue}")

    # 2. Health de cada serie
    print("\n2. Verificando salud de series...")
    health = check_series_health()
    ok = sum(1 for h in health if h["status"] == "ok")
    warn = sum(1 for h in health if h["status"] == "warning")
    err = sum(1 for h in health if h["status"] == "error")

    for h in health:
        icon = "✓" if h["status"] == "ok" else ("⚠" if h["status"] == "warning" else "✗")
        extra = ""
        if h.get("days_since_last") is not None:
            extra = f" (último: {h['last_obs']}, hace {h['days_since_last']}d)"
        print(f"   {icon} {h['name']:20s} [{h['status']:7s}] {h.get('obs_count',0)} obs recientes{extra}")
        for issue in h.get("issues", []):
            print(f"      → {issue}")

    # 3. Guardar log
    log_entry = {
        "date": today,
        "summary": {"ok": ok, "warning": warn, "error": err, "total": len(health)},
        "catalog": catalog,
        "series": health,
    }

    existing_logs = []
    if MONITOR_LOG.exists():
        existing_logs = json.loads(MONITOR_LOG.read_text(encoding="utf-8"))
    existing_logs.append(log_entry)
    # Mantener solo últimas 52 semanas
    existing_logs = existing_logs[-52:]
    MONITOR_LOG.write_text(json.dumps(existing_logs, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. Resultado
    print(f"\n{'='*50}")
    print(f"Resultado: {ok} OK, {warn} warnings, {err} errores")
    if err > 0:
        print("⚠ HAY ERRORES QUE REQUIEREN ATENCIÓN")
        sys.exit(1)
    elif warn > 0:
        print("⚠ Hay warnings — revisar log")
    else:
        print("✓ Todo OK")


if __name__ == "__main__":
    main()
