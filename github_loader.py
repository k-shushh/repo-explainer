import tempfile
from git import Repo


def clone_repo(repo_url):

    temp_dir = tempfile.mkdtemp()

    Repo.clone_from(
        repo_url,
        temp_dir
    )

    return temp_dir