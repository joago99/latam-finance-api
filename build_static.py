"""Construye versión estática (GitHub Pages) de CápsulaData.
Estructura final:
  index.html        -> CápsulaData (empresa, raíz)
  lalinea.html      -> La Línea (dashboard oscuro)
  servicios.html    -> Servicios (tema claro)
  logo.png
  data/
  vendor/
"""
import json, shutil, os

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

def rel(src, path_from_root=False):
    for tok in [("/api/v1/chile/macro", "./data/chile-macro.json"),
                ("/api/v1/world/gdp-pcap", "./data/world-gdp.json"),
                ("/api/v1/world/pop", "./data/world-pop.json"),
                ('src="/vendor/chart.umd.min.js"', 'src="./vendor/chart.umd.min.js"')]:
        src = src.replace(tok[0], tok[1])
    if path_from_root:
        src = src.replace('href="lalinea.html"', 'href="./lalinea.html"')
        src = src.replace('href="servicios.html"', 'href="./servicios.html"')
        src = src.replace('src="logo.png"', 'src="./logo.png"')
    return src

def main():
    os.makedirs(os.path.join(DIST, "data"), exist_ok=True)
    os.makedirs(os.path.join(DIST, 'vendor'), exist_ok=True)
    os.makedirs(os.path.join(DIST, 'cerezas'), exist_ok=True)
    os.makedirs(os.path.join(DIST, 'bombas-hormigon'), exist_ok=True)

    macro = json.load(open(os.path.join(ROOT, "data", "chile", "bcentral", "chile_macro_monthly.json"), encoding="utf-8"))
    clean = [r for r in macro["data"] if r.get("fecha","") <= "2026-12"]
    json.dump({"metadata": macro.get("metadata", {}), "data": clean},
              open(os.path.join(DIST, "data", "chile-macro.json"), "w", encoding="utf-8"), ensure_ascii=False)

    world = json.load(open(os.path.join(ROOT, "data", "world", "gdp_pcap_wb.json"), encoding="utf-8"))
    json.dump({"data": world}, open(os.path.join(DIST, "data", "world-gdp.json"), "w", encoding="utf-8"), ensure_ascii=False)

    pop = json.load(open(os.path.join(ROOT, "data", "world", "pop_wb.json"), encoding="utf-8"))
    json.dump({"data": pop}, open(os.path.join(DIST, "data", "world-pop.json"), "w", encoding="utf-8"), ensure_ascii=False)

    shutil.copy(os.path.join(ROOT, "web", "vendor", "chart.umd.min.js"),
                os.path.join(DIST, "vendor", "chart.umd.min.js"))

    # 1) empresa -> index.html (raíz)
    emp = open(os.path.join(ROOT, "web", "empresa", "index.html"), encoding="utf-8").read()
    emp = rel(emp, path_from_root=True)
    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(emp)

    # 2) la-linea -> lalinea.html
    ll = open(os.path.join(ROOT, "web", "la-linea", "index.html"), encoding="utf-8").read()
    ll = rel(ll)
    # nav interna: enlaces a ../index.html, ../servicios.html
    ll = ll.replace('href="https://joago99.github.io/la-linea-web/empresa.html"', 'href="../index.html"')
    ll = ll.replace('href="https://joago99.github.io/la-linea-web/capsula-servicios.html"', 'href="../servicios.html"')
    ll = ll.replace('href="#contacto"', 'href="../index.html#contacto"')
    open(os.path.join(DIST, "lalinea.html"), "w", encoding="utf-8").write(ll)

    # 3) servicios -> servicios.html  [RETIRADO 2026-07-27: secciones guardadas en web/servicios-bloques-respaldo.html]
    # svc = open(os.path.join(ROOT, "web", "capsula-servicios", "index.html"), encoding="utf-8").read()
    # svc = rel(svc, path_from_root=True)
    # svc = svc.replace('href="lalinea.html"', 'href="./lalinea.html"')
    # svc = svc.replace('href="index.html"', 'href="./index.html"')
    # svc = svc.replace('href="https://joago99.github.io/la-linea-web/empresa.html"', 'href="./index.html"')
    # svc = svc.replace('href="https://joago99.github.io/la-linea-web/capsula-servicios.html"', 'href="./servicios.html"')
    # open(os.path.join(DIST, "servicios.html"), "w", encoding="utf-8").write(svc)
    # logo: copiar el logo definitivo del usuario (web/logo.png) a dist
    logo = os.path.join(ROOT, "web", "logo.png")
    if os.path.exists(logo):
        shutil.copy(logo, os.path.join(DIST, "logo.png"))

    # --- Datos de proyectos ---
    for fname in ["cerezas-export.json"]:
        src = os.path.join(ROOT, "data", fname)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(DIST, "data", fname))

    print(f"Build estático en {DIST}")
    print(f"  - index.html (CápsulaData empresa)")
    print(f"  - lalinea.html (La Línea hub)")
    print(f"  - servicios.html (Servicios)")

    # 4) chile -> lalinea/chile/index.html
    ch = open(os.path.join(ROOT, "web", "chile", "index.html"), encoding="utf-8").read()
    ch_dir = os.path.join(DIST, "lalinea", "chile")
    os.makedirs(ch_dir, exist_ok=True)
    ch = ch.replace('../../vendor/chart.umd.min.js', '../../vendor/chart.umd.min.js')
    ch = ch.replace('../../data/chile-macro.json', '../../data/chile-macro.json')
    ch = ch.replace('../../data/world-gdp.json', '../../data/world-gdp.json')
    ch = ch.replace('../../data/world-pop.json', '../../data/world-pop.json')
    open(os.path.join(ch_dir, "index.html"), "w", encoding="utf-8").write(ch)

    # 5) cerezas -> lalinea/cerezas/index.html
    cz = open(os.path.join(ROOT, "web", "cerezas", "index.html"), encoding="utf-8").read()
    cz_dir = os.path.join(DIST, "lalinea", "cerezas")
    os.makedirs(cz_dir, exist_ok=True)
    cz = cz.replace('../../vendor/chart.umd.min.js', '../../vendor/chart.umd.min.js')
    cz = cz.replace('../../data/cerezas-export.json', '../../data/cerezas-export.json')
    open(os.path.join(cz_dir, "index.html"), "w", encoding="utf-8").write(cz)

    # 6) bombas-hormigon -> lalinea/bombas-hormigon/index.html
    bh = open(os.path.join(ROOT, "web", "bombas-hormigon", "index.html"), encoding="utf-8").read()
    bh_dir = os.path.join(DIST, "lalinea", "bombas-hormigon")
    os.makedirs(bh_dir, exist_ok=True)
    bh = bh.replace('../../vendor/chart.umd.min.js', '../../vendor/chart.umd.min.js')
    open(os.path.join(bh_dir, "index.html"), "w", encoding="utf-8").write(bh)

    print(f"  - lalinea/chile/index.html")
    print(f"  - lalinea/cerezas/index.html")
    print(f"  - lalinea/bombas-hormigon/index.html")
    print(f"  - logo.png")
    print(f"  - data/chile-macro.json ({len(clean)} filas)")
    print(f"  - data/world-gdp.json ({len(world)} países)")
    print(f"  - vendor/chart.umd.min.js")

if __name__ == "__main__":
    main()
