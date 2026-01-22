# secrect
```shell
kubectl create secret generic rustfs-credentials \
  --namespace=rustfs \
  --from-literal=accessKey=rustfsadmin \
  --from-literal=secretKey=rustfsadmin
```