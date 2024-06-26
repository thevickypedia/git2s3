import logging
import multiprocessing
import os
import secrets
import shutil
import threading
import warnings
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict

import git
import requests
from git.exc import GitCommandError

from git2s3 import config, s3, squire


class Git2S3:
    # noinspection PyUnresolvedReferences
    """Instantiates Git2S3 object to clone all repos/wiki/gists from GitHub and upload to S3.

    >>> Git2S3

    Keyword Args:
        env_file: Environment configuration.
        logger: Bring your own logger object.
        max_per_page: Maximum number of repos to fetch per page.
    """

    def __init__(
        self,
        env_file: str | os.PathLike = ".env",
        logger: logging.Logger = None,
        max_per_page: int = 100,
    ):
        """Instantiates Git2S3 object to clone all repos/wiki/gists from GitHub and upload to S3."""
        assert 1 <= max_per_page <= 100, "'max_per_page' must be between 1 and 100"
        self.per_page = max_per_page
        self.src_logger = logger
        self.env = squire.env_loader(env_file)
        self.logger = self.src_logger or squire.default_logger(self.env)
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env.git_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.repo = git.Repo()
        self.clone_dir = os.path.join(os.getcwd(), self.env.git_owner)
        profile = self.profile_type()
        if profile == "orgs":
            if config.Fields.gist in self.env.fields:
                warnings.warn(
                    f"Gists are not supported for organizations. Removing {config.Fields.gist!r} from the fields.",
                    UserWarning,
                )
                self.env.fields.remove(config.Fields.gist)
        self.base_url = f"{self.env.git_api_url}/{profile}/{self.env.git_owner}"

    def profile_type(self) -> str:
        """Get the profile type.

        Returns:
            str:
            Returns the profile type.
        """
        try:
            response = self.session.get(
                f"{self.env.git_api_url}/orgs/{self.env.git_owner}"
            )
            assert response.ok
            return "orgs"
        except (requests.RequestException, AssertionError):
            pass
        try:
            response = self.session.get(
                f"{self.env.git_api_url}/users/{self.env.git_owner}"
            )
            assert response.ok
            return "users"
        except (requests.RequestException, AssertionError):
            pass
        raise Exception(
            f"Failed to get the profile type for {self.env.git_owner}. Please check the owner/organization name."
        )

    def get_all(self, field: config.Fields) -> Generator[Dict[str, str]]:
        """Iterate through a target owner/organization to get all available repositories/gists.

        Args:
            field: Field type to clone.

        Yields:
            Generator[Dict[str, str]]:
            Yields a dictionary of each repo's information.
        """
        if field == config.Fields.repo:
            endpoint = f"{self.base_url}/repos"
        elif field == config.Fields.gist:
            endpoint = f"{self.base_url}/gists"
        else:
            # This won't occur programmatically, but here just in case
            raise ValueError(
                f"Invalid field type. Please choose from {config.Fields.repo.value!r} or {config.Fields.gist.value!r}"
            )
        idx = 1
        while True:
            self.logger.debug("Fetching repos from page %d", idx)
            try:
                response = self.session.get(
                    url=endpoint, params={"per_page": self.per_page, "page": idx}
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
                # Yields dictionary from a list
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
                os.path.join(self.clone_dir, field.field, "private", field.name)
            )
        else:
            wiki_dest = str(
                os.path.join(self.clone_dir, field.field, "public", field.name)
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
        self.logger.info("Cloning %s: %s", target.field, target.name)
        if target.private:
            repo_dest = str(
                os.path.join(self.clone_dir, target.field.value, "private", target.name)
            )
        else:
            repo_dest = str(
                os.path.join(self.clone_dir, target.field.value, "public", target.name)
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
            try:
                if target.description:
                    desc_file = os.path.join(
                        repo_dest, f"description_{secrets.token_hex(2)}.txt"
                    )
                    with open(desc_file, "w") as desc:
                        desc.write(target.description)
                        desc.flush()
            except Exception as warning:
                # Adding description file is only an added feature, so no need to fail
                self.logger.warning(warning)
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
                futures[future] = repo.get("name") or repo.get("id")
        for future in as_completed(futures):
            if future.exception():
                self.logger.error(
                    "Thread cloning the %s '%s' received an exception: %s",
                    field,
                    futures[future],
                    future.exception(),
                )

    def start(self) -> None:
        """Start the cloning process."""
        self.logger.info("Starting cloning process...")
        # Both processes run concurrently, calling the same function with different arguments
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
        self.logger.info("Initiating S3 upload process...")
        s3_upload = s3.Uploader(self.env, self.logger)
        s3_upload.trigger()
        self.logger.info("S3 upload process completed.")
