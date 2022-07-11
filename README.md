# AutoDict
[![Unit Test][unittest-image]][unittest-url] [![Pylint][pylint-image]][pylint-url] [![Coverage][coverage-image]][coverage-url] [![Latest Version][pypi-image]][pypi-url]

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
> python -m pip install autodict
```
For development, install as a link to repository such that code changes are used.
```bash
> python -m pip install -e .
```

----
## Usage
```python
>>> from autodict import AutoDict, JSONAutoDict
>>>
>>> d = AutoDict()
>>> print(d)
{}
>>> d["level0"]["level1"]["level2"]["level3"] = "value"
>>> print(d)
{'level0': {'level1': {'level2': {'level3': 'value'}}}}
>>>
>>> with JSONAutoDict("autodict.json") as j:
...   j["level0"]["level1"]["level2"]["level3"] = "value"
...
>>> print(open("autodict.json").read())
{
  "__type__": "AutoDict",
  "level0": {
    "__type__": "AutoDict",
    "level1": {
      "__type__": "AutoDict",
      "level2": {
        "__type__": "AutoDict",
        "level3": "value"
      }
    }
  }
}
>>> with JSONAutoDict("autodict.json") as j:
...   j["level0"]["key"] = "another value"
...
>>> print(open("autodict.json").read())
{
  "__type__": "AutoDict",
  "level0": {
    "__type__": "AutoDict",
    "level1": {
      "__type__": "AutoDict",
      "level2": {
        "__type__": "AutoDict",
        "level3": "value"
      }
    },
    "key": "another value"
  }
}
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

[pypi-image]: https://img.shields.io/pypi/v/AutoDict.svg
[pypi-url]: https://pypi.python.org/pypi/AutoDict/
[unittest-image]: https://github.com/WattsUp/AutoDict/actions/workflows/test.yml/badge.svg
[unittest-url]: https://github.com/WattsUp/AutoDict/actions/workflows/test.yml
[pylint-image]: https://github.com/WattsUp/AutoDict/actions/workflows/lint.yml/badge.svg
[pylint-url]: https://github.com/WattsUp/AutoDict/actions/workflows/lint.yml
[coverage-image]: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/WattsUp/36d9705addcd44fb0fccec1d23dc1338/raw/AutoDict__heads_master.json
[coverage-url]: https://github.com/WattsUp/AutoDict/actions/workflows/coverage.yml
