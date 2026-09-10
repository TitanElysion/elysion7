# from pathlib import Path
# from git import Repo


# def get_git_metadata(repo_path: Path) -> dict:
#     """
#     Récupère les métadonnées Git du repository.
#     """

#     repo = Repo(repo_path)

#     commit = repo.head.commit

#     return {
#         "repository": next(
#             repo.remote("origin").urls
#         ),
#         "branch": repo.active_branch.name,
#         "commit": commit.hexsha,
#         "commit_short": commit.hexsha[:12],
#         "commit_date": commit.committed_datetime.isoformat(),
#     }


# def get_priority(category: str) -> int:
#     """
#     Définit la priorité documentaire.
#     """

#     priorities = {
#         "documentation": 3,
#         "example": 2,
#         "source": 1,
#         "test": 0,
#     }

#     return priorities.get(category, 0)

from pathlib import Path
from git import Repo, GitCommandError


def get_git_metadata(repo_path: Path) -> dict:
    repo = Repo(repo_path)

    commit = repo.head.commit
    commit_sha = commit.hexsha

    # Branche courante
    try:
        branch = repo.active_branch.name
    except TypeError:
        branch = "detached"

    # Tag(s) pointant exactement sur le commit
    exact_tags = [
        tag.name
        for tag in repo.tags
        if tag.commit.hexsha == commit_sha
    ]

    # Dernier tag accessible depuis le commit
    nearest_tag = None
    commits_since_tag = None

    try:
        description = repo.git.describe(
            "--tags",
            "--always",
            "--long",
            commit_sha,
        )

        # Exemple :
        # 0.141.1-106-g50113da16fec
        parts = description.rsplit("-", 2)

        if len(parts) == 3 and parts[1].isdigit():
            nearest_tag = parts[0]
            commits_since_tag = int(parts[1])

    except GitCommandError:
        pass

    # Détermination de la version
    if exact_tags:
        version = exact_tags[0]
        version_type = "stable"

    elif nearest_tag:
        version = f"{nearest_tag}+{commits_since_tag}"
        version_type = "development"

    else:
        version = "unknown"
        version_type = "unknown"

    return {
        "repository": next(repo.remote("origin").urls),
        "branch": branch,
        "commit": commit_sha,
        "commit_short": commit_sha[:12],
        "commit_date": commit.committed_datetime.isoformat(),

        "version": version,
        "version_type": version_type,
        "tag": exact_tags[0] if exact_tags else None,
        "nearest_tag": nearest_tag,
        "commits_since_tag": commits_since_tag,
    }


def get_priority(category: str) -> int:
    priorities = {
        "documentation": 3,
        "example": 2,
        "source": 1,
        "test": 0,
    }

    return priorities.get(category, 0)