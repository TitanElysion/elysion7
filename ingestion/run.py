"""Script d'automatisation pour cloner et indexer les bibliothèques configurées."""

import argparse
import sys
from pathlib import Path
import yaml

from ingestion.github import clone_repository
from ingestion.indexer import index_library

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "libraries.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pipeline(library_name: str | None = None, all_libraries: bool = False, qdrant_url: str | None = None):
    config = load_config()
    libraries = config.get("libraries", {})

    if all_libraries:
        targets = list(libraries.keys())
    elif library_name:
        if library_name not in libraries:
            print(f"[ERROR] Bibliothèque inconnue dans la configuration : {library_name}")
            sys.exit(1)
        targets = [library_name]
    else:
        print("[ERROR] Veuillez spécifier une bibliothèque ou utiliser --all.")
        sys.exit(1)

    print(f"[INFO] Bibliothèques cibles : {targets}")

    for lib_key in targets:
        lib_cfg = libraries[lib_key]
        repo_url = lib_cfg["repository"]
        branch = lib_cfg.get("branch", "main")

        print(f"\n--- Traitement de {lib_key} ({repo_url}, branche: {branch}) ---")
        try:
            clone_repository(lib_key, repo_url, branch=branch)
        except Exception as e:
            print(f"[ERROR] Échec du clonage pour {lib_key}: {e}")
            continue

        print(f"[INFO] Lancement de l'indexation pour {lib_key}...")
        try:
            chunks_count = index_library(lib_key, qdrant_url=qdrant_url)
            print(f"[OK] {chunks_count} chunks indexés avec succès pour {lib_key}.")
        except Exception as e:
            print(f"[ERROR] Échec de l'indexation pour {lib_key}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatisation du clonage et de l'indexation des bibliothèques.")
    parser.add_argument("library", nargs="?", help="Nom de la bibliothèque à indexer (ex: fastapi)")
    parser.add_argument("--all", action="store_true", help="Indexer toutes les bibliothèques configurées")
    parser.add_argument("--qdrant-url", default=None, help="URL de l'instance Qdrant")

    args = parser.parse_args()
    run_pipeline(library_name=args.library, all_libraries=args.all, qdrant_url=args.qdrant_url)
