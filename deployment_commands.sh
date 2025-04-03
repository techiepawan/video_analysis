#apply deployment and services
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# verify running pods
kubectl get pods

#get service info
kubectl get svc fastapi-service

#apply ingress(optional)
kubectl apply -f ingress.yaml

