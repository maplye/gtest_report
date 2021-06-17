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

nosetests gtest_report.tests.logic_flow_test:LogicFlowTest.testSingleIf -s

nosetests gtest_report.tests.logic_flow_test:LogicFlowTest --debug=gtest_report.logic_flow
```

show print:
```shell
nosetests gtest_report.tests.logic_flow_test:LogicFlowTest.testSingleIf -s
```

show logging:
```shell
nosetests -l gtest_report.tests.logic_flow_test:LogicFlowTest --debug=[gtest_report.logic_flow]
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
