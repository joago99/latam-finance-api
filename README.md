# La Línea

**Análisis macroeconómico de Chile desde 1958 hasta hoy.**

La Línea integra datos de fuentes oficiales — Banco Central de Chile, Instituto Nacional de Estadísticas y Banco Mundial — en una sola capa de información limpia y consultable, con visualización interactiva y contexto histórico.

## Datos que utilizamos

- **Indicadores macro mensuales** (BCCh): TPM, UF, Dólar observado, Euro, UTM, IMACEC, IPC, Desempleo, PIB, IPSA, Cobre, Petróleo WTI, PIB per cápita.
- **Población nacional por sexo** (INE): Total, hombres y mujeres, desde 1992.
- **Comparación internacional** (Banco Mundial): PIB per cápita (USD) de 24 economías, serie 1960-2023.
- **Población mundial** (Banco Mundial): Total mundial, Latinoamérica y 24 países.
- **Contexto histórico**: 63 hitos — terremotos, reformas, crisis, procesos políticos — organizados por período presidencial.
- **Períodos presidenciales**: 12 gobiernos desde Jorge Alessandri (1958) hasta Gabriel Boric, con bandas de color por ideología.

## Lo que hace

- Dashboard interactivo con 13 indicadores económicos, filtrables por fecha y presidente.
- Gráficos de comparación internacional: evolución histórica, ranking 2023, índice de crecimiento, convergencia con mediana mundial y distribución poblacional.
- Los períodos presidenciales se muestran como bandas de color dentro del gráfico principal.
- Los hitos históricos más importantes aparecen señalados como puntos sobre la línea del indicador.
- Filtro por presidente: al seleccionarlo, el gráfico y la lista de eventos se acotan al período exacto.
- Modo de agregación automática: rangos mayores a 20 años agrupan datos en promedios anuales.

## Cómo se sirve

- Versión local: servidor Python (FastAPI) que expone los datos como API REST y sirve la página web.
- Versión online: copia estática con los datos congelados en JSON, publicada en GitHub Pages.
- Sin build tools: HTML + JavaScript vanilla + Chart.js.

## Fuentes

| Fuente | Datos | Período |
|--------|-------|---------|
| Banco Central de Chile (BCCh) | TPM, UF, USD, EUR, UTM, IMACEC, IPC, Desempleo, PIB, IPSA, Cobre, WTI, PIBPC | 1958–2026 |
| Instituto Nacional de Estadísticas (INE) | Población total, hombres y mujeres | 1992–2026 |
| Banco Mundial — NY.GDP.PCAP.CD | PIB per cápita (USD), 24 países | 1960–2023 |
| Banco Mundial — SP.POP.TOTL | Población total mundial y por país | 1960–2023 |

## Enlaces

- **Online:** https://joago99.github.io/la-linea-web/
- **Local:** http://127.0.0.1:8080/ (con gateway) o http://127.0.0.1:8099/ (estático)

---

*Powered by CápsulaData*
