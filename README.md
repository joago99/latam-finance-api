# LatAm Finance API — API de datos macroeconómicos de Chile

**ES** · **EN** (bilingüe / bilingual)

API y pipeline de datos macroeconómicos de Chile construida con FastAPI, alimentada desde el Banco Central de Chile (BCCh), INE y Banco Mundial.

Chile macroeconomic data API and pipeline built with FastAPI, fed from the Central Bank of Chile (BCCh), INE and the World Bank.

---

## Qué resuelve · What it solves

Los datos macro de Chile están dispersos en fuentes con formatos distintos. Este repo unifica la extracción, transformación y publicación en una sola API + pipeline reproducible.

Chile's macro data is scattered across sources with inconsistent formats. This repo unifies extraction, transformation and publishing into a single API + reproducible pipeline.

## Componentes · Components

| Componente · Component | Función · Role |
|---|---|
| `api/gateway.py` | FastAPI gateway — sirve series macro, presidentes, hitos y timeline · FastAPI gateway serving macro series, presidents, milestones and timeline |
| `scripts/fetch_bcentral.py` | Extrae series desde el BCCh · Fetches series from BCCh |
| `scripts/monitor_bcch.py` | Monitorea disponibilidad de series · Monitors series availability |
| `scripts/fetch_bcrp_peru.py` | Extrae series del BCRP (Perú) · Fetches series from BCRP (Peru) |
| `build_static.py` / `deploy_web.py` | Construyen y despliegan el sitio estático · Build and deploy the static site |
| `data/` | Series procesadas (BCCh, INE, Banco Mundial) · Processed series |

## Cómo correr · How to run

```bash
# 1. Credenciales BCCh (variables de entorno, nunca en el repo)
export BCCH_USER=tu_correo
export BCCH_PASS=tu_clave

# 2. Levantar la API (puerto 8080)
pip install -r requirements.txt   # fastapi, uvicorn
uvicorn api.gateway:app --host 0.0.0.0 --port 8080
```

## Stack

FastAPI · Python · BCCh API · Banco Mundial · INE · GitHub Pages (front estático)

## Estado · Status

Fase 1 (Chile) funcionando. El front-end vivo se publica en [capsuladata](https://github.com/joago99/capsuladata).
Phase 1 (Chile) working. The live front-end is published in [capsuladata](https://github.com/joago99/capsuladata).
