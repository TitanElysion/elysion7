from collections import Counter
from pathlib import Path
import statistics

from ingestion.scanner import scan_repository
from ingestion.parser import parse_file
from ingestion.chunker import chunk_documents
from ingestion.metadata import (
    get_git_metadata,
    get_priority,
)


BASE_DIR = Path(__file__).resolve().parent.parent


def classify_path(path: str) -> str:
    path_lower = path.lower()

    if "/docs/" in path_lower:
        return "documentation"

    if path_lower.startswith("docs/"):
        return "documentation"

    if "/examples/" in path_lower:
        return "example"

    if path_lower.startswith("examples/"):
        return "example"

    if "/test" in path_lower or path_lower.startswith("tests/"):
        return "test"

    suffix = Path(path).suffix.lower()

    if suffix in {
        ".py",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
    }:
        return "source"

    if suffix in {
        ".md",
        ".mdx",
        ".rst",
    }:
        return "documentation"

    return "other"


def main():

    library = "fastapi"

    print("=" * 70)
    print(f"ANALYSE DE {library.upper()}")
    print("=" * 70)

    files = scan_repository(library)
    repo_path = BASE_DIR / "data" / "repos" / library

    git_metadata = get_git_metadata(
    repo_path
)

    print()
    print(f"Fichiers sélectionnés : {len(files)}")

    categories = Counter()

    for file in files:
        category = classify_path(
            file["path"]
        )

        categories[category] += 1

    print()
    print("CATÉGORIES")
    print("-" * 70)

    for category, count in categories.most_common():
        print(
            f"{category:20} : {count}"
        )

    print()
    print("PARSING...")

    documents = []

    for index, file in enumerate(
        files,
        start=1,
    ):

        path = Path(file["absolute_path"])

        relative_path = Path(file["path"])
    
        try:
    
            parsed = parse_file(
            path,
            library=library,
            version=git_metadata["commit_short"],
            )
    
            for document in parsed:

                category = classify_path(
                    file["path"]
                )

                document["path"] = str(
                    relative_path
                )

                document["category"] = category

                document["repository"] = (
                    git_metadata["repository"]
                )

                document["branch"] = (
                    git_metadata["branch"]
                )

                document["commit"] = (
                    git_metadata["commit"]
                )

                document["commit_date"] = (
                    git_metadata["commit_date"]
                )

                document["priority"] = (
                    get_priority(category)
                )

            documents.extend(parsed)

        except Exception as exc:

            print(
                f"[WARN] {file['path']}: {exc}"
            )

        if index % 250 == 0:
            print(
                f"  {index}/{len(files)} fichiers..."
            )

    print()
    print(
        f"Documents générés : {len(documents)}"
    )

    print()
    print("CHUNKING...")

    chunks = chunk_documents(
        documents
    )

    print(
        f"Chunks générés : {len(chunks)}"
    )

    if not chunks:
        print("Aucun chunk.")
        return

    sizes = [
        len(chunk["content"])
        for chunk in chunks
    ]

    print()
    print("STATISTIQUES DES CHUNKS")
    print("-" * 70)

    print(
        f"Minimum : {min(sizes)} caractères"
    )

    print(
        f"Maximum : {max(sizes)} caractères"
    )

    print(
        f"Moyenne : {statistics.mean(sizes):.1f} caractères"
    )

    print(
        f"Médiane : {statistics.median(sizes):.1f} caractères"
    )

    print()
    print("CHUNKS PAR CATÉGORIE")
    print("-" * 70)

    chunk_categories = Counter(
        chunk.get("category", "unknown")
        for chunk in chunks
    )

    for category, count in chunk_categories.most_common():
        percentage = (
            count / len(chunks) * 100
        )

        print(
            f"{category:20} : "
            f"{count:6} "
            f"({percentage:5.1f}%)"
        )

    print()
    print("CHUNKS PAR LANGAGE")
    print("-" * 70)

    languages = Counter(
        chunk["language"]
        for chunk in chunks
    )

    for language, count in languages.most_common():

        percentage = (
            count / len(chunks) * 100
        )

        print(
            f"{language:20} : "
            f"{count:6} "
            f"({percentage:5.1f}%)"
        )

    print()
    print("PETITS CHUNKS")
    print("-" * 70)

    small_chunks = [
        chunk
        for chunk in chunks
        if len(chunk["content"]) < 150
    ]

    print(
        f"< 150 caractères : "
        f"{len(small_chunks)}"
    )

    print()
    print("EXEMPLES DE CHUNKS")
    print("=" * 70)


    for index, chunk in enumerate(
        chunks[:5],
        start=1,
    ):

        print()
        print(
            f"CHUNK {index}"
        )

        print(
            f"Catégorie : {chunk.get('category')}"
        )

        print(
            f"Priority  : {chunk.get('priority')}"
        )

        print(
            f"Version   : {chunk.get('version')}"
        )

        print(
            f"Commit    : {chunk['commit'][:12]}"
        )

        print(
            f"Path      : {chunk['path']}"
        )

        print(
            f"Section   : {chunk['section']}"
        )

        print(
            f"Taille    : {len(chunk['content'])}"
        )

        print()

        print(
            chunk["content"][:400]
        )



if __name__ == "__main__":
    main()
