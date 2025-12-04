#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <namespace> <output-dir>" >&2
  exit 1
fi

NAMESPACE="$1"
OUTPUT_DIR="$2"
mkdir -p "$OUTPUT_DIR"

kubectl get all -n "$NAMESPACE" -o yaml >"$OUTPUT_DIR/${NAMESPACE}-resources.yaml"
for kind in deployment configmap secret service; do
  kubectl get "$kind" -n "$NAMESPACE" -o yaml >"$OUTPUT_DIR/${NAMESPACE}-${kind}.yaml" || true
done

echo "Snapshot written to $OUTPUT_DIR"
