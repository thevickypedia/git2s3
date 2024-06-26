import logging
import os
import secrets
import shutil
import threading
import warnings
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing.pool import ThreadPool
from typing import Dict
from urllib.parse import urlsplit, urlunsplit

import git
import requests
from git.exc import GitCommandError
from pydantic import HttpUrl

from git2s3 import config, exc, s3, squire


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
        self.env = squire.env_loader(env_file)
        self.logger = logger or squire.default_logger(self.env)
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.env.git_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.repo = git.Repo()
        self.origin = self.repo.remote()
        self.clone_dir = os.path.join(os.getcwd(), self.env.git_owner)
        warnings.simplefilter("always", exc.DirectoryExists)
        warnings.simplefilter("always", exc.UnsupportedSource)
        if os.path.isdir(self.clone_dir) and os.listdir(self.clone_dir):
            warnings.warn(
                "The clone directory is not empty. Deleting the contents to avoid conflicts.",
                exc.DirectoryExists,
            )
            shutil.rmtree(self.clone_dir)
        profile = self.profile_type()
        if profile == "orgs":
            if config.SourceControl.gist in self.env.source:
                warnings.warn(
                    f"Gists are not supported for organizations. Removing {config.SourceControl.gist!r} from source.",
                    exc.UnsupportedSource,
                )
                self.env.source.remove(config.SourceControl.gist)
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
        raise exc.InvalidOwner(
            f"Failed to get the profile type for {self.env.git_owner}. Please check the owner/organization name."
        )

    def get_all(self, source: config.SourceControl) -> Generator[Dict[str, str]]:
        """Iterate through a target owner/organization to get all available repositories/gists.

        Args:
            source: Source type to clone.

        Yields:
            Generator[Dict[str, str]]:
            Yields a dictionary of each repo's information.
        """
        if source == config.SourceControl.repo:
            endpoint = f"{self.base_url}/repos"
        elif source == config.SourceControl.gist:
            endpoint = f"{self.base_url}/gists"
        else:
            # This won't occur programmatically, but here just in case
            raise exc.InvalidSource(
                f"Invalid field type. Please choose from {config.SourceControl.repo!r} or {config.SourceControl.gist!r}"
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
                if idx == 1:
                    raise exc.GitHubAPIError(
                        f"Failed to fetch {source.value}s from {self.env.git_owner!r}."
                    )
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

    def set_pat(self, url: str | HttpUrl) -> None:
        """Creates an authenticated URL by updating the netloc, and sets that as the origin URL.

        Args:
            url: Takes the repository/gist/wiki URL as input.

        See Also:
            - This step is not required for:
                - Public repositories/gists/wiki
                -
        """
        url_split = urlsplit(str(url))
        authed_netloc = f"{self.env.git_token}@{url_split.netloc}"
        joined = urlunsplit(
            (
                url_split.scheme,
                authed_netloc,
                url_split.path,
                url_split.query,
                url_split.fragment,
            )
        )
        self.origin.config_writer.set("url", joined)
        self.origin.config_writer.release()

    def clone_wiki(self, datastore: config.DataStore) -> None:
        """Clone all the wikis from the repository.

        Args:
            datastore: DataStore model to store repository/gist information.
        """
        datastore.source = config.SourceControl.wiki.value
        self.logger.debug("Cloning wiki for %s", datastore.name)
        wiki_url = str(datastore.clone_url).replace(".git", ".wiki.git")
        if datastore.private:
            wiki_dest = str(
                os.path.join(
                    self.clone_dir, datastore.source, "private", datastore.name
                )
            )
        else:
            wiki_dest = str(
                os.path.join(self.clone_dir, datastore.source, "public", datastore.name)
            )
        if not os.path.isdir(wiki_dest):
            os.makedirs(wiki_dest)
        try:
            self.set_pat(wiki_url)
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
        datastore = squire.source_detector(repo, self.env)
        self.logger.info("Cloning %s: %s", datastore.source, datastore.name)
        if datastore.private:
            repo_dest = str(
                os.path.join(
                    self.clone_dir, datastore.source.value, "private", datastore.name
                )
            )
        else:
            repo_dest = str(
                os.path.join(
                    self.clone_dir, datastore.source.value, "public", datastore.name
                )
            )
        # only repos have this field anyway
        if config.SourceControl.wiki in self.env.source and repo.get("has_wiki"):
            # run as daemon and don't care about the output for wiki
            # 'has_wiki' flag will always be true even if there are no files to clone
            threading.Thread(
                target=self.clone_wiki, args=(datastore,), daemon=True
            ).start()
        if not os.path.isdir(repo_dest):
            os.makedirs(repo_dest)
        try:
            self.set_pat(datastore.clone_url)
            self.repo.clone_from(datastore.clone_url, repo_dest)
            try:
                if datastore.description:
                    desc_file = os.path.join(
                        repo_dest, f"description_{secrets.token_hex(2)}.txt"
                    )
                    with open(desc_file, "w") as desc:
                        desc.write(datastore.description)
                        desc.flush()
            except Exception as warning:
                # Adding description file is only an added feature, so no need to fail
                self.logger.warning(warning)
            shutil.make_archive(repo_dest, "zip", repo_dest)
            if os.path.isfile(f"{repo_dest}.zip"):
                shutil.rmtree(repo_dest)
            else:
                self.logger.error("Failed to create a zip file for %s", datastore.name)
                raise exc.ArchiveError(
                    f"Failed to create a zip file for {datastore.name!r}"
                )
        except GitCommandError as error:
            msg = error.stderr or error.stdout or ""
            msg = msg.strip().replace("\n", "").replace("'", "").replace('"', "")
            self.logger.error(msg)
            # Raise an exception to indicate that the thread failed
            raise exc.Git2S3Error(msg)

    def cloner(self, source: config.SourceControl) -> bool:
        """Clones all the repos/gists concurrently.

        Args:
            source: Source type to clone.

        See Also:
            - Clones all the repos/gists concurrently using ThreadPoolExecutor.
            - GitHub doesn't have a rate limit for cloning, so multi-threading is safe.
            - This makes it depend on Git installed on the host machine.

        References:
            https://github.com/orgs/community/discussions/44515

        Returns:
            bool:
            Returns a boolean flag to indicate if any of the threads failed.
        """
        futures = {}
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for repo in self.get_all(source):
                identifier = repo.get("name") or repo.get("id")
                if identifier.lower() in self.env.git_ignore:
                    self.logger.info("Skipping %s: '%s'", source, identifier)
                    continue
                future = executor.submit(self.worker, repo)
                futures[future] = identifier
        return_flag = True
        for future in as_completed(futures):
            if future.exception():
                self.logger.error(
                    "Thread cloning the %s '%s' received an exception: %s",
                    source,
                    futures[future],
                    future.exception(),
                )
                return_flag = False
        return return_flag

    def start(self) -> None:
        """Start the cloning process and upload to S3 once cloning completes successfully."""
        self.logger.info("Starting cloning process...")
        # Both processes run concurrently, calling the same function with different arguments
        processes = [
            ThreadPool(processes=1).apply_async(
                self.cloner, args=(config.SourceControl.repo,)
            )
        ]
        if config.SourceControl.gist in self.env.source:
            processes.append(
                ThreadPool(processes=1).apply_async(
                    self.cloner, args=(config.SourceControl.gist,)
                )
            )
        if not all(process.get() for process in processes):
            self.logger.error(
                "Cloning process did not complete successfully. Skipping S3 backup."
            )
            return
        self.logger.info("Cloning process completed.")
        if squire.check_file_presence(self.clone_dir):
            self.logger.info("Initiating S3 upload process...")
            s3_upload = s3.Uploader(self.env, self.logger)
            s3_upload.trigger()
            self.logger.info("S3 upload process completed.")
        else:
            self.logger.warning("No files found for S3 upload process.")
