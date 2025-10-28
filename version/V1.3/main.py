import re
import os
import sys
import requests
import subprocess

# Version actuelle
version_actuelle = "V1.0"

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

    derniere_version = max(versions)
    if derniere_version > version_num:
        print(f"Nouvelle version disponible : V{'.'.join(map(str, derniere_version))}")
        print("Passage a la nouvelle version (ne desactiver pas votre ordinateur).")
        with open(os.path.join(dst, "transistor_version.py"), "w", encoding="utf-8") as f:
            f.write(script_mise_a_jour)
        subprocess.Popen([sys.executable, os.path.join(dst, "transistor_version.py")])
        sys.exit(0)
    else:
        pass

script_mise_a_jour = r"""
import requests
import os
import shutil

version = "V1.3"
dst = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(dst, version, "main.py")

def download_github_folder(owner, repo, path, output_dir="."):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)
    response.raise_for_status()
    items = response.json()

    if not isinstance(items, list):
        print("❌ Le chemin indiqué n'est pas un dossier valide sur GitHub.")
        return

    os.makedirs(output_dir, exist_ok=True)

    for item in items:
        if item["type"] == "file":
            print(f"Téléchargement de {item['name']}...")
            file_data = requests.get(item["download_url"])
            file_data.raise_for_status()

            with open(os.path.join(output_dir, item["name"]), "wb") as f:
                f.write(file_data.content)
        elif item["type"] == "dir":
            sub_dir = os.path.join(output_dir, item["name"])
            download_github_folder(owner, repo, item["path"], sub_dir)

def delete(fichier):
    if os.path.exists(fichier):
        os.remove(fichier)

print("🚀 Téléchargement de la nouvelle version...")
download_github_folder(
    owner="yo-le-zz",
    repo="test-version-checker",
    path=f"version/{version}",
    output_dir=f"{version}"
)

print("🧹 Suppression de l’ancienne version...")
delete(os.path.join(dst, "main.py"))

print("📦 Déplacement de la nouvelle version...")
shutil.move(src, os.path.join(dst, "main.py"))

print("✅ Mise à jour terminée.")
delete(os.path.join(dst, "transistor_version.py"))
"""

# --- Exécution ---
check_version(version_actuelle, GITHUB_API_URL, script_mise_a_jour)
print(f"tu a reussie!!!! on est sur la version : {version_actuelle})
