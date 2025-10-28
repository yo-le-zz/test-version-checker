import re
import os
import sys
import requests
import subprocess

# Version actuelle
version_actuelle = "V1.3"

# dossier parent
dst = os.path.dirname(os.path.abspath(__file__))

# URL API GitHub (⚠️ pas l'URL HTML)
GITHUB_API_URL = "https://api.github.com/repos/yo-le-zz/test-version-checker/contents/version"

# --- Fonctions utilitaires ---

def extraire_version(v: str):
    """Extrait une version sous forme de tuple d'entiers (ex: V1.3 -> (1, 3))."""
    m = re.match(r"V(\d+(?:\.\d+)*)$", v)
    if not m:
        return ()
    return tuple(map(int, m.group(1).split(".")))

def check_version(version_locale: str, api_url: str, script_mise_a_jour):
    """Compare la version locale avec les versions disponibles sur GitHub."""
    version_num = extraire_version(version_locale)

    # Appel à l'API GitHub
    r = requests.get(api_url)
    if r.status_code != 200:
        print(f"Erreur HTTP {r.status_code} : impossible d’accéder au dépôt GitHub")
        return

    contenus = r.json()
    versions = []

    for item in contenus:
        if item["type"] == "dir" and re.match(r"V\d+(\.\d+)*$", item["name"]):
            versions.append(extraire_version(item["name"]))

    if not versions:
        print("Aucune version trouvée sur GitHub.")
        return

    global derniere_version
    derniere_version = max(versions)
    if derniere_version > version_num:
        new_version = f"V{'.'.join(map(str, derniere_version))}"
        print(f"Nouvelle version disponible : {new_version}")
        print("Passage à la nouvelle version (ne désactivez pas votre ordinateur).")

        # injection de la bonne version dans le script de mise à jour
        script_final = script_mise_a_jour.replace('new_version = ""', f'new_version = "{new_version}"')

        with open(os.path.join(dst, "transistor_version.py"), "w", encoding="utf-8") as f:
            f.write(script_final)

        subprocess.Popen([sys.executable, os.path.join(dst, "transistor_version.py")])
        sys.exit(0)


# --- Script de mise à jour (sera injecté dans transistor_version.py) ---

script_mise_a_jour = r"""
import requests
import os
import shutil
import sys
import time
import psutil

version = "V1.3"
new_version = ""  # sera remplacé par la vraie version avant exécution

dst = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(dst, "main.py")

def get_src_path():
    return os.path.join(dst, new_version, "main.py")

def download_github_folder(owner, repo, path, output_dir="."):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)
    response.raise_for_status()
    items = response.json()

    if not isinstance(items, list):
        print("❌ Le chemin indiqué n'est pas un dossier valide sur GitHub.")
        return

    full_output_dir = os.path.join(dst, output_dir)
    os.makedirs(full_output_dir, exist_ok=True)

    for item in items:
        if item["type"] == "file":
            print(f"Téléchargement de {item['name']}...")
            file_data = requests.get(item["download_url"])
            file_data.raise_for_status()

            file_path = os.path.join(full_output_dir, item["name"])
            print(f"📂 Enregistrement dans : {file_path}")

            with open(file_path, "wb") as f:
                f.write(file_data.content)

        elif item["type"] == "dir":
            sub_dir = os.path.join(full_output_dir, item["name"])
            download_github_folder(owner, repo, item["path"], sub_dir)


            
def stop_old_script(script_name="main.py"):
    current_pid = os.getpid()
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if (
                proc.info["pid"] != current_pid
                and "python" in proc.info["name"].lower()
                and any(script_name in str(arg) for arg in proc.info["cmdline"])
            ):
                print(f"🛑 Arrêt du processus : {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def delete(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

print("🚀 Téléchargement de la nouvelle version...")
download_github_folder(
    owner="yo-le-zz",
    repo="test-version-checker",
    path=f"version/{new_version}",
    output_dir=f"{new_version}"
)

print("🛑 Tentative d'arrêt de l'ancien script...")
stop_old_script("main.py")
time.sleep(1)

if os.path.exists(main_path):
    print("🧹 Suppression de l'ancien main.py...")
    delete(main_path)

src = get_src_path()
print(f"📦 Installation de la nouvelle version depuis {src}...")

if not os.path.exists(src):
    print(f"❌ Fichier introuvable : {src}")
    sys.exit(1)

shutil.move(src, main_path)

print("🗑️ Nettoyage du dossier de version...")
delete(os.path.join(dst, new_version))
delete(os.path.join(dst, "transistor_version.py"))

print("✅ Mise à jour terminée. Relance du script...")
os.execv(sys.executable, [sys.executable, main_path])
"""

# --- Exécution ---
check_version(version_actuelle, GITHUB_API_URL, script_mise_a_jour)

print(f"version : {version_actuelle}")
