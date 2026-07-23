"""deploy_web.py — Construye la versión estática de La Línea / CápsulaData y la
sube al repo público la-linea-web (GitHub Pages) en github.com/joago99.

Uso:
  python deploy_web.py            # build + push a github (requiere gh auth)
  python deploy_web.py --cname capsuladata.com   # también escribe CNAME

El repo la-linea-web es PUBLICO y solo contiene la web estática (el código
fuente del backend queda privado en latam-finance-api).
"""
import os, shutil, subprocess, sys, json

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
TMP = "C:/tmp/la-linea-web-deploy"
REPO = "joago99/la-linea-web"
REMOTE = f"https://github.com/{REPO}.git"

def run(cmd, cwd=None):
    print(">", cmd)
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr); sys.exit(r.returncode)
    return r.stdout

def build():
    print("== Build estático ==")
    run(f'python "{os.path.join(ROOT, "build_static.py")}"')

def deploy(cname=None):
    print("== Deploy a", REPO, "==")
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    # copiar dist
    for item in os.listdir(DIST):
        s = os.path.join(DIST, item)
        d = os.path.join(TMP, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    # CNAME opcional (dominio propio)
    if cname:
        with open(os.path.join(TMP, "CNAME"), "w") as f:
            f.write(cname.strip() + "\n")
        print("CNAME ->", cname)
    run("git init -q", cwd=TMP)
    run("git add -A", cwd=TMP)
    run('git commit -q -m "deploy: update La Línea / CápsulaData"', cwd=TMP)
    # force push a main
    run(f"git remote add origin {REMOTE}", cwd=TMP)
    run("git branch -M main", cwd=TMP)
    run("git push -f origin main", cwd=TMP)
    print("== Listo. GitHub Pages rebuild en ~1-2 min ==")
    print("URL: https://joago99.github.io/la-linea-web/")
    if cname:
        print("Dominio:", cname, "(recuerda configurar DNS: CNAME -> joago99.github.io)")

if __name__ == "__main__":
    cname = None
    if "--cname" in sys.argv:
        i = sys.argv.index("--cname")
        cname = sys.argv[i+1]
    build()
    deploy(cname)
