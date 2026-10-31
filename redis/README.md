
## Endpoints

lan
```text
redis://juicefs-redis.redis.svc.cluster.local:6379/0
```

cluster
```text
redis://192.168.31.24:30638/0
```


## Deploy

```shell
kubectl -n redis get secret juicefs-redis-auth >/dev/null 2>&1 || \
  kubectl -n redis create secret generic juicefs-redis-auth \
    --from-file=redis-password=/etc/juicefs/redis-password
```

```shell
helm upgrade --install juicefs-redis oci://registry-1.docker.io/bitnamicharts/redis \
  --namespace redis \
  --version 28.3.10 \
  -f values.yaml \
  --wait \

kubectl apply -f service.yaml
```

## Admin

```shell
kubectl -n redis exec -it juicefs-redis-master-0 -- sh -lc '
  REDISCLI_AUTH="$(cat "$REDIS_PASSWORD_FILE")" \
  exec redis-cli -h 127.0.0.1 -p 6379 -n 0
'
```
