#!/usr/bin/env bash
set -euo pipefail

echo "http://localhost:9001/rustfs/console/"
kubectl -n storage-0 port-forward svc/tenant-0-console 9001:9001
