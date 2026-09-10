from pathlib import Path
import shutil

from git import Repo


BASE_DIR = Path(__file__).resolve().parent.parent
REPOS_DIR = BASE_DIR / "data" / "repos"


def clone_repository(name: str, url: str, branch: str = "main") -> Path:
    destination = REPOS_DIR / name

    if destination.exists():
        print(f"[INFO] Repository already exists: {destination}")
        return destination

    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Cloning {url}")
    print(f"[INFO] Destination: {destination}")

    try:
        Repo.clone_from(
            url,
            destination,
            branch=branch,
            depth=1,
        )
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)

        raise

    print("[OK] Repository cloned")

    return destination
