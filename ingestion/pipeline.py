"""Construction de chunks enrichis, prêts pour l'indexation."""

from pathlib import Path

from ingestion.chunker import chunk_documents
from ingestion.metadata import get_git_metadata, get_priority
from ingestion.parser import parse_file
from ingestion.scanner import scan_repository


BASE_DIR = Path(__file__).resolve().parent.parent


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
