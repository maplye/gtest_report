# gcov-testreport

## Usage



## Development

### Running locally

Start python3 in the base of repository.

```python
pass
```

### Running tests

```shell
python3 setup.py test

nosetests gtest_report.tests.logic_flow_test:GoParserTest.testSingleIf -s
```

### Running pylint

```shell
pylint gtest_report
```

### Running formatter

```shell
yapf -rip --style=yapf .
```

### Deploying to PyPi

```shell
python3 setup.py sdist
twine upload dist/*
```
