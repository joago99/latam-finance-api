# La Línea, por CápsulaData

**La economía de Chile desde 1958, contada con datos.**

La Línea es un dashboard interactivo que cruza 13 indicadores macroeconómicos con 68 años de historia política. Una sola fuente para entender la relación entre las cifras y los eventos que marcaron al país.

---

## Qué problema resuelve

Los datos macro de Chile existen — BCCh, INE, Banco Mundial — pero están dispersos, con formatos distintos, documentación inconsistente y sin conexión entre sí. Para responder "¿qué pasó con la inflación durante el gobierno de Allende?" o "¿cómo se compara el PIB per cápita de Chile con el de Noruega?", necesitabas abrir cinco fuentes distintas, limpiar los datos y armarlos a mano.

La Línea integra todo en un lugar, con contexto histórico y comparación internacional.

---

## Dashboard Chile

- **13 indicadores**: TPM, UF, USD, EUR, UTM, IMACEC, IPC, Desempleo, PIB, IPSA, Cobre, WTI, PIB per cápita.
- **Población por sexo**: total, hombres y mujeres (desde 1992, INE).
- **Filtro por período presidencial**: cada gobierno se ve como una banda de color en el eje del gráfico. Al hacer clic, el dashboard se acota a ese período.
- **Bandas de ideología**: izquierda (rojo), centro (gris), derecha (azul), con 5 niveles de intensidad.
- **Datos combinados**: Dólar y Euro en una misma serie. Población total + hombres + mujeres en un gráfico mixto (línea + barras).
- **Agregación automática**: rangos >20 años agrupan en promedios anuales.

## Chile vs el Mundo

Comparación del PIB per cápita de Chile con 23 economías:

1. **Evolución histórica** — 9 países seleccionados. Chile en rojo siempre.
2. **Ranking 2023** — Barras horizontales ordenadas. Chile en rojo destacado.
3. **Crecimiento desde 1990** — Índice base 100. Chile vs potencias asiáticas y pares regionales.
4. **Convergencia** — Chile vs mediana de los 23 países.
5. **Ranking de población** — Los 24 países ordenados por habitantes.

## Datos que utilizamos

| Fuente | Indicador | Cobertura |
|--------|-----------|-----------|
| Banco Central de Chile | TPM, UF, USD, EUR, UTM, IMACEC, IPC, Desempleo, PIB, IPSA, Cobre, WTI, PIBPC | 1958–2026 |
| INE | Población total, hombres, mujeres | 1992–2026 |
| Banco Mundial (NY.GDP.PCAP.CD) | PIB per cápita (USD), 24 países | 1960–2023 |
| Banco Mundial (SP.POP.TOTL) | Población total, 24 países + regiones | 1960–2023 |

---

## Live demo

👉 [**Abrir La Línea**](https://joago99.github.io/la-linea-web/)
(Copia estática en GitHub Pages. Sin backend, sin API keys.)

👉 **Versión local con gateway:** `python api/gateway.py` → http://127.0.0.1:8080/

---

*Proyecto de CápsulaData. Datos macro que se entienden.*