from pathlib import Path
import re


def detect_language(path: Path) -> str:
    suffix = path.suffix.lower()

    languages = {
        ".md": "markdown",
        ".mdx": "mdx",
        ".rst": "rst",
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".js": "javascript",
        ".jsx": "jsx",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".html": "html",
        ".css": "css",
    }

    return languages.get(suffix, "text")


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )


def clean_markdown(content: str) -> str:
    """
    Nettoyage léger du Markdown.

    On conserve le contenu technique,
    mais on élimine une partie du bruit
    typique des README GitHub.
    """

    # Commentaires HTML
    content = re.sub(
        r"<!--.*?-->",
        "",
        content,
        flags=re.DOTALL,
    )

    # Badges GitHub / images Markdown
    content = re.sub(
        r"!\[[^\]]*\]\([^)]+\)",
        "",
        content,
    )

    # Balises HTML simples
    content = re.sub(
        r"<img[^>]*>",
        "",
        content,
        flags=re.IGNORECASE,
    )

    # Liens HTML autour d'images
    content = re.sub(
        r"<a[^>]*>\s*</a>",
        "",
        content,
        flags=re.IGNORECASE,
    )

    # Réduction des lignes vides
    content = re.sub(
        r"\n{3,}",
        "\n\n",
        content,
    )

    return content.strip()


def extract_title(content: str, path: Path) -> str:

    match = re.search(
        r"^#\s+(.+)$",
        content,
        re.MULTILINE,
    )

    if match:
        return match.group(1).strip()

    lines = content.splitlines()

    if len(lines) >= 2:
        if re.match(
            r"^[=\-~^]+$",
            lines[1].strip(),
        ):
            return lines[0].strip()

    return (
        path.stem
        .replace("_", " ")
        .replace("-", " ")
        .title()
    )


def extract_sections(content: str, language: str):

    if language not in ("markdown", "mdx"):
        return [
            {
                "title": None,
                "content": content.strip(),
            }
        ]

    lines = content.splitlines()

    sections = []

    current_title = None
    current_lines = []

    for line in lines:

        heading = re.match(
            r"^(#{1,6})\s+(.+)$",
            line,
        )

        if heading:

            if current_lines:

                sections.append({
                    "title": current_title,
                    "content": "\n".join(
                        current_lines
                    ).strip(),
                })

            current_title = heading.group(2).strip()
            current_lines = []

        else:
            current_lines.append(line)

    if current_lines:

        sections.append({
            "title": current_title,
            "content": "\n".join(
                current_lines
            ).strip(),
        })

    return [
        section
        for section in sections
        if section["content"]
    ]


def should_ignore_section(title: str | None) -> bool:

    if not title:
        return False

    title_normalized = title.lower().strip()

    ignored = {
        "sponsors",
        "keystone sponsor",
        "gold sponsors",
        "silver sponsors",
        "bronze sponsors",
        "sponsorship",
    }

    return title_normalized in ignored


def parse_file(
    path: Path,
    library: str,
    version: str = "unknown",
):

    content = read_file(path)

    language = detect_language(path)

    if language in ("markdown", "mdx"):
        content = clean_markdown(content)

    title = extract_title(
        content,
        path,
    )

    sections = extract_sections(
        content,
        language,
    )

    documents = []

    for section in sections:

        if should_ignore_section(
            section["title"]
        ):
            continue

        section_content = section[
            "content"
        ].strip()

        # Évite les sections insignifiantes
        if len(section_content) < 50:
            continue

        documents.append({
            "library": library,
            "version": version,
            "source": "github",
            "path": str(path),
            "language": language,
            "title": title,
            "section": section["title"],
            "content": section_content,
        })

    return documents
