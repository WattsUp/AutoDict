# AutoDict
[![Unit Test](https://github.com/WattsUp/AutoDict/actions/workflows/test.yml/badge.svg)](https://github.com/WattsUp/AutoDict/actions/workflows/test.yml) [![Pylint](https://github.com/WattsUp/AutoDict/actions/workflows/lint.yml/badge.svg)](https://github.com/WattsUp/AutoDict/actions/workflows/lint.yml) [![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/WattsUp/36d9705addcd44fb0fccec1d23dc1338/raw/AutoDict__heads_master.json)](https://github.com/WattsUp/AutoDict/actions/workflows/coverage.yml)

Dictionary that automatically adds children dictionaries as necessary. Including a json based serialization and deserialization.

----
## Environment
List of dependencies for package to run.
### Required
* None

### Optional
* None
----
## Installation / Build / Deployment
Install module
```bash
> python -m pip install .
```
For development, install as a link to repository such that code changes are used.
```bash
> python -m pip install -e .
```

----
## Usage
```python
import autodict import AutoDict, JSONAutoDict

d = AutoDict()
d["level0"]["level1"]["level2"]["level3"]["level4"] = "value"
print(d)
## TODO

with JSONAutoDict("autodict.json") as j:
  j["level0"]["level1"]["level2"]["level3"]["level4"] = "value"

with open("autodict.json") as f:
  print(f.read())
  ## TODO

with JSONAutoDict("autodict.json") as j:
  j["level0"]["key"] = "another value"

with open("autodict.json") as f:
  print(f.read())
  ## TODO
```

----
## Running Tests
To run the automated tests, execute `unittest discover`:
```bash
> python -m unittest discover tests -v
```

To run the automated tests with coverage, execute `coverage run`:
```bash
> python -m coverage run
> python -m coverage report
```

----
## Development
Code development of this project adheres to [Google Python Guide](https://google.github.io/styleguide/pyguide.html)

### Styling
Use `yapf` to format files, based on Google's guide with the exception of indents being 2 spaces.

---
## Versioning
Versioning of this projects adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and is implemented using git tags.  
