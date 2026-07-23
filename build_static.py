"""Construye versión estática (GitHub Pages) de La Línea / CápsulaData.
Extrae datos reales a JSON estáticos y genera dist/index.html que los carga
con rutas relativas (sin backend FastAPI).
"""
import json, shutil, os

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

def main():
    os.makedirs(os.path.join(DIST, "data"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "vendor"), exist_ok=True)

    # --- Macro Chile ---
    macro = json.load(open(os.path.join(ROOT, "data", "chile", "bcentral", "chile_macro_monthly.json"), encoding="utf-8"))
    # Mantener solo campos útiles y recortar a 2026
    clean = []
    for r in macro["data"]:
        if r.get("fecha", "") > "2026-12":
            continue
        clean.append(r)
    json.dump({"metadata": macro.get("metadata", {}), "data": clean},
               open(os.path.join(DIST, "data", "chile-macro.json"), "w", encoding="utf-8"),
               ensure_ascii=False)

    # --- Mundo (Banco Mundial) ---
    world = json.load(open(os.path.join(ROOT, "data", "world", "gdp_pcap_wb.json"), encoding="utf-8"))
    # world is dict: country -> {year: value}; wrap in {data: ...} to match gateway
    json.dump({"data": world}, open(os.path.join(DIST, "data", "world-gdp.json"), "w", encoding="utf-8"),
              ensure_ascii=False)

    # --- Población mundial ---
    pop = json.load(open(os.path.join(ROOT, "data", "world", "pop_wb.json"), encoding="utf-8"))
    json.dump({"data": pop}, open(os.path.join(DIST, "data", "world-pop.json"), "w", encoding="utf-8"),
              ensure_ascii=False)

    # --- Chart.js vendored ---
    shutil.copy(os.path.join(ROOT, "web", "vendor", "chart.umd.min.js"),
                os.path.join(DIST, "vendor", "chart.umd.min.js"))

    # --- index.html: copia de la-linea con fetches relativos ---
    src = open(os.path.join(ROOT, "web", "la-linea", "index.html"), encoding="utf-8").read()
    src = src.replace("/api/v1/chile/macro", "./data/chile-macro.json")
    src = src.replace("/api/v1/world/gdp-pcap", "./data/world-gdp.json")
    src = src.replace("/api/v1/world/pop", "./data/world-pop.json")
    # chart vendor también relativo
    src = src.replace('src="/vendor/chart.umd.min.js"', 'src="./vendor/chart.umd.min.js"')
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(src)

    # --- empresa.html (página corporativa CápsulaData) ---
    emp = open(os.path.join(ROOT, "web", "empresa", "index.html"), encoding="utf-8").read()
    emp = emp.replace('src="/vendor/chart.umd.min.js"', 'src="./vendor/chart.umd.min.js"')
    open(os.path.join(DIST, "empresa.html"), "w", encoding="utf-8").write(emp)

    # --- capsula-servicios.html (página de servicios CápsulaData, tema claro) ---
    svc = open(os.path.join(ROOT, "web", "capsula-servicios", "index.html"), encoding="utf-8").read()
    open(os.path.join(DIST, "capsula-servicios.html"), "w", encoding="utf-8").write(svc)

    # --- CNAME opcional (descomenta si tienes dominio) ---
    # open(os.path.join(DIST, "CNAME"), "w").write("capsuladata.com\n")

    print(f"Build estático listo en {DIST}")
    print(f"  - index.html ({len(src)} bytes)")
    print(f"  - empresa.html ({len(emp)} bytes)")
    print(f"  - data/chile-macro.json ({len(clean)} filas)")
    print(f"  - data/world-gdp.json ({len(world)} países)")
    print(f"  - vendor/chart.umd.min.js")

if __name__ == "__main__":
    main()
