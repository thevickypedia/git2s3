import os
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

import git
import requests
from git.exc import GitCommandError

from git2s3 import config, models


class Git2S3:
    def __init__(self, **kwargs):
        self.env = models.EnvConfig(**kwargs)
        self.logger = kwargs.get("logger", config.default_logger(self.env))
        self.repo = git.Repo()
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env.git_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def get_all_repos(self) -> Generator[Dict[str, str]]:
        """Iterate through a target owner/organization to get all available repositories.

        Yields:
            Generator[Dict[str, str]]:
            Yields a dictionary of each repo's information.
        """
        idx = 1
        while True:
            self.logger.debug("Fetching repos from page %d", idx)
            try:
                response = self.session.get(
                    url=f"{self.env.git_api_url}orgs/{self.env.git_owner}/repos?per_page=1&page={idx}"
                )
            except (requests.RequestException, AssertionError):
                break
            json_response = response.json()
            if json_response:
                self.logger.debug(
                    "Repositories in page %d: %d", idx, len(json_response)
                )
                yield from json_response
                idx += 1
            else:
                self.logger.debug("No repos found in page: %d, ending loop.", idx)
                break

    def worker(self, repo: Dict[str, str]):
        """Clones repository from GitHub.

        Args:
            repo: Repository information as JSON payload.
        """
        self.logger.info("Cloning %s", repo.get("name"))
        repo_dest = os.path.join(self.env.clone_dir, repo.get("name"))
        if not os.path.isdir(repo_dest):
            os.makedirs(repo_dest)
        try:
            self.repo.clone_from(repo.get("clone_url"), str(repo_dest))
        except GitCommandError as error:
            msg = error.stderr or error.stdout or ""
            msg = msg.strip().replace("\n", "").replace("'", "").replace('"', "")
            self.logger.error(msg)
            # Raise an exception to indicate that the thread failed
            raise Exception(msg)

    def cloner(self):
        """Clones all the repos concurrently.

        References:
            https://github.com/orgs/community/discussions/44515
        """
        futures = {}
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for repo in self.get_all_repos():
                future = executor.submit(self.worker, repo)
                futures[future] = repo.get("name")
        for future in as_completed(futures):
            if future.exception():
                self.logger.error(
                    "Thread processing for '%s' received an exception: %s",
                    futures[future],
                    future.exception(),
                )


if __name__ == "__main__":
    Git2S3().cloner()
