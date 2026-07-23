#!/usr/bin/env python3
"""
Genera un archivo unificado de datos macro mensuales para el dashboard,
combinando todas las series descargadas del BCCh.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "chile" / "bcentral"
OUTPUT = DATA_DIR / "chile_macro_monthly.json"

SERIES_FILES = [
    "TPM.json",
    "UF.json",
    "Dolar_Observado.json",
    "Euro.json",
    "UTM.json",
    "IMACEC.json",
    "IPC_var_mensual.json",
    "Desempleo.json",
    "PIB_var_anual.json",
    "IPSA.json",
    "Cobre_USD.json",
    "Petroleo_WTI.json",
    "PIB_per_capita.json",
    "Poblacion.json",
]

# Short clean names for the unified output
SHORT_NAMES = {
    "TPM": "TPM",
    "UF": "UF",
    "Dolar_Observado": "USD",
    "Euro": "EUR",
    "UTM": "UTM",
    "IMACEC": "IMACEC",
    "IPC_var_mensual": "IPC",
    "Desempleo": "DESEMPLEO",
    "PIB_var_anual": "PIB",
    "IPSA": "IPSA",
    "Cobre_USD": "COBRE",
    "Petroleo_WTI": "WTI",
    "PIB_per_capita": "PIBPC",
    "Poblacion": "POB",
}


def month_key(date_str: str) -> str:
    """Convierte 'DD-MM-YYYY' o 'YYYY-MM-DD' a 'YYYY-MM'."""
    date_str = date_str.strip()
    if "-" in date_str and len(date_str.split("-")[0]) == 2:
        # DD-MM-YYYY
        parts = date_str.split("-")
        return f"{parts[2]}-{parts[1]}"
    elif "-" in date_str:
        # YYYY-MM-DD
        return date_str[:7]
    return date_str[:7]


def aggregate_daily_to_monthly(data: list[dict], value_key: str = "valor") -> dict[str, float]:
    """Convierte datos diarios a promedios mensuales."""
    monthly = defaultdict(list)
    for row in data:
        mk = month_key(row["fecha"])
        try:
            v = float(str(row[value_key]).replace(",", "."))
            monthly[mk].append(v)
        except (ValueError, TypeError):
            continue
    return {k: round(sum(v) / len(v), 4) for k, v in monthly.items()}


def aggregate_last_of_month(data: list[dict], value_key: str = "valor") -> dict[str, float]:
    """Toma el último valor de cada mes (útil para UF, UTM, etc)."""
    monthly = {}
    for row in data:
        mk = month_key(row["fecha"])
        try:
            v = float(str(row[value_key]).replace(",", "."))
            monthly[mk] = v
        except (ValueError, TypeError):
            continue
    return monthly


def aggregate_quarterly_to_monthly(data: list[dict], value_key: str = "valor") -> dict[str, float]:
    """Expande datos trimestrales (ej: PIB) al mes de inicio del trimestre."""
    result = {}
    for row in data:
        fecha = row["fecha"]
        try:
            v = float(str(row[value_key]).replace(",", "."))
            mk = month_key(fecha)
            result[mk] = v
        except (ValueError, TypeError):
            continue
    return result


def main():
    print(f"Leyendo series desde {DATA_DIR}...")

    all_series: dict[str, dict] = {}

    for fname in SERIES_FILES:
        path = DATA_DIR / fname
        if not path.exists():
            print(f"  ✗ {fname}: no encontrado")
            continue

        with open(path, encoding="utf-8") as f:
            series_data = json.load(f)

        name = series_data["metadata"]["name"]
        short = SHORT_NAMES.get(fname.replace(".json", ""), name)
        rows = series_data["data"]
        monthly: dict[str, float] = {}

        # Determinar frecuencia y agregar
        if name in ("IMACEC", "UTM", "IPC_var_mensual", "Desempleo", "PIB_var_anual"):
            monthly = {month_key(r["fecha"]): float(str(r["valor"]).replace(",", "."))
                       for r in rows if r["valor"]}
        elif name == "PIB_var_anual":
            monthly = aggregate_quarterly_to_monthly(rows)
        else:
            monthly = aggregate_last_of_month(rows)

        all_series[short] = monthly
        print(f"  ✓ {short}: {len(monthly)} meses")

    # Combinar todos los meses
    all_months = set()
    for s in all_series.values():
        all_months.update(s.keys())

    all_months = sorted(all_months)

    # Construir arreglo unificado
    output = []
    for mk in all_months:
        entry = {"fecha": mk}
        for sname, sdata in all_series.items():
            if mk in sdata:
                v = sdata[mk]
                # Sanitize NaN/Inf to null for JSON compliance
                import math
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    v = None
                entry[sname] = v
        output.append(entry)

    # Guardar
    OUTPUT.write_text(json.dumps({
        "metadata": {
            "fuente": "Banco Central de Chile (BDE)",
            "generado": date.today().isoformat(),
            "total_meses": len(output),
            "series": list(all_series.keys()),
        },
        "data": output,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓ Archivo unificado generado: {OUTPUT}")
    print(f"  {len(output)} meses ({output[0]['fecha']} → {output[-1]['fecha']})")
    print(f"  Series: {', '.join(all_series.keys())}")

    # Quick stats
    print(f"\nÚltimo mes ({output[-1]['fecha']}):")
    for k, v in output[-1].items():
        if k != "fecha":
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
