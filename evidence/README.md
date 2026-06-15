# 本地预验证证据

本目录中的文件均来自 2026-06-15 的真实本地运行，但不代表华为云部署完成。

- `01_local_compose/`：Docker Compose、页面、API 和 Redis 联调。
- `02_local_spark/`：本地 Spark 清洗、SQL、Pandas 和耗时。
- `03_minikube/`：本地 Kubernetes 的 PVC、Redis 持久化、ConfigMap 和 HPA。
- `04_spark_operator/`：离线 Helm Chart、Spark Operator 和 WordCount SparkApplication。

正式验收应另外保存 CCE、SWR、OBS、ELB 和云端 Spark 的真实证据。本目录不得存放 AK、SK、Token、私钥、KubeConfig 或 Redis 明文密码。
