# Operational Triton Tests

This directory contains unit tests for the Operational Triton project.

## Running Tests

To run the tests, you need `pytest` installed.

```bash
pip install pytest
```

Run the tests from the project root directory:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/
```

## Test Structure

- `conftest.py`: Contains fixtures and mocks for external dependencies (GDAL, pygrib, pyslurm). This allows tests to run on environments where these libraries are not installed (e.g., generic Linux, macOS).
- `test_*.py`: Unit tests for corresponding modules in `src/`.

## Environment Support

The tests are designed to be environment-agnostic. Heavy dependencies are mocked, so you can run these tests on:
- macOS
- Generic Linux
- HPC Systems (without needing the full software stack loaded)
