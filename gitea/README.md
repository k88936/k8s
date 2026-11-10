```bash
helm repo add gitea-charts https://dl.gitea.com/charts/
helm repo update
helm upgrade --install gitea gitea-charts/gitea \
  --version 12.7.0 \
  --namespace gitea \
```

```bash
kubectl -n gitea exec deploy/gitea -c gitea -- \
  gitea admin user create --admin --username admin \
  --password '<new-password>' --email admin@k88936.top \
  --must-change-password=false
```
