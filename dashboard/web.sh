kubectl -n kubernetes-dashboard create token admin-user 
echo "https://localhost:8443"
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443