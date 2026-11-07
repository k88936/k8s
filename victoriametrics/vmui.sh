#!/usr/bin/env bash
set -euo pipefail

namespace="victoriametrics"
service="$(kubectl -n "$namespace" get service -l app.kubernetes.io/name=vmsingle -o jsonpath='{.items[0].metadata.name}')"

echo "http://localhost:8428/vmui"
kubectl -n "$namespace" port-forward "service/$service" 8428:8428
