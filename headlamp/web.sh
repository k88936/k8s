kubectl create token headlamp --namespace headlamp
echo "https://localhost:8081"
kubectl port-forward -n headlamp service/headlamp 8081:80
