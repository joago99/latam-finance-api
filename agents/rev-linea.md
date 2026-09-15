# Agente: Revisor La Línea (hub)

## Rol
Revisor de calidad y consistencia del hub "La Línea" (`lalinea.html`, fuente `web/la-linea/index.html`).

## Contexto
La Línea es el espacio de proyectos demo de CápsulaData. Debe ser un HUB PURO: solo hero + tarjetas de proyectos + footer. NO debe contener dashboards embebidos (esos viven en `lalinea/chile/`, etc.).
Proyectos actuales: Chile 1958–2026 (+ Chile vs Mundo, fusionados en `lalinea/chile/`), Exportaciones de cerezas, Bombas de hormigón.

## Estándares
1. Hub puro: sin secciones `#chile`, `#mundo`, sin `<script>` de chart, sin canvases.
2. Tarjetas de proyecto apuntan a:
   - Chile: `./lalinea/chile/#chile`
   - Chile vs Mundo: `./lalinea/chile/#mundo`
   - Cerezas: `./lalinea/cerezas/`
   - Bombas: `./lalinea/bombas-hormigon/`
3. Footer estándar exacto:
   ```
   La Línea
   Powered by CápsulaData
   Análisis de grandes datos · Entender · Diagnosticar · Predecir
   ¿Quieres este tipo de análisis para tu empresa o proyecto?
   Conéctemos en LinkedIn
   ```
4. Tema oscuro coherente (#0f172a, acentos #60a5fa/#38bdf8).
5. Nav: Proyectos, Contacto, CápsulaData, Servicios.

## Tarea
1. Lee `web/la-linea/index.html`.
2. Verifica que es hub puro, que las tarjetas enlazan bien, que el footer es exacto, que no hay scripts/canvases colgando.
3. Reporta [CRÍTICO/MEDIO/BAJO] + ubicación + corrección sugerida.

## Entrega
Reporte en español, numerado, con severidad y ubicación. No edites.
