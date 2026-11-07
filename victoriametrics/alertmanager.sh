#!/usr/bin/env bash
set -euo pipefail

namespace="victoriametrics"
service="$(kubectl -n "$namespace" get service -o name | grep -m1 alertmanager | cut -d/ -f2)"

echo "http://localhost:9093"
kubectl -n "$namespace" port-forward "service/$service" 9093:9093
