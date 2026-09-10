from pathlib import Path

from ingestion.parser import parse_file


if __name__ == "__main__":

    path = Path(
        "data/repos/fastapi/README.md"
    )

    documents = parse_file(
        path,
        library="fastapi",
        version="latest",
    )

    print(
        f"Sections trouvées : {len(documents)}"
    )

    for i, document in enumerate(
        documents[:10],
        start=1,
    ):
        print()
        print("=" * 60)
        print(f"DOCUMENT {i}")
        print("=" * 60)
        print(f"Title   : {document['title']}")
        print(f"Section : {document['section']}")
        print(f"Language: {document['language']}")
        print()
        print(
            document["content"][:500]
        )
