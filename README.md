# DriftSense

DriftSense is a batteries-included DevOps companion that continuously scans Kubernetes desired state (for example from your GitOps repository) against what is actually running in the cluster and produces human friendly diff reports. It focuses on developer experience: no cluster access is required during development, reports are available as CLI output, Markdown, or JSON, and sane defaults make it easy to plug into CI/CD for drift gates.

> Why now? Platform teams are moving fast toward GitOps while simultaneously operating fleets of ephemeral clusters. Detecting and explaining drift before it turns into an incident is trending hard across DevOps communities, and DriftSense gives you a focused, scriptable tool to do exactly that.

## Features

-  **Deep manifest comparison** – normalizes Kubernetes objects and pinpoints spec-level differences using readable diffs.
-  **Drift policies** – mark kinds to ignore (e.g., `Event`, `Lease`) while auditing critical workloads.
-  **Multiple report modes** – stdout with ANSI colors, Markdown tables for pull requests, or JSON for bots and dashboards.
-  **Sample data & tests** – ship-ready fixtures make it easy to demo or extend the tool.
-  **CI ready** – `--fail-on-drift` lets you fail pipelines if unauthorized changes are detected.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Compare sample manifests
driftsense scan sample_manifests/desired sample_manifests/actual
```

## CLI usage

```bash
driftsense scan <desired_dir> <actual_dir> \
  [--format text|markdown|json] \
  [--ignore-kind KindA --ignore-kind KindB] \
  [--fail-on-drift]
```
## Run Unittest
```
python -m unittest discover -s tests 
```

- `desired_dir` – Checkout of your GitOps repo or Helm template output.
- `actual_dir` – Snapshot collected from the cluster (e.g., `kubectl get all -o yaml` per namespace).

## Sample manifests

The repository contains an example `sample_manifests` folder showing a Deployment scaling drift, a ConfigMap with changed data, and an unexpected Secret. Use it to validate the workflow or for demos/blog posts.

## Project structure

```
.
├── sample_manifests
│   ├── desired
│   └── actual
├── src/driftsense
│   ├── cli.py
│   ├── diff_engine.py
│   ├── manifest_loader.py
│   └── report.py
├── tests
│   └── test_diff_engine.py
└── README.md
```

## Roadmap ideas

1. Integrate live-cluster discovery through `kubectl` or the Kubernetes Python client.
2. Add Prometheus exporter mode for long-running drift guardians.
3. Publish Docker image & GitHub Action for turnkey adoption.
4. Extend drift policies with severity levels and overrides per namespace. 

---

DriftSense is released under the MIT License. Contributions, issues, and feature requests are welcome!
