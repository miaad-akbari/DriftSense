.PHONY: install lint test demo

install:
	python -m venv .venv && . .venv/bin/activate && pip install -e .

lint:
	@echo "Lint step placeholder (add ruff or flake8 later)"

test:
	PYTHONPATH=src python -m unittest discover -s tests

demo:
	driftsense scan sample_manifests/desired sample_manifests/actual --format text --fail-on-drift || true
