# LatAm Finance API — Fase 1: Chile

**Gateway unificado de datos macroeconómicos, políticos y periodísticos de América Latina.**

> 🚀 Fase 1: Chile (1990-2026). Perú y Brasil en Fase 2.

## 📊 Demo visual

Abrir en navegador:
```
http://127.0.0.1:8080/dashboard
```

O abrir directamente el archivo:
```
web/linea-del-poder/index.html
```

## 🔧 Stack

| Capa | Tecnología |
|------|-----------|
| API Gateway | FastAPI (Python 3.11+) |
| Dashboard | HTML5 + Chart.js 4 (sin build) |
| Datos estáticos | JSON (presidentes, hitos) |
| Datos macro | BCCh BDE (requiere credenciales) / placeholder |
| Caché | Redis (planeado) |

## 📁 Estructura

```
latam-finance-api/
├── api/
│   └── gateway.py              # FastAPI server (puerto 8080)
├── data/
│   ├── chile/
│   │   ├── presidentes.json    # 8 presidentes (1990-2026)
│   │   └── hitos.json          # 38 hitos históricos
│   └── peru/
│       └── bcrp/               # Datos reales BCRP (sin auth)
├── scripts/
│   ├── fetch_bcentral.py       # Fetcher BCCh (requiere credenciales)
│   └── fetch_bcrp_peru.py      # Fetcher BCRP (sin auth — funcional)
├── web/
│   └── linea-del-poder/
│       └── index.html          # Dashboard interactivo
└── README.md
```

## 🚀 Quickstart

```bash
# Instalar dependencias
pip install fastapi uvicorn bcchapi requests

# Iniciar API
cd latam-finance-api
python api/gateway.py

# Abrir dashboard
# http://127.0.0.1:8080/dashboard
```

## 📡 Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/chile/presidentes` | Lista de presidentes (1990-2026) |
| GET | `/api/v1/chile/presidentes/{id}` | Presidente específico |
| GET | `/api/v1/chile/hitos` | Hitos históricos (filtrable: `?categoria=`, `?presidente_id=`, `?desde=`, `?hasta=`) |
| GET | `/api/v1/chile/timeline` | Timeline unificado (presidentes + hitos) |
| GET | `/dashboard` | Dashboard interactivo "La Línea del Poder" |

## 🔑 Credenciales pendientes

Para datos macro reales de Chile:
1. Registrarse en https://si3.bcentral.cl/estadisticas/principal1/web_services/index.htm
2. Obtener usuario/contraseña
3. Configurar `BCCH_USER` y `BCCH_PASS` como variables de entorno
4. Ejecutar `python scripts/fetch_bcentral.py`

## 🗺️ Roadmap

- [ ] **Fase 1.1**: Integrar BCCh con datos reales (IMACEC, IPC, TPM, UF, USD)
- [ ] **Fase 1.2**: Agregar datos SII (empresas por región/rubro)
- [ ] **Fase 1.3**: Integrar noticias (NewsAPI / GNews) correlacionadas con timeline
- [ ] **Fase 1.4**: Dashboard cliente — subir datos propios (CSV) y cruzar con macro
- [ ] **Fase 2**: Perú (BCRPData ya funciona) + Brasil (BCB SGS)
- [ ] **Fase 3**: Colombia + México

## 📄 Licencia

Propietaria. Todos los derechos reservados.
