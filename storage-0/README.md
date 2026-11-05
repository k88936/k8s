```shell
export RUSTFS_ACCESS_KEY=rustfsadmin
read -rsp 'RUSTFS_SECRET_KEY: ' RUSTFS_SECRET_KEY; echo
export RUSTFS_RPC_SECRET="$(openssl rand -base64 32)"

kubectl create secret generic rustfs-tenant-creds \
  --namespace=storage-0 \
  --from-literal=accesskey="$RUSTFS_ACCESS_KEY" \
  --from-literal=secretkey="$RUSTFS_SECRET_KEY" \
  --from-literal=rpc-secret="$RUSTFS_RPC_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Access

- S3 API: `https://storage0.k88936.top` (`tenant-0-io:9000`)
- S3 NodePort: `http://127.0.0.1:30900` (`tenant-0-io-nodeport:9000`, fixed)
