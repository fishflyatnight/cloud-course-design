# 明日命令清单

这些命令只供真实环境中逐项执行，不代表已经成功。

## Docker 与 Compose

```bash
docker compose up --build
docker compose ps
docker compose logs -f backend
docker compose down

docker build --provenance=false -f backend/Dockerfile.backend -t cloud-course-backend:local backend
docker build --provenance=false -f frontend/Dockerfile.frontend -t cloud-course-frontend:local frontend
docker tag cloud-course-backend:local [SWR_IMAGE_BACKEND]
docker push [SWR_IMAGE_BACKEND]
```

## kubectl

```bash
kubectl get nodes -o wide
kubectl get pods -n cloud-course -o wide
kubectl get svc -n cloud-course
kubectl get pvc -n cloud-course
kubectl get hpa -n cloud-course
kubectl top nodes

kubectl apply -f k8s/00-namespace.yaml
kubectl describe pod <pod-name> -n cloud-course
kubectl logs <pod-name> -n cloud-course
kubectl logs -n cloud-course -l app=backend --tail=100
kubectl exec -it <pod-name> -n cloud-course -- sh
kubectl delete pod <pod-name> -n cloud-course
kubectl get events -n cloud-course --sort-by=.lastTimestamp
```

## ConfigMap 与 Redis

```bash
kubectl exec -n cloud-course deploy/frontend -- cat /etc/nginx/conf.d/default.conf
kubectl exec -n cloud-course <redis-pod> -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" SET testkey hello'
kubectl exec -n cloud-course <redis-pod> -- sh -c \
  'redis-cli -a "$REDIS_PASSWORD" GET testkey'
```

## Helm 与 Spark Operator

```bash
helm lint <OFFLINE_RESOURCE_ROOT>/spark/spark-operator/
helm install spark-op <OFFLINE_RESOURCE_ROOT>/spark/spark-operator/ \
  -n spark-operator --create-namespace \
  --set image.registry=swr.[REGION].myhuaweicloud.com \
  --set image.repository=[SWR_ORG]/spark-operator \
  --set image.tag=2.5.0 \
  --set spark.serviceAccount.name=spark
helm list -n spark-operator
kubectl get pods -n spark-operator
```

## SparkApplication

```bash
kubectl apply -f spark/sparkapplication-wordcount.yaml
kubectl apply -f spark/sparkapplication-douban-1executor.yaml
kubectl apply -f spark/sparkapplication-douban-2executor.yaml
kubectl get sparkapplications
kubectl describe sparkapplication spark-wordcount
kubectl get pods -l spark-role=driver
kubectl get pods -l spark-role=executor
kubectl logs <driver-pod>
kubectl delete sparkapplication spark-wordcount
```

## 访问与 HPA

```bash
curl "http://[ELB_IP]/api/ping"
kubectl get hpa,pods -n cloud-course -w
python scripts/07_hpa_pressure_test.py \
  --url "http://[ELB_IP]/api/ping" \
  --requests 10000 \
  --concurrency 200
kubectl describe hpa backend-hpa -n cloud-course
```

