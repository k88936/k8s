# setup
```shell
helm install \
    cert-manager oci://quay.io/jetstack/charts/cert-manager \
    --namespace cert-manager \
    --create-namespace \
    --set crds.enabled=true \
    --set 'extraArgs={--dns01-recursive-nameservers-only,--dns01-recursive-nameservers=8.8.8.8:53\,1.1.1.1:53}'
```

# alidns
```shell
helm upgrade --install alidns-webhook alidns-webhook --repo https://wjiec.github.io/alidns-webhook \
    --namespace cert-manager\
    --set groupName=acme.k88936.top
```

```shell
kubectl create secret generic alidns-secret \
  --namespace=cert-manager \
  --from-literal=access-key-id="YourAccessKeyID" \
  --from-literal=access-key-secret="YourAccessKeySecret"
```

```shell
kubectl apply -f issuer.yaml 
kubectl apply -f cert.yaml
```