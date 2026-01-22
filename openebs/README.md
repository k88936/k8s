# setup
```shell
helm install openebs --namespace openebs openebs/openebs --create-namespace \
    --set engines.replicated.mayastor.enabled=false \
    --set engines.local.lvm.enabled=false \
    --set engines.local.zfs.enabled=false 
```