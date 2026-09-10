from ingestion.github import clone_repository


if __name__ == "__main__":
    clone_repository(
        name="fastapi",
        url="https://github.com/fastapi/fastapi.git",
        branch="master",
    )
