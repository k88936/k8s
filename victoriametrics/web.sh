#!/usr/bin/env bash
set -euo pipefail

namespace="victoriametrics"
service="$(kubectl -n "$namespace" get service -l app.kubernetes.io/name=grafana -o jsonpath='{.items[0].metadata.name}')"

echo "http://localhost:3000"
echo "Grafana user: $(kubectl -n "$namespace" get secret grafana-admin -o jsonpath='{.data.admin-user}' | base64 -d)"
echo "Grafana password: $(kubectl -n "$namespace" get secret grafana-admin -o jsonpath='{.data.admin-password}' | base64 -d)"
kubectl -n "$namespace" port-forward "service/$service" 3000:80
