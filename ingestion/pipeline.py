"""Construction de chunks enrichis, prêts pour l'indexation."""

from datetime import datetime, timezone
import json
from pathlib import Path
import yaml

from ingestion.chunker import chunk_documents
from ingestion.metadata import get_git_metadata, get_priority
from ingestion.parser import parse_file
from ingestion.scanner import scan_repository


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "libraries.yaml"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def classify_path(path: str) -> str:
    normalized = path.lower()
    if normalized.startswith("docs/") or "/docs/" in normalized:
        return "documentation"
    if normalized.startswith("examples/") or "/examples/" in normalized:
        return "example"
    if normalized.startswith("tests/") or "/test" in normalized:
        return "test"
    if Path(path).suffix.lower() in {".py", ".ts", ".tsx", ".js", ".jsx"}:
        return "source"
    return "documentation" if Path(path).suffix.lower() in {".md", ".mdx", ".rst"} else "other"


def build_chunks(library: str) -> list[dict]:
    """Parse une bibliothèque configurée et retourne des chunks enrichis."""
    repo_path = BASE_DIR / "data" / "repos" / library
    metadata = get_git_metadata(repo_path)
    documents: list[dict] = []

    for file_info in scan_repository(library):
        relative_path = file_info["path"]
        category = classify_path(relative_path)
        for document in parse_file(
            Path(file_info["absolute_path"]),
            library=library,
            version=metadata["version"],
        ):
            document.update(
                path=relative_path,
                category=category,
                priority=get_priority(category),
                repository=metadata["repository"],
                branch=metadata["branch"],
                commit=metadata["commit"],
                commit_date=metadata["commit_date"],
            )
            documents.append(document)

    return chunk_documents(documents)


def generate_manifest(library: str) -> dict:
    """Génère et sauvegarde le manifest JSON pour une bibliothèque."""
    config = load_config()
    if library not in config["libraries"]:
        raise ValueError(f"Library inconnue: {library}")
    lib_cfg = config["libraries"][library]

    repo_path = BASE_DIR / "data" / "repos" / library
    metadata = get_git_metadata(repo_path)

    documents: list[dict] = []
    for file_info in scan_repository(library):
        relative_path = file_info["path"]
        category = classify_path(relative_path)
        for document in parse_file(
            Path(file_info["absolute_path"]),
            library=library,
            version=metadata["version"],
        ):
            document.update(
                path=relative_path,
                category=category,
                priority=get_priority(category),
                repository=metadata["repository"],
                branch=metadata["branch"],
                commit=metadata["commit"],
                commit_date=metadata["commit_date"],
            )
            documents.append(document)

    chunks = chunk_documents(documents)

    manifest = {
        "library": library,
        "name": lib_cfg.get("name", library),
        "repository": metadata["repository"],
        "branch": metadata["branch"],
        "commit": metadata["commit"],
        "commit_short": metadata["commit_short"],
        "commit_date": metadata["commit_date"],
        "version": metadata["version"],
        "version_type": metadata["version_type"],
        "tag": metadata["tag"],
        "nearest_tag": metadata["nearest_tag"],
        "commits_since_tag": metadata["commits_since_tag"],
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "documents": len(documents),
        "chunks": len(chunks),
    }

    output_dir = BASE_DIR / "data" / "documents" / library
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    return manifest
