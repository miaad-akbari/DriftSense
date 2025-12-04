# Testing DriftSense

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

PYTHONPATH=src python -m unittest discover -s tests
```

Use `make test` for a shorthand once the virtual environment is active.
