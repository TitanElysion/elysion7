from pathlib import Path
import fnmatch
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "libraries.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def matches_pattern(path: Path, patterns):
    """
    Vérifie si le nom ou le chemin du fichier correspond
    à l'un des patterns fournis.
    """
    path_str = str(path)

    for pattern in patterns:
        if fnmatch.fnmatch(path.name, pattern):
            return True

        if fnmatch.fnmatch(path_str, pattern):
            return True

    return False


def should_exclude(path: Path, exclude_patterns):
    """
    Vérifie si un fichier ou l'un de ses dossiers parents
    doit être exclu.
    """
    parts = path.parts

    for part in parts:
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(part, pattern):
                return True

    return matches_pattern(path, exclude_patterns)


def scan_repository(name: str):
    config = load_config()

    if name not in config["libraries"]:
        raise ValueError(f"Library inconnue: {name}")

    library = config["libraries"][name]

    repo_path = BASE_DIR / "data" / "repos" / name

    if not repo_path.exists():
        raise FileNotFoundError(
            f"Repository introuvable: {repo_path}"
        )

    include_patterns = library.get("include", [])
    exclude_patterns = library.get("exclude", [])

    results = []

    for path in repo_path.rglob("*"):

        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_path)

        if should_exclude(relative_path, exclude_patterns):
            continue

        if not matches_pattern(relative_path, include_patterns):
            continue

        results.append({
            "library": name,
            "path": str(relative_path),
            "absolute_path": str(path),
            "size": path.stat().st_size,
        })

    return results


if __name__ == "__main__":
    import sys

    library_name = sys.argv[1] if len(sys.argv) > 1 else "fastapi"

    files = scan_repository(library_name)

    print(f"\nLibrary : {library_name}")
    print(f"Fichiers sélectionnés : {len(files)}")

    total_size = sum(item["size"] for item in files)

    print(f"Taille totale : {total_size / 1024 / 1024:.2f} MB")

    print("\nPremiers fichiers :")

    for item in files[:30]:
        print(f"  {item['path']} ({item['size']} bytes)")
