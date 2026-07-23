# La Línea — Release v1.1.0

**Fecha:** 2026-07-23
**Tag:** `v1.1.0`
**Repo fuente:** `joago99/latam-finance-api` (privado)
**Repo público:** `joago99/la-linea-web` (GitHub Pages)
**URL:** https://joago99.github.io/la-linea-web/

---

## Estructura de páginas

| Página | Tema | Ruta |
|--------|------|------|
| **La Línea** (dashboard) | Oscuro (`#1a1a2e` + `#16213e`) | `/` |
| **CápsulaData** (empresa) | Claro (`#f8fafc`, azul `#3b82f6`) | `/empresa.html` |
| **Servicios** | Claro (mismo esquema que empresa) | `/capsula-servicios.html` |

- Logo "C" con arcos concéntricos en azul medio, sin texto. PNG: `logo.png`.
- Tipografía: `Playfair Display` (títulos) + `Inter` (cuerpo).
- Navegación cruzada: todas las páginas linkean entre sí en el header.
- Tagline unificado: **"Storytelling con tus datos"** bajo el brand.

---

## Cambios técnicos vs. v1.0.0

### La Línea (dashboard oscuro)

| Fix | Detalle |
|-----|---------|
| **YearsRange** | `Array.from(all)` reemplaza `[].concat([].slice.call(Set))` que no funciona en Set. |
| **Filtro presidente** | Revertido a rango exacto (sin expansión ±1 rota). |
| **Bandas presidenciales** | Dibujadas con `beforeDraw` de Chart.js como strip de 14px en el eje X. Sin plugin externo. |
| **Tiraje de eventos** | Eliminado cuadro de noticias debajo del chart. |
| **Charts mundo** | Gráficos 1, 2, 3, 4, 5 funcionan con `safeChart()` + `yearsRange()` corregido. |
| **Chart 5** | Reemplazó donut roto por ranking horizontal de población (24 países). |
| **Composite indices** | `aggregateAnnual()` aplicado por sub-indicador (no por array completo). |

### CápsulaData (empresa, tema claro)

| Cambio | Detalle |
|--------|---------|
| Tema | De oscuro a claro: bg blanco, texto `#0f172a`, acento `#3b82f6`. |
| Logo | Brand + imagen `logo.png` pegado al texto (36px). |
| Tagline | "Storytelling con tus datos". |
| Iconos | Eliminados emojis (🔗📊🌎) de cards y sección "Para quién". |
| Nav | Links a La Línea + Servicios + secciones internas. |

### Servicios (página nueva)

| Sección | Contenido |
|---------|-----------|
| Hero + stats | 13 indicadores, 24 países, 68 años, 63 eventos. |
| Servicios | Análisis de datos · Páginas informativas · Scrapper de datos · Informes personalizados. |
| Cómo trabajamos | 4 pasos: fuentes → limpieza → producto → actualización. |
| Para quién | Dashboards ejecutivos · Documentos propios · APIs de datos. |
| Contacto | LinkedIn. |

---

## Datos utilizados

| Fuente | Indicador | Cobertura |
|--------|-----------|-----------|
| Banco Central de Chile | TPM, UF, USD, EUR, UTM, IMACEC, IPC, Desempleo, PIB, IPSA, Cobre, WTI, PIBPC | 1958–2026 |
| INE | Población total, hombres, mujeres | 1992–2026 |
| Banco Mundial (NY.GDP.PCAP.CD) | PIB per cápita (USD), 24 países | 1960–2023 |
| Banco Mundial (SP.POP.TOTL) | Población total, 24 países + regiones | 1960–2023 |

---

## Despliegue

1. `python build_static.py` → genera `/dist/` con rutas relativas (`./vendor/`).
2. `cp -r dist/* /tmp/deploy/` + `git push -f origin main` al repo público.
3. GitHub Pages rebuild en ~1–2 minutos.

## Cómo actualizar

```bash
cd C:/Users/joaqu/latam-finance-api
# 1. hacer cambios editando web/la-linea/index.html, web/empresa/index.html, etc.
python build_static.py
# 2. deploy manual: build → dist → push a la-linea-web
```

---

*Proyecto CápsulaData. Datos macro que se entienden.*
