# Git2S3
Backup GitHub projects to AWS S3

![Python][label-pyversion]

**Platform Supported**

![Platform][label-platform]

**Deployments**

[![pages][label-actions-pages]][gha_pages]
[![pypi][label-actions-pypi]][gha_pypi]
[![markdown][label-actions-markdown]][gha_md_valid]

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

> Use `git2s3 --help` for usage instructions.

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
[![pypi-module][label-pypi-package]][pypi-repo]

[https://pypi.org/project/git2s3/][pypi]

## Runbook
[![made-with-sphinx-doc][label-sphinx-doc]][sphinx]

[https://thevickypedia.github.io/git2s3/][runbook]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[//]: # (Labels)

[label-actions-markdown]: https://github.com/thevickypedia/git2s3/actions/workflows/markdown.yaml/badge.svg
[label-pypi-package]: https://img.shields.io/badge/Pypi%20Package-git2s3-blue?style=for-the-badge&logo=Python
[label-sphinx-doc]: https://img.shields.io/badge/Made%20with-Sphinx-blue?style=for-the-badge&logo=Sphinx
[label-pyversion]: https://img.shields.io/badge/python-3.10%20%7C%203.11-orange
[label-platform]: https://img.shields.io/badge/Platform-Linux|macOS|Windows-1f425f.svg
[label-actions-pages]: https://github.com/thevickypedia/git2s3/actions/workflows/pages/pages-build-deployment/badge.svg
[label-actions-pypi]: https://github.com/thevickypedia/git2s3/actions/workflows/python-publish.yaml/badge.svg
[label-pypi]: https://img.shields.io/pypi/v/git2s3
[label-pypi-format]: https://img.shields.io/pypi/format/git2s3
[label-pypi-status]: https://img.shields.io/pypi/status/git2s3

[3.10]: https://docs.python.org/3/whatsnew/3.10.html
[3.11]: https://docs.python.org/3/whatsnew/3.11.html
[virtual environment]: https://docs.python.org/3/tutorial/venv.html
[release-notes]: https://github.com/thevickypedia/git2s3/blob/master/release_notes.rst
[gha_pages]: https://github.com/thevickypedia/git2s3/actions/workflows/pages/pages-build-deployment
[gha_pypi]: https://github.com/thevickypedia/git2s3/actions/workflows/python-publish.yaml
[gha_md_valid]: https://github.com/thevickypedia/git2s3/actions/workflows/markdown.yaml
[google-docs]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pep8]: https://www.python.org/dev/peps/pep-0008/
[isort]: https://pycqa.github.io/isort/
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[pypi]: https://pypi.org/project/git2s3
[pypi-files]: https://pypi.org/project/git2s3/#files
[pypi-repo]: https://packaging.python.org/tutorials/packaging-projects/
[license]: https://github.com/thevickypedia/git2s3/blob/master/LICENSE
[runbook]: https://thevickypedia.github.io/git2s3/
