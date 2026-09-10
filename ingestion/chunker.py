import re


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 150
MIN_CHUNK_SIZE = 80

def clean_text(text: str) -> str:
    """
    Nettoie légèrement le texte sans détruire
    la structure utile aux développeurs.
    """

    # Supprime les espaces en fin de ligne
    text = re.sub(r"[ \t]+\n", "\n", text)

    # Réduit les lignes vides multiples
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
):
    """
    Découpe un texte en morceaux avec chevauchement.

    On essaie de couper d'abord sur :
    - paragraphes
    - lignes
    - espaces
    """

    text = clean_text(text)

    if not text:
        return []

    if len(text) <= chunk_size:
        if len(text) >= MIN_CHUNK_SIZE:
            return [text]
    return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        if end < text_length:

            # On préfère couper sur un paragraphe
            boundary = text.rfind(
                "\n\n",
                start,
                end,
            )

            if boundary > start + chunk_size // 2:
                end = boundary

            else:
                # Sinon sur une ligne
                boundary = text.rfind(
                    "\n",
                    start,
                    end,
                )

                if boundary > start + chunk_size // 2:
                    end = boundary

                else:
                    # Dernier recours : espace
                    boundary = text.rfind(
                        " ",
                        start,
                        end,
                    )

                    if boundary > start + chunk_size // 2:
                        end = boundary

        chunk = text[start:end].strip()

        if len(chunk) >= MIN_CHUNK_SIZE:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(
            end - overlap,
            start + 1,
        )

    return chunks


def chunk_documents(
    documents,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
):
    """
    Transforme les documents du parser en chunks
    prêts pour l'indexation.
    """

    results = []

    for document in documents:

        content = document["content"]

        chunks = split_text(
            content,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, chunk in enumerate(
            chunks
        ):

            results.append({
                "library": document["library"],
                "version": document["version"],
                "repository": document["repository"],
                "branch": document["branch"],
                "commit": document["commit"],
                "commit_date": document["commit_date"],
                "source": document["source"],
                "path": document["path"],
                "language": document["language"],
                "title": document["title"],
                "section": document["section"],
                "category": document.get(
                    "category",
                    "unknown",
                ),
                "priority": document.get(
                    "priority",
                    0,
                ),
                "chunk_index": index,
                "content": chunk,
})

    return results
