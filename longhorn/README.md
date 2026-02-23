## setup
```shell
modprobe dm-crypt
echo dm_crypt | sudo tee /etc/modules-load.d/dm_crypt.conf
pacman -S cryptsetup nfs-utils open-iscsi
systemctl enable iscsid
systemctl start iscsid

helm repo add longhorn https://charts.longhorn.io
helm repo update
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace
```