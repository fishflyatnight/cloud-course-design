# 报告材料索引

本文件只索引真实材料，不是课程设计报告。

| 任务点 | 证据位置 |
|---|---|
| Docker Compose 三服务与后端日志 | `../01_local_compose/report-docker-compose-validation.png` |
| SWR 镜像列表总览 | `02_swr_push/swr-console-image-list.png` |
| CCE 两个 Worker 与版本 | `01_cce_connection/cce-public-connection-success.txt` |
| Metrics Server CPU/内存 | `01_cce_connection/metrics-server-success.txt` |
| SWR 镜像推送 | `02_swr_push/push-*.log` |
| CCE 服务端 YAML 校验 | `03_cce_deploy/server-dry-run.txt` |
| CCE Pod、Service、PVC、HPA 基线 | `03_cce_deploy/first-running-baseline.txt` |
| SWR 镜像 digest 与节点分布 | `03_cce_deploy/image-runtime-proof.txt` |
| Flask 启动与 `/api/ping` 日志 | `03_cce_deploy/backend-startup.log` |
| CCE Frontend 首页截图 | `03_cce_deploy/cce-frontend-home.png` |
| ELB `/api/ping` 截图 | `03_cce_deploy/cce-elb-api-ping.png` |
| Redis 持久化三步截图 | `04_redis_configmap_hpa/report-redis-1-set.png`、`report-redis-2-delete-pod.png`、`report-redis-3-get-after-rebuild.png` |
| ConfigMap Volume | `04_redis_configmap_hpa/report-configmap-volume.png` |
| HPA 扩容 | `04_redis_configmap_hpa/hpa-cloud-scale-up-ready.txt`、`report-hpa-scale-up.png` |
| HPA 缩容 | `04_redis_configmap_hpa/report-hpa-scale-down-complete.png` |
| Spark Operator | `05_spark/operator-status.txt`、`operator-controller.log` |
| WordCount 2 Executor 运行/完成 | `05_spark/report-wordcount-driver-executors-running.png`、`report-wordcount-completed.png` |
| Douban 清洗 | `05_spark/report-cleaning-schema.png`、`report-cleaning-statistics.png` |
| Spark SQL 1 executor | `05_spark/report-query-1-genre.png` 至 `report-query-5-join.png` |
| Spark SQL 2 executors | `05_spark/douban-2executor-driver.log` |
| 性能对比 | `05_spark/performance-comparison.png`、`performance-analysis-facts.txt` |
| Spark 状态截图 | `05_spark/report-spark-status.png` |

截图必须保留完整命令、资源状态和时间，且不得出现 Token、KubeConfig、私钥或 Secret 明文。
