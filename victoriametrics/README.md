
```shell
kubectl create namespace victoriametrics --dry-run=client -o yaml | kubectl apply -f -
kubectl -n victoriametrics create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$(openssl rand -base64 24)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

安装 VictoriaMetrics：

```shell
helm upgrade --install victoria-metrics \
  oci://ghcr.io/victoriametrics/helm-charts/victoria-metrics-k8s-stack \
  --version 0.97.0 \
  --namespace victoriametrics \
  --create-namespace \
  -f values.yaml
```


## smart

```shell
kubectl apply -f smartctl-exporter.yaml
kubectl apply -f smart-rules.yaml
kubectl apply -f rustfs-operator.yaml
```


```shell
sudo install -m 0644 smartd.conf /etc/smartd.conf
sudo systemctl enable --now smartd
smartd -c /etc/smartd.conf -q showtests
```


## RustFS Tenant

- `OPERATOR_METRICS_ENABLED=true`
- `OPERATOR_TENANT_MONITOR_ENABLED=true`
- `OPERATOR_TENANT_MONITOR_INTERVAL_SECONDS=300`


## web ui


```shell
./web.sh
./vmui.sh
./alertmanager.sh
```
