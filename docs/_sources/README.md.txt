# Git2S3
Backup GitHub projects to AWS S3

![Python][label-pyversion]

**Platform Supported**

![Platform][label-platform]

**Deployments**

[![pages][label-actions-pages]][gha_pages]
[![pypi][label-actions-pypi]][gha_pypi]

[![Pypi][label-pypi]][pypi]
[![Pypi-format][label-pypi-format]][pypi-files]
[![Pypi-status][label-pypi-status]][pypi]

## Kick off

**Recommendations**

- Install `python` [3.10] or [3.11]
- Use a dedicated [virtual environment]

**Install Git2S3**
```shell
python -m pip install git2s3
```

**Initiate - IDE**
```python
import git2s3


if __name__ == '__main__':
    git = git2s3.Git2S3()
    git.start()
```

**Initiate - CLI**
```shell
git2s3 start
```

> Use `Git2S3 --help` for usage instructions.

## Coding Standards
Docstring format: [`Google`][google-docs] <br>
Styling conventions: [`PEP 8`][pep8] and [`isort`][isort]

## [Release Notes][release-notes]
**Requirement**
```shell
python -m pip install gitverse
```

**Usage**
```shell
gitverse-release reverse -f release_notes.rst -t 'Release Notes'
```

## Linting
`pre-commit` will ensure linting, run pytest, generate runbook & release notes, and validate hyperlinks in ALL
markdown files (including Wiki pages)

**Requirement**
```shell
python -m pip install sphinx==5.1.1 pre-commit recommonmark
```

**Usage**
```shell
pre-commit run --all-files
```

## Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)][pypi-repo]

[https://pypi.org/project/Git2S3/][pypi]

## Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)][sphinx]

[https://Git2S3-docs.vigneshrao.com/][runbook]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[python]: https://python.org
[3.10]: https://docs.python.org/3/whatsnew/3.10.html
[3.11]: https://docs.python.org/3/whatsnew/3.11.html
[virtual environment]: https://docs.python.org/3/tutorial/venv.html
[PyCharm]: https://www.jetbrains.com/pycharm/
[VSCode]: https://code.visualstudio.com/download
[repo]: https://api.github.com/repos/thevickypedia/Git2S3
[license]: https://github.com/thevickypedia/Git2S3/blob/master/LICENSE
[pypi]: https://pypi.org/project/Git2S3
[pypi-files]: https://pypi.org/project/Git2S3/#files
[pypi-repo]: https://packaging.python.org/tutorials/packaging-projects/
[wiki]: https://github.com/thevickypedia/Git2S3/wiki
[release-notes]: https://github.com/thevickypedia/Git2S3/blob/master/release_notes.rst
[gha_pages]: https://github.com/thevickypedia/git2s3/actions/workflows/pages/pages-build-deployment
[gha_pypi]: https://github.com/thevickypedia/git2s3/actions/workflows/python-publish.yaml
[gha_md_valid]: https://github.com/thevickypedia/Git2S3/actions/workflows/markdown.yml
[gha_cleanup]: https://github.com/thevickypedia/Git2S3/actions/workflows/cleanup.yml
[webpage]: https://vigneshrao.com/
[webpage_contact]: https://vigneshrao.com/contact
[Anaconda]: https://docs.conda.io/projects/conda/en/latest/user-guide/install/
[Miniconda]: https://docs.conda.io/en/latest/miniconda.html#windows-installers
[vcpp]: https://visualstudio.microsoft.com/visual-cpp-build-tools/
[git-cli]: https://git-scm.com/download/win/
[google-docs]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pep8]: https://www.python.org/dev/peps/pep-0008/
[isort]: https://pycqa.github.io/isort/
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[runbook]: https://Git2S3-docs.vigneshrao.com/

<!-- labels -->

[label-python]: https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=Python
[label-pyversion]: https://img.shields.io/badge/python-3.10%20%7C%203.11-orange
[label-platform]: https://img.shields.io/badge/Platform-Linux|macOS|Windows-1f425f.svg

[label-language-ct]: https://img.shields.io/github/languages/count/thevickypedia/Git2S3
[label-code-coverage]: https://img.shields.io/github/languages/top/thevickypedia/Git2S3

[label-license]: https://img.shields.io/github/license/thevickypedia/Git2S3

[label-stars]: https://img.shields.io/github/stars/thevickypedia/Git2S3
[label-forks]: https://img.shields.io/github/forks/thevickypedia/Git2S3
[label-watchers]: https://img.shields.io/github/watchers/thevickypedia/Git2S3

[label-repo-size]: https://img.shields.io/github/repo-size/thevickypedia/Git2S3
[label-code-size]: https://img.shields.io/github/languages/code-size/thevickypedia/Git2S3
[label-code-line]: http://Git2S3.vigneshrao.com/line-count?badge=true
[label-file-count]: http://Git2S3.vigneshrao.com/file-count?badge=true

[label-issues-closed]: https://img.shields.io/github/issues-closed-raw/thevickypedia/Git2S3
[label-issues-raw]: https://img.shields.io/github/issues-raw/thevickypedia/Git2S3
[label-pr-closed]: https://img.shields.io/github/issues-pr-closed-raw/thevickypedia/Git2S3
[label-pr-raw]: https://img.shields.io/github/issues-pr-raw/thevickypedia/Git2S3

[label-file-count]: https://tokei.rs/b1/github/thevickypedia/Git2S3?category=files
[label-line-of-code]: https://tokei.rs/b1/github/thevickypedia/Git2S3?category=code

[label-stats-Modules]: https://img.shields.io/github/search/thevickypedia/Git2S3/module
[label-stats-Python]: https://img.shields.io/github/search/thevickypedia/Git2S3/.py
[label-stats-Threads]: https://img.shields.io/github/search/thevickypedia/Git2S3/thread
[label-stats-Listener]: https://img.shields.io/github/search/thevickypedia/Git2S3/listener
[label-stats-Speaker]: https://img.shields.io/github/search/thevickypedia/Git2S3/speaker
[label-stats-Bash]: https://img.shields.io/github/search/thevickypedia/Git2S3/.sh
[label-stats-AppleScript]: https://img.shields.io/github/search/thevickypedia/Git2S3/.scpt
[label-stats-Make]: https://img.shields.io/github/search/thevickypedia/Git2S3/Makefile

[label-actions-pages]: https://github.com/thevickypedia/git2s3/actions/workflows/pages/pages-build-deployment/badge.svg
[label-actions-pypi]: https://github.com/thevickypedia/git2s3/actions/workflows/python-publish.yaml/badge.svg

[label-pypi]: https://img.shields.io/pypi/v/git2s3
[label-pypi-format]: https://img.shields.io/pypi/format/Git2S3
[label-pypi-status]: https://img.shields.io/pypi/status/Git2S3

[label-github-repo-created]: https://img.shields.io/date/1599432310
[label-github-commit-activity]: https://img.shields.io/github/commit-activity/y/thevickypedia/Git2S3
[label-github-last-commit]: https://img.shields.io/github/last-commit/thevickypedia/Git2S3
[label-github-last-release]: https://img.shields.io/github/release-date/thevickypedia/Git2S3

[label-active-development]: https://img.shields.io/badge/Development%20Level-Actively%20Developed-success.svg
[label-actively-maintained]: https://img.shields.io/badge/Maintenance%20Level-Actively%20Maintained-success.svg
[label-maintainer]: https://img.shields.io/badge/Maintained%20By-Vignesh%20Rao-blue.svg

[label-askme]: https://img.shields.io/badge/SELECT%20*%20FROM-questions-1abc9c.svg
