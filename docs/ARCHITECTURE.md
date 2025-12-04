# DriftSense Architecture

```
GitOps repo (desired)   Cluster snapshot (actual)
          \                 /
           \               /
            \             /
             manifest_loader
                     |
                 diff_engine
           /           |          \
    missing        changed       extra
           \           |          /
            \          |         /
                report formatters
                       |
                    CLI output
```

- **manifest_loader** reads all YAML docs under the provided directories and tags their source paths.
- **diff_engine** indexes manifests by `kind/namespace/name`, strips noisy metadata, and builds a drift report.
- **report** renders the report to Rich-powered text, Markdown, JSON, or future formats.
- **cli** wires the modules together and exposes developer-friendly flags for CI and local demos.
