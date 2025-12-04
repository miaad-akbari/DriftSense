# Contributing to DriftSense

Thanks for taking the time to contribute! Follow these quick steps to keep the history tidy:

1. Fork the repo and create a feature branch.
2. Create a virtual environment and install dependencies with `pip install -e .`.
3. Add tests for any new features and run `PYTHONPATH=src python -m unittest discover -s tests`.
4. Keep commits focused; reference issues in commit messages when applicable.
5. Submit a PR and describe the motivation plus validation steps.

## Commit style

Use concise conventional commits, e.g., `feat: add namespace filter` or `fix: handle missing manifests`. This keeps release notes readable and highlights intent.
