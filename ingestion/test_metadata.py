from pathlib import Path

from ingestion.metadata import (
    get_git_metadata,
    get_priority,
)


BASE_DIR = Path(__file__).resolve().parent.parent

repo_path = BASE_DIR / "data" / "repos" / "fastapi"

metadata = get_git_metadata(repo_path)

print("=" * 70)
print("GIT METADATA")
print("=" * 70)

for key, value in metadata.items():
    print(f"{key:20} : {value}")

print()
print("=" * 70)
print("PRIORITIES")
print("=" * 70)

for category in [
    "documentation",
    "example",
    "source",
    "test",
]:
    print(
        f"{category:20} : "
        f"{get_priority(category)}"
    )
