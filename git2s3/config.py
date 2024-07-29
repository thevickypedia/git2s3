import pathlib
import sys
import time
from typing import List, Optional

from pydantic import BaseModel, DirectoryPath, HttpUrl, field_validator
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


class SourceControl(StrEnum):
    """Available source control options to clone.

    >>> SourceControl

    """

    all: str = "all"
    gist: str = "gist"
    repo: str = "repo"
    wiki: str = "wiki"


class DataStore(BaseModel):
    """DataStore model to store repository/gist information.

    >>> DataStore

    """

    source: SourceControl
    clone_url: HttpUrl
    name: str
    description: Optional[str] = None
    private: bool


class Boto3RetryMode(StrEnum):
    """Retry mode for boto3 client.

    >>> Boto3RetryMode

    """

    legacy: str = "legacy"
    standard: str = "standard"
    adaptive: str = "adaptive"


# noinspection PyMethodParameters
class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic``.

    >>> EnvConfig

    """

    git_api_url: HttpUrl = "https://api.github.com/"
    git_owner: str
    git_token: str
    git_ignore: List[str] = []

    source: SourceControl | List[SourceControl] = SourceControl.all
    log: LogOptions = LogOptions.stdout
    debug: bool = False
    local_store: bool = False

    aws_profile_name: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region_name: str | None = None
    aws_bucket_name: str
    aws_s3_prefix: str = f"github_{int(time.time())}"
    boto3_retry_attempts: int = 10
    boto3_retry_mode: Boto3RetryMode = Boto3RetryMode.standard

    @classmethod
    def from_env_file(cls, filename: pathlib.Path) -> "EnvConfig":
        """Create an instance of EnvConfig from environment file.

        Args:
            filename: Name of the env file.

        See Also:
            - Loading environment variables from files are an additional feature.
            - Both the system's and session's env vars are processed by default.

        Returns:
            EnvConfig:
            Loads the ``EnvConfig`` model.
        """
        return cls(_env_file=filename)

    @field_validator("source", mode="after", check_fields=True)
    def parse_source(cls, value: SourceControl | List[SourceControl]) -> DirectoryPath:
        """Validate and parse 'source' to remove 'all' from the source option."""
        if isinstance(value, list):
            if value == [SourceControl.all] or SourceControl.all in value:
                return [SourceControl.repo, SourceControl.gist, SourceControl.wiki]
            if SourceControl.repo not in value:
                raise ValueError(
                    f"{value!r} must contain {SourceControl.repo.value!r} as a source type"
                )
            return value
        if value == SourceControl.all:
            return [SourceControl.repo, SourceControl.gist, SourceControl.wiki]
        value = [value]
        if SourceControl.repo in value:
            return value
        raise ValueError(f"Must contain {SourceControl.repo.value!r} as a source type")

    @field_validator("git_api_url", mode="after", check_fields=True)
    def parse_git_api_url(cls, value: HttpUrl) -> str:
        """Parse git_api_url stripping the ``/`` at the end."""
        return str(value).rstrip("/")

    @field_validator("git_ignore", mode="after", check_fields=True)
    def parse_git_ignore(cls, value: List[str]) -> List[str]:
        """Convert all git_ignore values to lowercase."""
        return [v.lower() for v in value]

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "allow"
        hide_input_in_errors = True
