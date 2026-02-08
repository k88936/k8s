# secrect
```shell
kubectl create secret generic nextcloud-s3-secret \
  --namespace=nextcloud \
  --from-literal=OBJECTSTORE_S3_KEY="" \
  --from-literal=OBJECTSTORE_S3_SECRET="" 
```