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

pytest tests <-s>
pytest tests/test_models.py
pytest tests/test_price.py::TestPrice::test_main
pytest tests --cov=powerfee --cov-report=html

python3 setup.py test

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
