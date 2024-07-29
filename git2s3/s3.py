import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from git2s3 import config, exc


class Uploader:
    # noinspection PyUnresolvedReferences
    """Concurrent uploader object to upload files to S3.

    >>> Uploader

    Keyword Args:
        env: Environment configuration.
        logger: Logger object.
    """

    def __init__(self, env: config.EnvConfig, logger: logging.Logger):
        """Concurrent uploader object to upload files to S3.

        References:
            - https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
            - https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
        """
        session = boto3.Session(
            aws_access_key_id=env.aws_access_key_id,
            aws_secret_access_key=env.aws_secret_access_key,
            region_name=env.aws_region_name,
            profile_name=env.aws_profile_name,
        )
        self.logger = logger
        self.bucket = env.aws_bucket_name
        self.prefix = env.aws_s3_prefix
        self.base_path = os.path.join(os.getcwd(), env.git_owner)
        self.s3_client = session.client(
            "s3",
            config=Config(
                retries=dict(
                    max_attempts=env.boto3_retry_attempts, mode=env.boto3_retry_mode
                )
            ),
        )

    def upload_file(
        self, local_file_path: str | os.PathLike, s3_file_path: str | os.PathLike
    ) -> None:
        """Uploads an object to S3.

        Args:
            local_file_path: Local file path to upload from.
            s3_file_path: S3 file path to upload to.
        """
        try:
            self.s3_client.upload_file(local_file_path, self.bucket, s3_file_path)
            self.logger.info("Uploaded '%s' to 's3://%s'", s3_file_path, self.bucket)
        except (FileNotFoundError, BotoCoreError, ClientError) as error:
            raise exc.UploadError(error)

    def trigger(self) -> bool:
        """Trigger to upload all file objects concurrently to S3.

        Returns:
            bool:
            Returns a boolean flag to indicate completion status.
        """
        futures = {}
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, self.base_path)
                    s3_file_path = os.path.join(self.prefix, relative_path)
                    future = executor.submit(
                        self.upload_file, local_file_path, s3_file_path
                    )
                    futures[future] = s3_file_path
        exception = False
        for future in as_completed(futures):
            if future.exception():
                exception = True
                self.logger.error(
                    "Thread processing '%s' received an exception: %s",
                    futures[future],
                    future.exception(),
                )
        return exception
