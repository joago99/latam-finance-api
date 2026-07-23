#!/usr/bin/env python3
"""
Genera datasets sintéticos/mock de macro chilena mensual desde 1990 hasta 2026-06.
Reemplazar por datos oficiales del BCCh cuando las credenciales estén disponibles.
"""
from __future__ import annotations

import csv
import math
import os
from datetime import date, timedelta
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "bcentral" / "chile_macro_monthly.csv"
START_MONTH = date(1990, 1, 1)
END_MONTH = date(2026, 6, 1)


def iter_months(start: date, end: date):
    current = date(start.year, start.month, 1)
    while current <= end:
        yield current
        year = current.year + (current.month // 12)
        month = (current.month % 12) + 1
        current = date(year, month, 1)


def month_index(d: date) -> int:
    return (d.year - 1990) * 12 + (d.month - 1)


rows: list[dict[str, object]] = []
for m in iter_months(START_MONTH, END_MONTH):
    idx = month_index(m)
    year_fraction = idx / 12.0

    # TPM: tasa base con fluctuaciones estacionales
    tpm = 8.0 + 2.0 * math.sin(year_fraction * 2.5)

    # UF: acumulado diario, aproximación mensual
    uf = round(9000 + idx * 250 + 1200 * math.sin(year_fraction * 1.8), 2)

    # IVP correlacionado con UF
    ivp = round(uf * 0.98 + 120 * math.sin(year_fraction * 1.2), 2)

    # UTM: correlacionado con UF/poder adquisitivo
    utm = round((uf / 28.5) + 2500 * math.sin(year_fraction * 1.6), 2)

    # Dólar observado
    usd = round(580 + 80 * math.sin(year_fraction * 1.4 + 0.5), 2)

    # Euro
    eur = round(usd * 0.92 + 15 * math.cos(year_fraction * 1.1), 2)

    # IPC: variación mensual acumulada anual
    ipc = round(0.2 + 0.15 * math.sin(year_fraction * 2.1 + 1.0), 2)

    # IMACEC: crecimiento anualizado estimado
    imacec = round(2.8 + 0.6 * math.sin(year_fraction * 1.9), 2)

    rows.append({
        "fecha": m.strftime("%Y-%m-%d"),
        "TPM_pct": f"{tpm:.2f}",
        "UF": f"{uf:.2f}",
        "IVP": f"{ivp:.2f}",
        "UTM": f"{utm:.2f}",
        "USD_CLP": f"{usd:.2f}",
        "EUR_CLP": f"{eur:.2f}",
        "IPC_var_mensual_pct": f"{ipc:.2f}",
        "IMACEC_var_anual_pct": f"{imacec:.2f}",
    })

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "fecha",
            "TPM_pct",
            "UF",
            "IVP",
            "UTM",
            "USD_CLP",
            "EUR_CLP",
            "IPC_var_mensual_pct",
            "IMACEC_var_anual_pct",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"CSV generado: {OUTPUT_PATH}")
print(f"Registros: {len(rows)}")
print(f"Rango: {rows[0]['fecha']} -> {rows[-1]['fecha']}")
