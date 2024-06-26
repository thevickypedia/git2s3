## Sample Environment Variables

Environment variables can be sourced using any `plaintext` / `JSON` / `YAML` file.

The filepath should be provided as an argument during object instantiation.

Samples values are randomly generated strings from https://pinetools.com/random-string-generator

> _By default, `Git2S3` will look for a `.env` file in the current working directory._<br>
> Refer [samples] directory for examples.

### Examples

- PlainText: [.env]
- JSON: [secrets.json]
- YAML: [secrets.yaml]

[.env]: .env
[secrets.json]: secrets.json
[secrets.yaml]: secrets.yaml

### Usage

- **CLI**
```shell
git2s3 start --env "/path/to/env/file"
```

- **IDE**
```python
import git2s3
backup = git2s3.Git2S3(env_file='/path/to/env/file')
backup.start()
```
