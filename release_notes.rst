Release Notes
=============

v0.1.0 (08/27/2025)
-------------------
- Includes a ``cut_off_days`` threshold to skip repos/gists that weren't updated in the last N days
- Fails if running within a git repo or the destination (``backup_dir``) is a git repo
- Remove setting max per page via CLI
- Includes an optional ``dry_run`` flag to skip S3 upload after enforcing ``local_store``
- Logs more information about cloning status
- Replaced misleading variable names with generics
- Bug fix ``incomplete_upload`` behavior being reversed
- Moves local copy to a dynamically named directory when ``local_store`` is set to ``True``
- Maintains the same default naming convention for both S3 and local store
- Enforces local store when dry run is set to true
- **Full Changelog**: https://github.com/thevickypedia/git2s3/compare/v0.0.5...v0.1.0

v0.0.5 (11/03/2024)
-------------------
- Includes an option to upload to S3 even when cloning partially failed
- Includes detailed logging of success and failed count for clones and uploads
- **Full Changelog**: https://github.com/thevickypedia/git2s3/compare/0.0.4...v0.0.5

v0.0.4 (08/01/2024)
-------------------
- Release ``v0.0.4``
- **Full Changelog**: https://github.com/thevickypedia/git2s3/compare/0.0.3...v0.0.4

v0.0.3 (07/28/2024)
-------------------
- Release ``v0.0.3``
- **Full Changelog**: https://github.com/thevickypedia/git2s3/compare/0.0.2...v0.0.3

0.0.2 (07/28/2024)
------------------
- Create a backup approach for `GitPython`
- Make `aws_bucket_name` mandatory
- Remove empty repositories when cloning wiki fails
- Bump version to 0.0.2

v0.0.1 (06/27/2024)
-------------------
- Release `v0.0.1`
- **Full Changelog**: https://github.com/thevickypedia/git2s3/compare/ba49b99...c83b01c

v0.0.0-b (06/26/2024)
---------------------
- Release beta version

v0.0.0-a (06/25/2024)
---------------------
- Pre-alpha release to pypi
- Includes cloning of all repositories
