import logging
import multiprocessing
import os
import shutil
import threading
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict

import git
import requests
from git.exc import GitCommandError

from git2s3 import config, squire


class Git2S3:
    """Instantiates Git2S3 object to clone all repos/wiki/gists from GitHub and upload to S3.

    >>> Git2S3

    """

    def __init__(
        self,
        env_file: str | os.PathLike = ".env",
        logger: logging.Logger = None,
        max_per_page: int = 100,
    ):
        """Loads all the necessary args, creates a connection to GitHub API and S3 to perform the backup.

        Keyword Args:
            env_file: Environment configuration.
            logger: Bring your own logger object.
            max_per_page: Maximum number of repos to fetch per page.
        """
        assert 1 <= max_per_page <= 100, "'max_per_page' must be between 1 and 100"
        self.per_page = max_per_page
        self.src_logger = logger
        self.env = squire.env_loader(env_file)
        self.logger = self.src_logger or squire.default_logger(self.env)
        self.repo = git.Repo()
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env.git_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def get_all(self, field: config.Fields) -> Generator[Dict[str, str]]:
        """Iterate through a target owner/organization to get all available repositories/gists.

        Args:
            field: Field type to clone.

        Yields:
            Generator[Dict[str, str]]:
            Yields a dictionary of each repo's information.
        """
        if not self.env.gist_owner:
            self.env.gist_owner = self.env.git_owner
        if field == config.Fields.repo:
            base_url = f"{self.env.git_api_url}orgs/{self.env.git_owner}/repos"
        elif field == config.Fields.gist:
            base_url = f"{self.env.git_api_url}users/{self.env.gist_owner}/gists"
        else:
            raise ValueError(
                f"Invalid field type. Please choose from {config.Fields.repo.value!r} or {config.Fields.gist.value!r}"
            )
        idx = 1
        while True:
            self.logger.debug("Fetching repos from page %d", idx)
            try:
                response = self.session.get(
                    url=f"{base_url}?per_page={self.per_page}&page={idx}"
                )
                assert response.ok, response.text
            except (requests.RequestException, AssertionError) as error:
                self.logger.error("Failed to fetch repos on page: %d - %s", idx, error)
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

    def clone_wiki(self, field: config.Field) -> None:
        """Clone all the wikis from the repository.

        Args:
            field: Field model to store repository/gist information.
        """
        field.field = config.Fields.wiki.value
        self.logger.debug("Cloning wiki for %s", field.name)
        wiki_url = str(field.clone_url).replace(".git", ".wiki.git")
        if field.private:
            wiki_dest = str(
                os.path.join(self.env.clone_dir, field.field, "private", field.name)
            )
        else:
            wiki_dest = str(
                os.path.join(self.env.clone_dir, field.field, "public", field.name)
            )
        if not os.path.isdir(wiki_dest):
            os.makedirs(wiki_dest)
        try:
            self.repo.clone_from(wiki_url, wiki_dest)
        except GitCommandError as error:
            msg = error.stderr or error.stdout or ""
            msg = msg.strip().replace("\n", "").replace("'", "").replace('"', "")
            self.logger.debug(msg)
            shutil.rmtree(wiki_dest)

    def worker(self, repo: Dict[str, str]) -> None:
        """Clones repository/gist/wiki from GitHub.

        Args:
            repo: Repository information as JSON payload.

        Raises:
            Exception:
            If the thread fails to clone the repository.
        """
        target = squire.field_detector(repo, self.env)
        self.logger.info("Cloning %s", target.name)
        if target.private:
            repo_dest = str(
                os.path.join(
                    self.env.clone_dir, target.field.value, "private", target.name
                )
            )
        else:
            repo_dest = str(
                os.path.join(
                    self.env.clone_dir, target.field.value, "public", target.name
                )
            )
        # only repos have this field anyway
        if config.Fields.wiki in self.env.fields and repo.get("has_wiki"):
            # run as daemon and don't care about the output
            threading.Thread(
                target=self.clone_wiki, args=(target,), daemon=True
            ).start()
        if not os.path.isdir(repo_dest):
            os.makedirs(repo_dest)
        try:
            self.repo.clone_from(target.clone_url, repo_dest)
            with open(os.path.join(repo_dest, "description.txt"), "w") as desc:
                desc.write(target.description)
                desc.flush()
            shutil.make_archive(repo_dest, "zip", repo_dest)
            if os.path.isfile(f"{repo_dest}.zip"):
                shutil.rmtree(repo_dest)
            else:
                self.logger.error("Failed to create a zip file for %s", target.name)
                raise Exception(f"Failed to create a zip file for {target.name}")
        except GitCommandError as error:
            msg = error.stderr or error.stdout or ""
            msg = msg.strip().replace("\n", "").replace("'", "").replace('"', "")
            self.logger.error(msg)
            # Raise an exception to indicate that the thread failed
            raise Exception(msg)

    def cloner(self, func: Callable, field: str) -> None:
        """Clones all the repos/gists concurrently.

        Args:
            func: Function to get all repos/gists.
            field: Field type to clone.

        References:
            https://github.com/orgs/community/discussions/44515
        """
        # Reload logger for child process
        self.logger = self.src_logger or squire.default_logger(self.env)
        futures = {}
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for repo in func(field):
                future = executor.submit(self.worker, repo)
                futures[future] = repo.get("name")
        for future in as_completed(futures):
            if future.exception():
                self.logger.error(
                    "Thread processing for '%s' received an exception: %s",
                    futures[future],
                    future.exception(),
                )

    def start(self) -> None:
        """Start the cloning process."""
        self.logger.info("Starting cloning process...")
        processes = [
            multiprocessing.Process(
                target=self.cloner,
                args=(
                    self.get_all,
                    config.Fields.repo,
                ),
            )
        ]
        if config.Fields.gist in self.env.fields:
            processes.append(
                multiprocessing.Process(
                    target=self.cloner,
                    args=(
                        self.get_all,
                        config.Fields.gist,
                    ),
                )
            )
        for process in processes:
            process.start()
        for process in processes:
            process.join()
        self.logger.info("Cloning process completed.")
