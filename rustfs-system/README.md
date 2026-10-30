```shell
helm repo add rustfs-operator https://operator.rustfs.com
helm repo update rustfs-operator

helm upgrade --install rustfs-operator rustfs-operator/rustfs-operator \
  --namespace rustfs-system \
  --create-namespace \
  --version 0.0.8 \
  -f values.yaml
```

