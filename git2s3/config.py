import os
import shutil
import sys
import warnings

from pydantic import DirectoryPath, HttpUrl, field_validator
from pydantic_settings import BaseSettings

if sys.version_info.minor > 10:
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Override for python 3.10 due to lack of StrEnum."""


class LogOptions(StrEnum):
    """Available log options for default logger.

    >>> LogOptions

    """

    stdout: str = "stdout"
    file: str = "file"


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic``.

    >>> EnvConfig

    Notes:
        - **git_api_url** - GitHub API endpoint to fetch all repos within an organization or owner.
        - **git_owner** - GitHub owner or organization name.
        - **git_token** - GitHub token to get ALL repos (including private).
        - **include_gist** - Includes Gists in the backup.
        - **zipper** - Downloads and uploads as tar/zip files to S3.
        - **clone_dir** - Backup location to store the files locally.
        - **debug** - Boolean flag to enable debug level logging. Does not apply when custom logger is used.
        - **log** - Log options to log to a ``file`` or ``stdout``. Does not apply when custom logger is used.
        - **aws_profile_name** - AWS profile name. Uses the CLI config value ``AWS_DEFAULT_PROFILE`` by default.
        - **aws_access_key_id** - AWS access key ID. Uses the CLI config value ``AWS_ACCESS_KEY_ID`` by default.
        - **aws_secret_access_key** - AWS secret key. Uses the CLI config value ``AWS_SECRET_ACCESS_KEY`` by default.
        - **aws_region_name** - S3 bucket's region. Uses the CLI config value ``AWS_DEFAULT_REGION`` by default.
    """

    git_api_url: HttpUrl = "https://api.github.com"
    git_owner: str | None = None
    git_token: str | None = None
    include_gist: bool = False  # todo: yet to be implemented
    zipper: bool = False  # todo: yet to be implemented, use GH API to download zipped version (include branches)
    clone_dir: DirectoryPath = os.path.join(os.getcwd(), "backup")

    debug: bool = False
    log: LogOptions = LogOptions.stdout

    aws_profile_name: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region_name: str | None = None
    aws_bucket_name: str | None = None

    @field_validator("clone_dir", mode="before", check_fields=True)
    def parse_clone_dir(cls, value: str) -> DirectoryPath:
        """Validate clone_dir to check if it is potential path."""
        if os.path.isdir(value):
            if os.listdir(value):
                # Re-creates the backup directory if it already exists and is not empty
                warnings.simplefilter("always", ResourceWarning)
                warnings.warn(
                    f"Directory {value!r} is not empty, cleaning up...", ResourceWarning
                )
                shutil.rmtree(value)
                os.makedirs(value)
            return value
        if os.path.isdir(os.path.dirname(value)):
            os.makedirs(value)
            return value
        raise ValueError(f"{value!r} is neither a valid path, nor a potential path")

    class Config:
        """Environment variables configuration."""

        env_file = os.environ.get("env_file", ".env")
        env_prefix = ""
        extra = "allow"
