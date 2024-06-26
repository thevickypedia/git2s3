class DirectoryExists(ResourceWarning):
    """Warning: Raised when clone directory already exists."""


class UnsupportedSource(UserWarning):
    """Warning: Raised when source is not supported."""


class Git2S3Error(Exception):
    """Exception: Base class for all exceptions."""


class GitHubAPIError(Git2S3Error):
    """Exception: Raised when failed to fetch repositories from source control."""


class InvalidOwner(GitHubAPIError):
    """Exception: Raised when owner is invalid."""


class InvalidSource(GitHubAPIError):
    """Exception: Raised when source is invalid."""


class ArchiveError(Git2S3Error):
    """Exception: Raised when failed to archive repositories."""


class UploadError(Git2S3Error):
    """Exception: Raised when failed to upload file objects to S3."""
