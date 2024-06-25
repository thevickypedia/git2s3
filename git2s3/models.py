import os
import sys

from pydantic import DirectoryPath, field_validator, HttpUrl
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

    """

    git_api_url: HttpUrl = "https://api.github.com"
    git_owner: str | None = None
    git_token: str | None = None
    clone_dir: DirectoryPath = os.path.join(os.getcwd(), "backup")

    debug: bool = False
    log: LogOptions = LogOptions.stdout

    aws_profile_name: str | None = None
    aws_access_key: str | None = None
    aws_secret_key: str | None = None
    aws_region_name: str | None = None
    aws_bucket_name: str | None = None

    @field_validator("clone_dir", mode="before", check_fields=True)
    def parse_clone_dir(cls, value: str) -> DirectoryPath:
        """Validate clone_dir to check if it is potential path."""
        if os.path.isdir(value):
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
