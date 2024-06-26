import pathlib
import sys
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


class Fields(StrEnum):
    """Available fields to clone.

    >>> Fields

    """

    all: str = "all"
    gist: str = "gist"
    repo: str = "repo"
    wiki: str = "wiki"


class Field(BaseModel):
    """Field model to store repository/gist information.

    >>> Field

    """

    field: Fields
    clone_url: HttpUrl
    name: str
    description: Optional[str] = None
    private: bool


# noinspection PyMethodParameters
class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic``.

    >>> EnvConfig

    """

    git_api_url: HttpUrl = "https://api.github.com/"
    git_owner: str
    git_token: str

    fields: Fields | List[Fields] = Fields.all
    log: LogOptions = LogOptions.stdout
    debug: bool = False

    aws_profile_name: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region_name: str | None = None
    aws_bucket_name: str | None = None

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

    @field_validator("fields", mode="after", check_fields=True)
    def parse_fields(cls, value: Fields | List[Fields]) -> DirectoryPath:
        """Validate and parse 'fields' to remove 'all' from the fields option."""
        if isinstance(value, list):
            if value == [Fields.all] or Fields.all in value:
                return [Fields.repo, Fields.gist, Fields.wiki]
            return value
        if value == Fields.all:
            return [Fields.repo, Fields.gist, Fields.wiki]
        raise ValueError(f"{value!r} is not a valid field type")

    @field_validator("git_api_url", mode="after", check_fields=True)
    def parse_git_api_url(cls, value: HttpUrl) -> str:
        """Parse git_api_url stripping the ``/`` at the end."""
        return str(value).rstrip("/")

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "allow"
        hide_input_in_errors = True
