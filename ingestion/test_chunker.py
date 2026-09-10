from pathlib import Path

from ingestion.parser import parse_file
from ingestion.chunker import chunk_documents


if __name__ == "__main__":

    path = Path(
        "data/repos/fastapi/README.md"
    )

    documents = parse_file(
        path,
        library="fastapi",
        version="latest",
    )

    chunks = chunk_documents(documents)

    print(
        f"Documents : {len(documents)}"
    )

    print(
        f"Chunks    : {len(chunks)}"
    )

    print()

    for i, chunk in enumerate(
        chunks[:10],
        start=1,
    ):

        print("=" * 70)
        print(f"CHUNK {i}")
        print("=" * 70)

        print(
            f"Library : {chunk['library']}"
        )

        print(
            f"Path    : {chunk['path']}"
        )

        print(
            f"Section : {chunk['section']}"
        )

        print(
            f"Language: {chunk['language']}"
        )

        print(
            f"Size    : {len(chunk['content'])} caractères"
        )

        print()

        print(
            chunk["content"][:700]
        )

        print()
